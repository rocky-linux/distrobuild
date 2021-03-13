import asyncio

from typing import List

from distrobuild.settings import settings
from distrobuild_scheduler import logger


class SigulException(Exception):
    pass


async def run_sigul(args: List[str]):
    args.insert(0, "-c")
    args.insert(1, settings.sigul_config_file)
    args.insert(2, "--batch")

    proc = await asyncio.create_subprocess_exec("sigul",
                                                *args,
                                                stdin=asyncio.subprocess.PIPE,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    proc.stdin.write(f"{settings.sigul_passphrase}\0".encode())
    await proc.wait()

    logger.debug('sigul returned with code: %s', proc.returncode)
    if proc.returncode != 0:
        err = (await proc.stderr.read()).decode()
        # means that the package is already signed.
        # stupid error
        if "ERROR: I/O error: EOFError()" not in err:
            raise SigulException(err)

    return await proc.communicate()


async def check_sigul_key():
    await run_sigul(["get-public-key", settings.sigul_key_name])


async def sign_koji_package(nvr_arch: str):
    await run_sigul([
        "sign-rpm",
        "--koji-only",
        "--store-in-koji",
        "--v3-signature",
        settings.sigul_key_name,
        nvr_arch
    ])
