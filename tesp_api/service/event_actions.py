import datetime
from typing import List

from pymonad.maybe import Just
from bson.objectid import ObjectId
from pymonad.promise import Promise

from tesp_api.utils.docker import docker_run_command
from tesp_api.service.pulsar_service import pulsar_service
from tesp_api.service.event_dispatcher import dispatch_event
from tesp_api.utils.functional import get_else_throw, maybe_of
from tesp_api.service.event_handler import Event, local_handler
from tesp_api.repository.task_repository import task_repository
from tesp_api.service.file_transfer_service import file_transfer_service
from tesp_api.service.error import pulsar_event_handle_error, TaskNotFoundError, TaskExecutorError
from tesp_api.service.pulsar_operations import PulsarRestOperations, PulsarAmpqOperations, DataType
from tesp_api.repository.model.task import TesTaskState, TesTaskExecutor, TesTaskInput, TesTaskOutput
from tesp_api.repository.task_repository_utils import append_task_executor_logs, update_last_task_log_time


@local_handler.register(event_name="queued_task")
def handle_queued_task(event: Event) -> None:
    event_name, payload = event
    match pulsar_service.get_operations():
        case PulsarRestOperations() as pulsar_rest_operations:
            dispatch_event('queued_task_rest', {**payload, 'pulsar_operations': pulsar_rest_operations})
        case PulsarAmpqOperations() as pulsar_ampq_operations:
            dispatch_event('queued_task_ampq', {**payload, 'pulsar_operations': pulsar_ampq_operations})


@local_handler.register(event_name="queued_task_rest")
async def handle_queued_task_rest(event: Event):
    event_name, payload = event
    task_id: ObjectId = payload['task_id']
    pulsar_operations: PulsarRestOperations = payload['pulsar_operations']
    await Promise(lambda resolve, reject: resolve(None))\
        .then(lambda nothing: pulsar_operations.setup_job(task_id))\
        .map(lambda setup_job_result: dispatch_event('initialize_task', {**payload, 'task_config': setup_job_result}))\
        .catch(lambda error: pulsar_event_handle_error(error, payload['task_id'], event_name, pulsar_operations))\
        .then(lambda x: x)  # invokes promise returned by error handler, otherwise acts as identity function


@local_handler.register(event_name="initialize_task")
async def handle_initializing_task(event: Event) -> None:
    event_name, payload = event
    task_id: ObjectId = payload['task_id']
    pulsar_operations: PulsarRestOperations = payload['pulsar_operations']

    async def setup_data(job_id: ObjectId, inputs: List[TesTaskInput], outputs: List[TesTaskOutput]):
        input_confs: List[dict] = []
        output_confs: List[dict] = []
        for i in range(0, len(inputs)):
            content = inputs[i].content
            if content is None and inputs[i].url is not None:
                content = await file_transfer_service.ftp_download_file(inputs[i].url)
            pulsar_path = await pulsar_operations.upload(
                job_id, DataType.INPUT, file_content=Just(content),
                file_path=maybe_of(inputs[i].url).maybe(f'input_file_{i}', lambda x: x.path))
            input_confs.append({'container_path': inputs[i].path, 'pulsar_path': pulsar_path})
        for i in range(0, len(outputs)):
            pulsar_path = await pulsar_operations.upload(
                job_id, DataType.OUTPUT, file_path=maybe_of(outputs[i].url.path).maybe("", lambda x: x))
            output_confs.append({
                'container_path': outputs[i].path, 'pulsar_path': pulsar_path, 'url': outputs[i].url})
        return input_confs, output_confs

    await Promise(lambda resolve, reject: resolve(None))\
        .then(lambda nothing: task_repository.update_task(
            {'_id': task_id, "state": TesTaskState.QUEUED},
            {'$set': {'state': TesTaskState.INITIALIZING}}
        )).map(lambda updated_task: get_else_throw(
            updated_task, TaskNotFoundError(task_id, Just(TesTaskState.QUEUED))
        )).then(lambda updated_task: setup_data(
            task_id, maybe_of(updated_task.inputs).maybe([], lambda x: x),
            maybe_of(updated_task.outputs).maybe([], lambda x: x)
        )).map(lambda input_output_confs: dispatch_event('run_task', {
            **payload,
            'input_confs': input_output_confs[0],
            'output_confs': input_output_confs[1]
        })).catch(lambda error: pulsar_event_handle_error(error, task_id, event_name, pulsar_operations))\
        .then(lambda x: x)  # invokes promise returned by error handler, otherwise acts as identity function


