from fastapi import APIRouter

from distrobuild.routes import build, packages, bootstrap

_base_router = APIRouter(prefix="/api")


def register_routes(app):
    _base_router.include_router(packages.router)
    _base_router.include_router(bootstrap.router)
    _base_router.include_router(build.router)

    app.include_router(_base_router)
