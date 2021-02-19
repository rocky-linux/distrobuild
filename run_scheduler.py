import asyncio

from tortoise import Tortoise

from distrobuild_scheduler.main import main

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main(loop))
    finally:
        loop.run_until_complete(Tortoise.close_connections())
    loop.close()