@local_handler.register(event_name="run_task")
async def handle_run_task(event: Event) -> None:
    event_name, payload = event
    task_id: ObjectId = payload['task_id']
    input_confs: List[dict] = payload['input_confs']
    output_confs: List[dict] = payload['output_confs']
    pulsar_operations: PulsarRestOperations = payload['pulsar_operations']

    async def execute_task(executors: List[TesTaskExecutor]):
        await update_last_task_log_time(
            task_id, TesTaskState.RUNNING,
            start_time=Just(datetime.datetime.now(datetime.timezone.utc)))
        for executor in executors:
            run_command = docker_run_command(executor, input_confs, output_confs)
            command_start_time = datetime.datetime.now(datetime.timezone.utc)
            command_status = await pulsar_operations.run_job(task_id, run_command)
            command_end_time = datetime.datetime.now(datetime.timezone.utc)
            await append_task_executor_logs(
                task_id, TesTaskState.RUNNING, command_start_time, command_end_time, command_status['stdout'],
                command_status['stderr'], command_status['returncode'])
            if command_status['returncode'] != 0:
                raise TaskExecutorError()

    await Promise(lambda resolve, reject: resolve(None))\
        .then(lambda nothing: task_repository.update_task(
            {'_id': task_id, "state": TesTaskState.INITIALIZING},
            {'$set': {'state': TesTaskState.RUNNING}}
        )).map(lambda task: get_else_throw(
            task, TaskNotFoundError(task_id, Just(TesTaskState.INITIALIZING))
        )).then(lambda task: execute_task(task.executors)) \
        .map(lambda nothing: dispatch_event('finalize_task', payload)) \
        .catch(lambda error: pulsar_event_handle_error(error, task_id, event_name, pulsar_operations)) \
        .then(lambda x: x)  # invokes promise returned by error handler, otherwise acts as identity function


@local_handler.register(event_name='finalize_task')
async def handle_finalize_task(event: Event) -> None:
    event_name, payload = event
    task_id: ObjectId = payload['task_id']
    output_confs: List[dict] = payload['output_confs']
    pulsar_outputs_dir_path: str = payload['task_config']['outputs_directory']
    pulsar_operations: PulsarRestOperations = payload['pulsar_operations']

    async def transfer_files(files_to_transfer):
        for file_to_transfer in files_to_transfer:
            file_content: bytes = await pulsar_operations.download_output(task_id, file_to_transfer['file'])
            await file_transfer_service.ftp_upload_file(file_to_transfer['url'], file_content)

    await Promise(lambda resolve, reject: resolve(None))\
        .map(lambda nothing: [
            {'file': output_conf['pulsar_path'].removeprefix(f'{pulsar_outputs_dir_path}/'),
             'url': output_conf['url']}
            for output_conf in output_confs]
        ).then(lambda files_to_transfer: transfer_files(files_to_transfer))\
        .then(lambda ignored: task_repository.update_task(
            {'_id': task_id, "state": TesTaskState.RUNNING},
            {'$set': {'state': TesTaskState.COMPLETE}}
        )).map(lambda task: get_else_throw(
            task, TaskNotFoundError(task_id, Just(TesTaskState.RUNNING))
        )).then(lambda ignored: pulsar_operations.erase_job(task_id))\
        .catch(lambda error: pulsar_event_handle_error(error, task_id, event_name, pulsar_operations)) \
        .then(lambda x: x)  # invokes promise returned by error handler, otherwise acts as identity function
