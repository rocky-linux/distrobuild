/*
 * Copyright (c) 2021 The Distrobuild Authors
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

-- upgrade --
CREATE TABLE IF NOT EXISTS "packages" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "name" VARCHAR(255) NOT NULL,
    "responsible_username" VARCHAR(255) NOT NULL,
    "is_module" BOOL NOT NULL  DEFAULT False,
    "is_package" BOOL NOT NULL  DEFAULT False,
    "part_of_module" BOOL NOT NULL  DEFAULT False,
    "last_import" TIMESTAMPTZ,
    "last_build" TIMESTAMPTZ,
    "el8" BOOL NOT NULL  DEFAULT False,
    "el9" BOOL NOT NULL  DEFAULT False,
    "repo" VARCHAR(17)
);
COMMENT ON COLUMN "packages"."repo" IS 'BASEOS: BASEOS\nAPPSTREAM: APPSTREAM\nPOWERTOOLS: POWERTOOLS\nEXTERNAL: EXTERNAL\nMODULAR_CANDIDATE: MODULAR_CANDIDATE\nORIGINAL: ORIGINAL\nINFRA: INFRA';;
CREATE TABLE IF NOT EXISTS "package_modules" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "package_id" BIGINT NOT NULL REFERENCES "packages" ("id") ON DELETE RESTRICT,
    "module_parent_package_id" BIGINT NOT NULL REFERENCES "packages" ("id") ON DELETE RESTRICT
);;
-- downgrade --
DROP TABLE IF EXISTS "package_modules";
DROP TABLE IF EXISTS "packages";
