from invoke import Context, task

from tasks.console import console


@task(aliases=("dev", "up"))
def developer_up(c: Context, prod: bool = False, build: bool = False) -> None:
    console.print(f"{' DEV STARTUP ':~^75}", style="green")
    console.print(f"{prod=} {build=}", style="yellow")
    console.print(f"{'':~^75}", style="green")

    compose = "-f ./docker/docker-compose.yml"
    debugpy = "-f ./docker/docker-compose.debugpy.yml"

    match prod, build:
        case True, True:
            c.run(f"docker-compose {compose} --build")
        case True, False:
            c.run(f"docker-compose {compose} up -d")
        case False, True:
            # run with debugpy waiting to connect to debugger
            c.run(f"docker-compose {compose} {debugpy} up -d --build")
        case False, False:
            c.run(f"docker-compose {compose} {debugpy} up -d")


@task(aliases=("down",))
def developer_down(c: Context) -> None:
    console.print(f"{' DEV SHUTDOWN ':~^75}", style="green")
    c.run("docker-compose -f ./docker/docker-compose.yml down --remove-orphans")


@task(aliases=("build",))
def developer_build(c: Context) -> None:
    console.print(f"{' DEV BUILD ':~^75}", style="green")
    c.run("docker compose -f ./docker/docker-compose.yml build")


@task(aliases=("hi",))
def hooks_install(c: Context) -> None:
    console.print("Installing hooks...", style="bold green")
    c.run("pre-commit install")


@task(aliases=("hr",))
def hooks_run(c: Context) -> None:
    console.print("Running hooks...", style="bold green")
    c.run("pre-commit run --all-files")


@task(hooks_install, hooks_run, aliases=("h",))
def hooks(c: Context) -> None:
    # pylint: disable=unused-argument
    pass
