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

from tortoise.contrib.pydantic import pydantic_model_creator

from distrobuild import models

Package_Pydantic = pydantic_model_creator(models.Package, name="Package")
PackageGeneral_Pydantic = pydantic_model_creator(models.Package, name="PackageGeneral", exclude=("imports", "builds"))
PackageModule_Pydantic = pydantic_model_creator(models.PackageModule, name="PackageModule")
Build_Pydantic = pydantic_model_creator(models.Build, name="Build", exclude=("import_commit.import_",))
BuildGeneral_Pydantic = pydantic_model_creator(models.Build, name="BuildGeneral",
                                               exclude=("import_commit.import_", "package.imports", "package.builds"))
Import_Pydantic = pydantic_model_creator(models.Import, name="Import", exclude=("commits.builds",))
ImportGeneral_Pydantic = pydantic_model_creator(models.Import, name="ImportGeneral",
                                                exclude=("package.imports", "package.builds"))
BatchImport_Pydantic = pydantic_model_creator(models.BatchImport, name="BatchImport",
                                              exclude=("imports.package.imports", "imports.package.builds"))
BatchBuild_Pydantic = pydantic_model_creator(models.BatchBuild, name="BatchBuild",
                                             exclude=("builds.package.imports", "builds.package.builds"))
