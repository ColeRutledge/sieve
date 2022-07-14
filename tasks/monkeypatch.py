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


# def fix_search_root(new_root: str) -> None:
#     """
#     Patch PyInvoke search root to allow non-root tasks.py

#     NOTE: `VENV_PATH` environment variable must be set or the virtual environment
#     must exist inside the root of the project
#     """
#     search_root = Path(new_root)
#     if not Path(new_root).exists():
#         console.print(
#             "Error validating new root path. Please ensure the directory exists.",
#             style="bold red",
#         )
#         raise SystemExit

#     # prioritize the environment variable and fallback to the .venv dir in the root
#     venv_root = os.environ.get("VENV_PATH") or ".venv"
#     try:
#         invoke_config = next(Path(venv_root).rglob("site-packages/invoke/config.py"))
#     except StopIteration:
#         console.print(
#             "Error locating the PyInvoke config.py module. Ensure the 'VENV_PATH' "
#             "environment variable is set OR that the virtual environment is inside "
#             "the root of the project.",
#             style="bold red",
#         )
#         raise SystemExit

#     text = Text.assemble(
#         Text("Patching the config.py located here: ", style="#4682B4"),
#         Text(str(invoke_config.resolve()), style="#FFFFFF"),
#     )
#     console.print(text)
#     text = Text.assemble(
#         Text("New search root will point here: ", style="#4682B4"),
#         Text(str(search_root.absolute()), style="#FFFFFF"),
#     )
#     console.print(text)

#     text = Text.assemble(
#         Text("Confirm ", style="#EEE8AA"),
#         Text("[y/n]: ", style="#D8BFD8"),
#     )
#     confirmed = console.input(text).lower().strip() == "y"
#     if confirmed:
#         source = open(invoke_config).read()
#         with open(invoke_config, "w+") as f:
#             patched = re.sub('"search_root":.*?,', f'"search_root": "{new_root}",', source)
#             f.write(patched)
#         console.print(Text("Successfully patched!", style="bold green"))


# if __name__ == "__main__":
#     # TODO: ensure we dont receive prompt during CI. default to ./tasks
#     # plan is to call fix_search_root("./tasks") during CI
#     text = Text.assemble(
#         Text("Enter new search root relative to the project root ", style="#4682B4"),
#         Text("(eg: ./tasks, tasks, ./scripts/tasks): ", style="#FFFFFF"),
#     )
#     new_root = console.input(text).strip()
#     fix_search_root(new_root)
