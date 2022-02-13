import asyncio
from enum import Enum
from typing import Union, Optional, Any, Dict

from pydantic.main import BaseModel

from tesp_api.service.event_handler import local_handler


class EventPayloadSchemaRegistry(Dict):

    def register(self, _schema=None, event_name: Union[str, Enum] = None):
        if not event_name:
            raise ValueError("'event_name' must be provided when registering a schema")

        def _wrap(schema):
            if BaseModel and not issubclass(schema, BaseModel):
                raise AssertionError("'schema' must be a subclass of Pydantic BaseModel")
            self[event_name] = schema
            return schema

        return _wrap if _schema is None else _schema


registry = EventPayloadSchemaRegistry()


def _dispatch(event_name: Union[str, Enum], payload: Optional[Any] = None) -> None:
    async def task(): await local_handler.handle((event_name, payload))
    asyncio.create_task(task())


def dispatch_event(event_name: Union[str, Enum],
                   payload: Optional[Any] = None,
                   validate_payload: bool = True) -> None:
    if validate_payload:
        payload_schema_cls = registry.get(event_name)
        if payload_schema_cls:
            payload = payload_schema_cls(**(payload or {})).dict(**{"exclude_unset": True})
    return _dispatch(event_name=event_name, payload=payload)
