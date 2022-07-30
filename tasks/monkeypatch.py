"""Helper module to monkeypatch PyInvoke's default behaviors"""

from inspect import ArgSpec, getfullargspec
from unittest.mock import patch

import invoke


# https://github.com/pyinvoke/invoke/issues/357#issuecomment-583851322
def fix_annotations():
    """Patch PyInvoke to allow for type annotations"""

    def patched_inspect_getargspec(func):
        spec = getfullargspec(func)
        return ArgSpec(*spec[0:4])

    org_task_argspec = invoke.tasks.Task.argspec

    def patched_task_argspec(*args, **kwargs):
        with patch(target="inspect.getargspec", new=patched_inspect_getargspec):
            return org_task_argspec(*args, **kwargs)

    invoke.tasks.Task.argspec = patched_task_argspec


fix_annotations()
