"""Patch PyInvoke to allow for type annotations"""
# https://github.com/pyinvoke/invoke/issues/357#issuecomment-583851322

from collections.abc import Callable
from inspect import ArgSpec, getfullargspec
from unittest.mock import patch

import invoke


def patched_inspect_getargspec(func: Callable[..., ArgSpec]) -> ArgSpec:
    args, varargs, varkw, defaults = getfullargspec(func)[:4]
    return ArgSpec(args, varargs, varkw, defaults or tuple())


class Task(invoke.tasks.Task):
    def argspec(self, body: Callable[..., ArgSpec]) -> tuple[list[str], dict[str, str]]:
        with patch(target="inspect.getargspec", new=patched_inspect_getargspec):
            argspec: tuple[list[str], dict[str, str]] = super().argspec(body)
            return argspec


setattr(invoke.tasks, "Task", Task)
