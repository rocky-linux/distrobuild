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

from enum import Enum
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError
from google.cloud import storage


class LookasideUploadException(Exception):
    pass


class LookasideBackend(str, Enum):
    FILE = "file"
    S3 = "s3"
    GCS = "gcs"


class Lookaside:
    backend: LookasideBackend

    def __init__(self, url: str):
        if url.startswith("file://"):
            self.backend = LookasideBackend.FILE
            self.dir = url.removeprefix("file://")
        elif url.startswith("s3://"):
            self.backend = LookasideBackend.S3
            self.s3 = boto3.client("s3")
            self.bucket = url.removeprefix("s3://")
        elif url.startswith("gs://"):
            self.backend = LookasideBackend.GCS
            self.gcs = storage.Client().bucket(url.removeprefix("gs://"))

    def upload(self, f: BinaryIO, name: str):
        if self.backend == LookasideBackend.FILE:
            file_content = f.read()
            with open(f"{self.dir}/{name}", "wb") as f2:
                f2.write(file_content)
        elif self.backend == LookasideBackend.S3:
            try:
                self.s3.upload_fileobj(f, self.bucket, name)
            except ClientError as e:
                raise LookasideUploadException(e)
        elif self.backend == LookasideBackend.GCS:
            blob = self.gcs.blob(name)
            blob.upload_from_file(f)
