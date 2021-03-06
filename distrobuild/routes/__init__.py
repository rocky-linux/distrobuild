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

from fastapi import APIRouter

from distrobuild.routes import builds, imports, packages, bootstrap, oidc, batches, lookaside

_base_router = APIRouter(prefix="/api")


def register_routes(app):
    _base_router.include_router(oidc.router)
    _base_router.include_router(packages.router)
    _base_router.include_router(bootstrap.router)
    _base_router.include_router(builds.router)
    _base_router.include_router(imports.router)
    _base_router.include_router(batches.router)
    _base_router.include_router(lookaside.router)

    app.include_router(_base_router)
