#  Copyright (c) 2021 The Distrobuild Authors
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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

if settings.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


async def init_channel(loop) -> None:
    global channel
    global connection
    connection = await aio_pika.connect_robust(settings.broker_url, loop=loop)
    logger.info("[*] Connected to amqp")
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


async def build_package_task(package_id: int, build_id: int, token: Optional[str]):
    msg_body = {
        "message": "build_package",
        "package_id": package_id,
        "build_id": build_id,
        "token": token,
    }
    encoded = json.dumps(msg_body).encode()

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=encoded,
        ),
        routing_key=settings.routing_key,
    )


async def merge_scratch_task(build_id: int):
    msg_body = {
        "message": "merge_scratch",
        "build_id": build_id,
    }
    encoded = json.dumps(msg_body).encode()

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=encoded,
        ),
        routing_key=settings.routing_key,
    )
