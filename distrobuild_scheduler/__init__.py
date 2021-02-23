import json
import logging

from typing import Tuple, Optional, List

import aio_pika

from distrobuild.settings import settings
from distrobuild_scheduler import import_package

# singleton
connection: Optional[aio_pika.RobustConnection] = None
channel: Optional[aio_pika.Channel] = None
logger = logging.getLogger("distrobuild_scheduler")
logging.basicConfig()
logger.setLevel(logging.INFO)


async def init_channel(loop) -> None:
    global channel
    global connection
    connection = await aio_pika.connect_robust(settings.broker_url, loop=loop)
    logger.info("[*] Connected to {}".format(settings.broker_url))
    channel = await connection.channel()


async def import_package_task(package_id: int, import_id: int, dependents: List[Tuple[int, int]]):
    msg_body = {
        "message": "import_package",
        "package_id": package_id,
        "import_id": import_id,
        "dependents": dependents,
    }
    encoded = json.dumps(msg_body).encode()

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=encoded,
        ),
        routing_key=settings.routing_key,
    )


async def build_package_task(package_id: int, build_id: int):
    msg_body = {
        "message": "build_package",
        "package_id": package_id,
        "build_id": build_id,
    }
    encoded = json.dumps(msg_body).encode()

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=encoded,
        ),
        routing_key=settings.routing_key,
    )
