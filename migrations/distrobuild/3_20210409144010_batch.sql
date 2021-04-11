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
CREATE TABLE IF NOT EXISTS "batch_imports"
(
    "id"         BIGSERIAL   NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "batch_import_packages"
(
    "id"              BIGSERIAL NOT NULL PRIMARY KEY,
    "import_id"       BIGINT    NOT NULL REFERENCES "imports" ("id") ON DELETE RESTRICT,
    "batch_import_id" BIGINT    NOT NULL REFERENCES "batch_imports" ("id") ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS "batch_builds"
(
    "id"         BIGSERIAL   NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "batch_build_packages"
(
    "id"             BIGSERIAL NOT NULL PRIMARY KEY,
    "build_id"       BIGINT    NOT NULL REFERENCES "builds" ("id") ON DELETE RESTRICT,
    "batch_build_id" BIGINT    NOT NULL REFERENCES "batch_builds" ("id") ON DELETE RESTRICT
);
-- downgrade --
DROP TABLE IF EXISTS "batch_import_packages";
DROP TABLE IF EXISTS "batches_imports";
DROP TABLE IF EXISTS "batch_build_packages";
DROP TABLE IF EXISTS "batches_builds";
