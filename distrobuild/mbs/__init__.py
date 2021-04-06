#  Copyright (c) 2021 Distrobuild authors
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
        scmurl = f"https://{settings.gitlab_host}{settings.repo_prefix}/modules/{name}?#{commit}"
        print(scmurl)

        client = httpx.AsyncClient()
        async with client:
            r = await client.post(
                f"{self.mbs_url}/1/module-builds/",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                json={
                    "scmurl": scmurl,
                    "branch": branch,
                }
            )

            if r.status_code == 409:
                raise MBSConflictException()

            data = r.json()
            print(data)
            return data["id"]
