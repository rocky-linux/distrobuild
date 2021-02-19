from tortoise.contrib.pydantic import pydantic_model_creator

from distrobuild import models

Package_Pydantic = pydantic_model_creator(models.Package, name="Package")
PackageModule_Pydantic = pydantic_model_creator(models.PackageModule, name="PackageModule")
Build_Pydantic = pydantic_model_creator(models.Build, name="Build")
Import_Pydantic = pydantic_model_creator(models.Import, name="Import")
