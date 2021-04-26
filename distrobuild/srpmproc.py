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
import json

from typing import Optional

from distrobuild.settings import settings


async def import_project(import_id: int, source_rpm: str, module_mode: bool = False,
                         single_tag: Optional[str] = None, original: bool = False) -> dict:
    upstream_prefix = f"ssh://{settings.ssh_user}@{settings.gitlab_host}:{settings.ssh_port}{settings.repo_prefix}"

    prefix_no_trailing = settings.repo_prefix
    if prefix_no_trailing.endswith("/"):
        prefix_no_trailing = prefix_no_trailing[:-1]

    upstream_prefix_https = f"{settings.gitlab_host}{prefix_no_trailing}"

    args = [
        "--version",
        str(settings.version),
        "--source-rpm",
        source_rpm,
        "--upstream-prefix",
        upstream_prefix,
        "--upstream-prefix-https",
        upstream_prefix_https,
        "--storage-addr",
        settings.storage_addr,
        "--ssh-user",
        settings.ssh_user,
    ]

    if settings.ssh_key_location:
        args.append("--ssh-key-location")
        args.append(settings.ssh_key_location)

    if settings.no_storage_download:
        args.append("--no-storage-download")

    if settings.no_storage_upload:
        args.append("--no-storage-upload")

    if module_mode:
        args.append("--module-mode")

    if single_tag:
        args.append("--single-tag")
        args.append(single_tag)

    if original:
        args.append("--import-branch-prefix")
        args.append(settings.original_import_branch_prefix)
        args.append("--rpm-prefix")
        args.append(settings.original_rpm_prefix)
        args.append("--module-prefix")
        args.append(settings.original_module_prefix)

    f = open(f"{settings.import_logs_dir}/import-{import_id}.log", "w")

    proc = await asyncio.create_subprocess_exec("srpmproc", *args, stdout=asyncio.subprocess.PIPE, stderr=f)

    last_line = ""
    while True:
        line = (await proc.stdout.readline()).decode("utf-8")
        f.write(line)

        if proc.stdout.at_eof():
            break

        last_line = line

    await proc.wait()
    f.close()

    if proc.returncode != 0:
        raise Exception("srpmproc failed")
    else:
        return json.loads(last_line.strip())
