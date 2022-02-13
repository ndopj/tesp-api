import inspect
import fnmatch
from enum import Enum
from typing import Any, Tuple, Union

Event = Tuple[Union[str, Enum], Any]


class LocalHandler:

    def __init__(self):
        self._registry = {}

    def register(self, _func=None, event_name="*"):
        def _wrap(func):
            self._register_handler(event_name, func)
            return func
        return _wrap if _func is None else _wrap(func=_func)

    async def handle(self, event: Event) -> None:
        for handler in self._get_handlers_for_event(event_name=event[0]):
            (await handler(event)) if inspect.iscoroutinefunction(handler) else handler(event)

    def _register_handler(self, event_name: any, func):
        if not isinstance(event_name, str):
            event_name = str(event_name)
        if event_name not in self._registry:
            self._registry[event_name] = []
        self._registry[event_name].append(func)

    def _get_handlers_for_event(self, event_name: any):
        if not isinstance(event_name, str):
            event_name = str(event_name)
        # TODO consider adding a cache
        handlers = []
        for event_name_pattern, registered_handlers in self._registry.items():
            if fnmatch.fnmatch(event_name, event_name_pattern):
                handlers.extend(registered_handlers)
        return handlers


local_handler = LocalHandler()
