import io

import monkeypatch

from invoke import Context, task
from rich import print

monkeypatch.fix_annotations()


GREEN = "[bold green]{message}[/bold green]"


@task(aliases=["hi"])
def hooks_install(c: Context) -> None:
    print(GREEN.format(message="Installing hooks..."))
    c.run("poetry run pre-commit install")


@task(aliases=["hr"])
def hooks_run(c: Context) -> None:
    print(GREEN.format(message="Running hooks..."))
    c.run("poetry run pre-commit run --all-files")


@task(hooks_install, hooks_run, aliases=["h"])
def hooks(c: Context) -> None:
    pass


@task(aliases=["bl"])
def black(c: Context) -> None:
    print(GREEN.format(message="Running black..."))
    output = io.StringIO()
    c.run(
        command="poetry run black . --diff",
        out_stream=output,
        err_stream=output,
        encoding="utf-8",
    )
    print(output.getvalue(), flush=True)
    if "file would be reformatted" not in output.getvalue():
        return
    y_or_n = input("Apply changes? [y/n]: ").strip()
    if y_or_n.lower() == "y":
        c.run(
            command="poetry run black .",
            out_stream=output,
            err_stream=output,
            encoding="utf-8",
        )
        print(output.getvalue())
