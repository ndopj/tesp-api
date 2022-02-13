import aiohttp
from loguru import logger
from socket import AF_INET

from tesp_api.config.properties import properties
from tesp_api.service.pulsar_operations import PulsarRestOperations, PulsarOperations


# aiohttp tracing feature allows to log each request
async def on_request_start(session, context, params):
    logger.debug(f'Sending request to pulsar <{params}>')


class PulsarService:

    def __init__(self):
        timeout = aiohttp.ClientTimeout(total=2)
        connector = aiohttp.TCPConnector(family=AF_INET, limit_per_host=100)
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        self.pulsar_client = aiohttp.ClientSession(timeout=timeout, connector=connector, trace_configs=[trace_config])

    def get_operations(self) -> PulsarOperations:
        return PulsarRestOperations(
            self.pulsar_client,
            properties.pulsar.url,
            properties.pulsar.status.poll_interval,
            properties.pulsar.status.max_polls)


pulsar_service = PulsarService()
