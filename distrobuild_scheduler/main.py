import asyncio
import json

from tortoise import Tortoise

Tortoise.init_models(["distrobuild.models"], "distrobuild")

from distrobuild.settings import TORTOISE_ORM, settings

# preload koji session
# noinspection PyUnresolvedReferences
import distrobuild.session

# noinspection PyUnresolvedReferences
from distrobuild_scheduler import init_channel, build_package, import_package, logger, periodic_tasks


async def consume_messages(i: int):
    from distrobuild_scheduler import channel

    queue = await channel.declare_queue(settings.routing_key, auto_delete=False)
    async with queue.iterator() as queue_iter:
        logger.info("[*] Waiting for messages (worker {})".format(i))
        async for message in queue_iter:
            async with message.process():
                body = json.loads(message.body.decode())

                if body["message"] == "import_package":
                    await import_package.task(body["package_id"], body["import_id"], body["dependents"])
                elif body["message"] == "build_package":
                    await build_package.task(body["package_id"], body["build_id"])
                else:
                    logger.error("[*] Received unknown message")


async def schedule_periodic_tasks():
    asyncio.create_task(periodic_tasks.check_build_status())


async def main(loop):
    await Tortoise.init(config=TORTOISE_ORM)
    await init_channel(loop)

    await schedule_periodic_tasks()

    tasks = [consume_messages(i) for i in range(0, settings.workers)]
    await asyncio.wait(tasks)

    from distrobuild_scheduler import connection
    logger.info("[*] Shutting down")
    await connection.close()
