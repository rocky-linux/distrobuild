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

    if proc.returncode != 0:
        err = (await proc.stderr.read()).decode()
        # means that the package is already signed.
        # stupid error
        if "ERROR: I/O error: EOFError()" not in err:
            logger.debug('sigul returned with code: %s', proc.returncode)
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
