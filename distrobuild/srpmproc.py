import asyncio
import json

from distrobuild.settings import settings


async def import_project(import_id: int, source_rpm: str, module_mode: bool = False) -> dict:
    upstream_prefix = f"ssh://{settings.ssh_user}@{settings.gitlab_host}:{settings.ssh_port}{settings.repo_prefix}"

    args = [
        "--version",
        str(settings.version),
        "--source-rpm",
        source_rpm,
        "--upstream-prefix",
        upstream_prefix,
        "--storage-addr",
        settings.storage_addr,
        "--ssh-user",
        settings.ssh_user
    ]

    if settings.ssh_key_location:
        args.append("--ssh-key-location")
        args.append(settings.ssh_key_location)

    if module_mode:
        args.append("--module-mode")

    f = open(f"/tmp/import-{import_id}.log", "w")
    proc = await asyncio.create_subprocess_exec("srpmproc", *args, stdout=asyncio.subprocess.PIPE, stderr=f)

    last_line = ""
    while True:
        line = (await proc.stdout.readline()).decode('utf-8')
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
