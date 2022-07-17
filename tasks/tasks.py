import io

from invoke import Context, task

from tasks import monkeypatch
from tasks.console import Text, console


monkeypatch.fix_annotations()


@task(aliases=["du"])
def docker_up(c: Context) -> None:
    # TODO: add cross platform path handling
    console.log(f"{' DEV STARTUP ':~^50}", style="green")
    compose_file = "-f .\docker\docker-compose.yml"
    c.run(f"docker-compose {compose_file} up -d --build")


@task(aliases=["dd"])
def docker_down(c: Context) -> None:
    # TODO: add cross platform path handling
    console.log(f"{'DEV SHUTDOWN':~^50}", style="red")
    compose_file = "-f .\docker\docker-compose.yml"
    c.run(f"docker-compose {compose_file} down")


@task(aliases=["hi"])
def hooks_install(c: Context) -> None:
    console.print("Installing hooks...", style="bold green")
    c.run("pre-commit install")


@task(aliases=["hr"])
def hooks_run(c: Context) -> None:
    console.print("Running hooks...", style="bold green")
    c.run("pre-commit run --all-files")


@task(hooks_install, hooks_run, aliases=["h"])
def hooks(c: Context) -> None:
    pass


@task(aliases=["bl"])
def black(c: Context) -> None:
    console.print("Running black...", style="bold green")
    output = io.StringIO()
    c.run(
        command="black . --diff",
        out_stream=output,
        err_stream=output,
        encoding="utf-8",
    )
    console.print(output.getvalue())
    if "file would be reformatted" not in output.getvalue():
        return
    text = Text.assemble(Text("Apply changes? ", style="#EEE8AA"), Text("[y/n]: ", style="#D8BFD8"))
    should_apply = console.input(text).lower().strip() == "y"
    if should_apply:
        output = io.StringIO()
        c.run(
            command="black .",
            out_stream=output,
            err_stream=output,
            encoding="utf-8",
        )
        console.print(output.getvalue())
