from invoke import Collection

from tasks import monkeypatch, tasks  # noqa


namespace = Collection()
namespace.add_task(tasks.developer_up)
namespace.add_task(tasks.developer_down)
namespace.add_task(tasks.developer_build)
namespace.add_task(tasks.hooks)
namespace.add_task(tasks.hooks_run)
namespace.add_task(tasks.hooks_install)
