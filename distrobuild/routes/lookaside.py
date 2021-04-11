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
import hashlib

from fastapi import APIRouter, Request, File, UploadFile
from pydantic import BaseModel
from tortoise.transactions import atomic

from distrobuild.common import get_user
from distrobuild.models import LookasideBlob
from distrobuild.session import lookaside_session

router = APIRouter(prefix="/lookaside")


class LookasideUploadResponse(BaseModel):
    sha256sum: str


@atomic()
@router.post("/", response_model=LookasideUploadResponse)
async def put_file_in_lookaside(request: Request, file: UploadFile = File(...)):
    user = get_user(request)

    file_content = await file.read()
    await file.seek(0)

    sha256sum = hashlib.sha256(file_content).hexdigest()
    lookaside_session.upload(file.file, sha256sum)

    await LookasideBlob.create(sum=sha256sum, executor_username=user["preferred_username"])

    return LookasideUploadResponse(sha256sum=sha256sum)
