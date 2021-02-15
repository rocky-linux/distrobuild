import asyncio

from distrobuild.settings import settings

async def import_project(import_id: int, source_rpm: str):
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

    f = open(f"/tmp/import-{import_id}.log", "w")
    proc = await asyncio.create_subprocess_exec("srpmproc", *args, stdout=f, stderr=f)
    await proc.wait()
    f.close()
    if proc.returncode != 0:
        raise Exception("srpmproc failed")
