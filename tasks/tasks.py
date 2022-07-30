import io

from pathlib import Path

from invoke import Context, task

from tasks import monkeypatch
from tasks.console import Text, console


monkeypatch.fix_annotations()


@task(aliases=["dev", "up"])
def developer_up(c: Context, all: bool = False) -> None:
    console.print(f"{' DEV STARTUP ':~^75}", style="green")
    project_root = Path().absolute()
    c.run("docker compose -f ./docker/docker-compose.yml build sieve db browserless")
    if all:
        c.run("docker-compose -f ./docker/docker-compose.yml --profile primary up -d")
    else:
        # default: run app as individual container with debugpy waiting to connect to debugger
        c.run("docker-compose -f ./docker/docker-compose.yml --profile support up -d")
        c.run(
            "docker run "
            "--tty "
            "--detach "
            "--name sieve "
            "--publish 5678:5678 "
            "--network=sieve "
            "--restart unless-stopped "
            f'--mount type=bind,source="{project_root}",target=/sieve '
            "--env-file=.env "
            '--entrypoint="" '
            "sieve:dev "
            '"sh" "-c" "pip install debugpy -t /tmp && python /tmp/debugpy --wait-for-client --listen 0.0.0.0:5678 -m sieve.__main__"'
        )


@task(aliases=["down"])
def developer_down(c: Context) -> None:
    console.print(f"{' DEV SHUTDOWN ':~^75}", style="green")
    c.run("docker-compose -f ./docker/docker-compose.yml down --remove-orphans")


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
