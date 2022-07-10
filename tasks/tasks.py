import monkeypatch

from invoke import Context, task
from rich import print

monkeypatch.fix_annotations()


BG = "[bold green]{message}[/bold green]"


@task(aliases=["hi"])
def hooks_install(c: Context) -> None:
    print(BG.format(message="Installing hooks..."))
    c.run("poetry run pre-commit install")


@task(aliases=["hr"])
def hooks_run(c: Context) -> None:
    print(BG.format(message="Running hooks..."))
    c.run("poetry run pre-commit run --all-files")


@task(hooks_install, hooks_run, aliases=["h"])
def hooks(c: Context) -> None:
    pass


@task(aliases=["bl"])
def black(c: Context) -> None:
    print(BG.format(message="Running black..."))
    result = c.run("poetry run black . --diff")
    if "file would be reformatted" not in result.stdout + result.stderr:
        return
    y_or_n = input("Apply changes? [y/n]: ").strip()
    if y_or_n.lower() == "y":
        c.run("poetry run black .")
