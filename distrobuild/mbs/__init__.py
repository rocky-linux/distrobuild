from dataclasses import dataclass

import httpx

from distrobuild.settings import settings


class MBSConflictException(BaseException):
    pass


class MBSBuildNotFound(BaseException):
    pass


@dataclass
class MBSClient:
    mbs_url: str

    async def get_build(self, mbs_id: int):
        client = httpx.AsyncClient()
        async with client:
            r = await client.get(f"{self.mbs_url}/1/module-builds/{mbs_id}")

            if r.status_code == 404:
                raise MBSBuildNotFound()

            return r.json()

    async def build(self, token: str, name: str, branch: str, commit: str) -> int:
        client = httpx.AsyncClient()
        async with client:
            r = await client.post(
                f"{self.mbs_url}/1/module-builds/",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                json={
                    "scmurl": f"https://{settings.gitlab_host}{settings.repo_prefix}/modules/{name}?#{commit}",
                    "branch": branch,
                }
            )

            if r.status_code == 409:
                raise MBSConflictException()

            data = r.json()
            return data["id"]
