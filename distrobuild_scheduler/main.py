import asyncio
import json

from tortoise import Tortoise

from distrobuild_scheduler.sigul import check_sigul_key

Tortoise.init_models(["distrobuild.models"], "distrobuild")

from distrobuild.settings import TORTOISE_ORM, settings

from distrobuild.session import message_cipher

# noinspection PyUnresolvedReferences
from distrobuild_scheduler import init_channel, build_package, import_package, logger, periodic_tasks


async def consume_messages(i: int):
    from distrobuild_scheduler import channel

    queue = await channel.declare_queue(settings.routing_key, auto_delete=False)
    async with queue.iterator() as queue_iter:
        logger.info(f"[*] Waiting for messages (worker {i})")
        async for message in queue_iter:
            async with message.process():
                body = json.loads(message.body.decode())
                msg = body.get("message")

                if msg == "import_package":
                    await import_package.task(body["package_id"], body["import_id"], body["dependents"])
                elif msg == "build_package":
                    token = body.get("token")
                    if token:
                        token = message_cipher.decrypt(token.encode()).decode()
                    await build_package.task(body["package_id"], body["build_id"], token)
                else:
                    logger.error("[*] Received unknown message")


def schedule_periodic_tasks():
    asyncio.create_task(periodic_tasks.check_build_status())


async def main(loop):
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await init_channel(loop)

        if not settings.disable_sigul:
            await check_sigul_key()

        schedule_periodic_tasks()

        tasks = [consume_messages(i) for i in range(0, settings.workers)]
        await asyncio.wait(tasks)
    finally:
        from distrobuild_scheduler import connection
        logger.info("[*] Shutting down")
        await connection.close()
