from fastapi import APIRouter

from distrobuild.routes import builds, imports, packages, bootstrap

_base_router = APIRouter(prefix="/api")


def register_routes(app):
    _base_router.include_router(packages.router)
    _base_router.include_router(bootstrap.router)
    _base_router.include_router(builds.router)
    _base_router.include_router(imports.router)

    app.include_router(_base_router)
