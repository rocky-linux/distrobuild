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

from base64 import b64decode, b64encode

import typing
import secrets

import itsdangerous
import json
import aioredis

from fastapi import FastAPI
from itsdangerous import SignatureExpired, BadTimeSignature
from starlette.datastructures import Secret
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, DispatchFunction
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from distrobuild.settings import settings


class RedisSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app: ASGIApp,
            fapi: FastAPI,
            secret_key: typing.Union[str, Secret],
            session_cookie: str = "session",
            max_age: int = 3000,
            same_site: str = "lax",
            https_only: bool = False,
            dispatch: DispatchFunction = None
    ) -> None:
        super().__init__(app, dispatch)
        self.redis = aioredis.create_redis_pool(settings.redis_url)
        self.redis_inited = False
        self.app = app
        self.signer = itsdangerous.TimestampSigner(str(secret_key))
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.same_site = same_site
        self.https_only = https_only

        @fapi.on_event("shutdown")
        async def shutdown():
            self.redis.close()
            await self.redis.wait_closed()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self.redis_inited:
            self.redis = await self.redis
            self.redis_inited = True

        initial_session_was_empty = True
        redis_key = ""

        if self.session_cookie in request.cookies:
            data = request.cookies[self.session_cookie].encode("utf-8")
            try:
                data = self.signer.unsign(data, max_age=self.max_age)
                redis_key = data
                redis_val = await self.redis.get(data, encoding="utf-8")
                request.scope["session"] = json.loads(b64decode(redis_val))
                initial_session_was_empty = False
            except (BadTimeSignature, SignatureExpired):
                request.scope["session"] = {}
        else:
            request.scope["session"] = {}

        response = await call_next(request)

        if request.scope["session"]:
            redis_val = b64encode(json.dumps(request.scope["session"]).encode("utf-8"))
            if redis_key == "":
                redis_key = secrets.token_hex(32)
            await self.redis.set(redis_key, redis_val)
            await self.redis.expire(redis_key, 3000)
            data = self.signer.sign(redis_key)
            response.set_cookie(self.session_cookie, data.decode("utf-8"), self.max_age, httponly=True,
                                samesite=self.same_site, path="/", secure=self.https_only)
        elif not initial_session_was_empty:
            response.delete_cookie(self.session_cookie, path="/")

        return response
