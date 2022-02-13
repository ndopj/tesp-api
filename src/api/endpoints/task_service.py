from typing import List, Optional

from fastapi import APIRouter, Body
from fastapi.params import Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.repository.task_repository import task_repository
from src.model.task import TesTaskView, TesTask, RegisteredTesTask
from src.model.task_service_info import TesServiceInfo, TesServiceType, TesServiceOrganization

router = APIRouter()

descriptions = {
    "tasks-create":  "Create a new task. The user provides a Task document, which the "
                     "server uses as a basis and adds additional fields.",
    "tasks-get":     "Get a single task, based on providing the exact task ID string.",
    "tasks-get-all": "List tasks tracked by the TES server. This includes queued, active"
                     " and completed tasks. How long completed tasks are stored by the"
                     " system may be dependent on the underlying implementation.",
    "tasks-delete":  "Cancel a task based on providing an exact task ID.",
    "service-info":  "Provides information about the service"
                     ", this structure is based on the standardized GA4GH"
                     " service info structure. In addition, this endpoint"
                     " will also provide information about customized storage"
                     " endpoints offered by the TES server."
}

query_descriptions = {
    "name_prefix": "OPTIONAL. Filter the list to include tasks where the name matches"
                   " this prefix. If unspecified, no task name filtering is done.",
    "page_size":   "OPTIONAL. Number of tasks to return in one page. Must be less than"
                   " 2048. Defaults to 256.",
    "page_token":  "OPTIONAL. Page token is used to retrieve the next page of results."
                   " If unspecified, returns the first page of results. See ListTasksResponse.next_page_token",
    "view":        "OPTIONAL. Affects the fields included in the returned Task messages. See TaskView below."
                   " - MINIMAL: Task message will include ONLY the fields: Task.Id Task.State"
                   " - BASIC: Task message will include all fields EXCEPT: Task.ExecutorLog.stdout"
                   " Task.ExecutorLog.stderr Input.content TaskLog.system_logs"
                   " - FULL: Task message includes all fields."
}

qry_var_name_prefix = Query(None, description=query_descriptions['name_prefix'])
qry_var_page_size = Query(256, description=query_descriptions['page_size'])
qry_var_page_token = Query(None, description=query_descriptions['page_token'])
qry_var_view = Query(TesTaskView.MINIMAL, description=query_descriptions['view'])


class TesCreateTaskResponse(BaseModel):
    id: str = Field(..., description='Task identifier assigned by the server.')


class TesGetAllTasksResponse(BaseModel):
    tasks: List[dict] = Field(..., description='List of tasks. These tasks will be based on the original'
                                               ' submitted task document, but with other fields, such as'
                                               ' the job state and logging info, added/changed as the job'
                                               ' progresses.')
    next_page_token: str = Field(None, description='Token used to return the next page of results. This value can be'
                                                   ' used in the page_token field of the next ListTasks request.')


async def view_query_params(view: Optional[TesTaskView] = qry_var_view):
    return {"view": view}


async def list_query_params(name_prefix: Optional[str] = qry_var_name_prefix,
                            page_size: Optional[int] = qry_var_page_size,
                            page_token: Optional[str] = qry_var_page_token,
                            view: dict = Depends(view_query_params)):
    return {
        "name_prefix": name_prefix,
        "page_size": page_size,
        "page_token": page_token,
        **view
    }


def get_view(view: Optional[TesTaskView]) -> dict:
    return {
        TesTaskView.BASIC: {'exclude': {'logs': {'__all__': {'logs': {'__all__': 'stdout'}}}}},
        TesTaskView.MINIMAL: {'include': {'id', 'state'}}
    }.get(view, {'exclude': {}})


@router.post("/tasks",
             responses={200: {"description": "OK"}},
             response_model=TesCreateTaskResponse,
             description=descriptions["tasks-create"])
async def create_task(tes_task: TesTask = Body(...)) -> TesCreateTaskResponse:
    id = await task_repository.create_task(tes_task)
    return TesCreateTaskResponse(id=id)


@router.get("/tasks/{id}",
            responses={
                200: {"description": "Ok"},
                404: {"description": "Not found"}},
            response_model=RegisteredTesTask,
            response_model_by_alias=False,
            description=descriptions["tasks-get"])
async def get_task(id: str, query_params: dict = Depends(view_query_params)) -> Response:
    registered_task = await task_repository.get_task(id)
    return Response(registered_task.json(**get_view(query_params['view'])),
                    status_code=200,
                    media_type='application/json')


@router.get("/tasks",
            responses={200: {"description": "Ok"}},
            response_model=List[RegisteredTesTask],
            response_model_by_alias=False,
            description=descriptions["tasks-get-all"])
async def get_tasks(query_params: dict = Depends(list_query_params)) -> Response:
    tasks = await task_repository.get_tasks()

    def jsonable_dict(task: RegisteredTesTask, exclude: any = None, include: any = None):
        task_dict = task.dict(exclude=exclude, include=include)
        task_dict['id'] = str(task_dict['id'])
        return task_dict

    tasks_under_view = list(map(lambda task: jsonable_dict(task, **get_view(query_params['view'])), tasks))
    return Response(TesGetAllTasksResponse(tasks=tasks_under_view, next_page_token=None).json(),
                    status_code=200,
                    media_type='application/json')


@router.post("/tasks/{id}:cancel",
             responses={200: {"description": "Ok"}},
             description=descriptions["tasks-delete"],)
async def cancel_task(id: str):
    return {"id": id}


@router.get("/service-info",
            responses={200: {"description": "Ok"}},
            description=descriptions["service-info"],
            response_model=TesServiceInfo)
async def get_service_info() -> TesServiceInfo:
    return TesServiceInfo(
        id="fi.muni.cz.tesp",
        name="TESP",
        type=TesServiceType(
            group="org.ga4gh",
            artifact="tes",
            version="0.1.0"
        ),
        description="GA4GH TES Server implementation for Pulsar",
        organisation=TesServiceOrganization(
            name="Faculty of Informatics, Masaryk University",
            url="https://www.fi.muni.cz/"
        ),
        contactUrl="https://www.fi.muni.cz/",
        documentationUrl="https://www.fi.muni.cz/",
        createdAt="2021-10-26T00:00:00Z",
        updatedAt="2021-10-26T00:00:00Z",
        environment="dev",
        version="0.1.0",
        storage=["https://www.fi.muni.cz/"]
    )
