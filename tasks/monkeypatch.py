"""
Helper module to monkeypatch PyInvoke's default behaviors.

If run as a module, will take input to update the default search root.
"""

import re

from inspect import ArgSpec, getfullargspec
from pathlib import Path
from unittest.mock import patch

import invoke


def fix_annotations():
    """
    Pyinvoke doesnt accept annotations by default, this fix that
    Based on: https://github.com/pyinvoke/invoke/pull/606
    """

    def patched_inspect_getargspec(func):
        spec = getfullargspec(func)
        return ArgSpec(*spec[0:4])

    org_task_argspec = invoke.tasks.Task.argspec

    def patched_task_argspec(*args, **kwargs):
        with patch(target="inspect.getargspec", new=patched_inspect_getargspec):
            return org_task_argspec(*args, **kwargs)

    invoke.tasks.Task.argspec = patched_task_argspec


def fix_search_root(new_root: str) -> None:
    """
    Patch PyInvoke search root to allow non-root tasks.py

    NOTE: requires config.py file is within the project root
    """
    try:
        invoke_config = next(Path().rglob("invoke/config.py"))
    except StopIteration:
        print(
            "Error locating the PyInvoke config.py module. "
            "Ensure packages are installed within the project root."
        )
        return

    with open(invoke_config, "r+") as f:
        source = f.read()
        f.seek(0)
        f.truncate()
        patched = re.sub('"search_root":.*?,', f'"search_root": "{new_root}",', source)
        f.write(patched)


if __name__ == "__main__":
    new_root = input("Enter new search root directory ( ex: ./tasks ): ").strip()
    fix_search_root(new_root)
