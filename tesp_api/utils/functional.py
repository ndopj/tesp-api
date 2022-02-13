from typing import TypeVar, Callable

from pymonad.maybe import Just, Nothing, Maybe

T = TypeVar("T")


def maybe_of(value: T) -> Maybe[T]:
    return Just(value) if value else Nothing


def get_else_throw(optional_val: Maybe[T], exception: Exception) -> T:
    ret_val: T = optional_val.maybe(None, lambda x: x)
    if ret_val is None:
        raise exception
    return ret_val


def identity_with_side_effect(value: T, func: Callable[[T], any]):
    func(value)
    return value
