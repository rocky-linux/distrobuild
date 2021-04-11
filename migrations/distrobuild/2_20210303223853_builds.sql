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
CREATE TABLE IF NOT EXISTS "imports"
(
    "id"                BIGSERIAL    NOT NULL PRIMARY KEY,
    "created_at"        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at"        TIMESTAMPTZ,
    "status"            VARCHAR(11)  NOT NULL,
    "module"            BOOL         NOT NULL DEFAULT False,
    "version"           INT          NOT NULL,
    "executor_username" VARCHAR(255) NOT NULL,
    "package_id"        BIGINT       NOT NULL REFERENCES "packages" ("id") ON DELETE RESTRICT
);
COMMENT ON COLUMN "imports"."status" IS 'QUEUED: QUEUED\nIN_PROGRESS: IN_PROGRESS\nFAILED: FAILED\nSUCCEEDED: SUCCEEDED\nCANCELLED: CANCELLED';;
CREATE TABLE IF NOT EXISTS "import_commits"
(
    "id"         BIGSERIAL    NOT NULL PRIMARY KEY,
    "commit"     VARCHAR(255) NOT NULL,
    "branch"     VARCHAR(255) NOT NULL,
    "import__id" BIGINT       NOT NULL REFERENCES "imports" ("id") ON DELETE RESTRICT
);;
CREATE TABLE IF NOT EXISTS "builds"
(
    "id"                BIGSERIAL    NOT NULL PRIMARY KEY,
    "created_at"        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at"        TIMESTAMPTZ,
    "status"            VARCHAR(9)   NOT NULL,
    "mbs"               BOOL         NOT NULL DEFAULT False,
    "koji_id"           BIGINT,
    "mbs_id"            BIGINT,
    "executor_username" VARCHAR(255) NOT NULL,
    "force_tag"         VARCHAR(255),
    "exclude_compose"   BOOL         NOT NULL DEFAULT False,
    "point_release"     VARCHAR(255) NOT NULL,
    "import_commit_id"        BIGINT       NOT NULL REFERENCES "import_commits" ("id") ON DELETE RESTRICT,
    "package_id"        BIGINT       NOT NULL REFERENCES "packages" ("id") ON DELETE RESTRICT
);
COMMENT ON COLUMN "builds"."status" IS 'QUEUED: QUEUED\nBUILDING: BUILDING\nFAILED: FAILED\nSUCCEEDED: SUCCEEDED\nCANCELLED: CANCELLED';;
-- downgrade --
DROP TABLE IF EXISTS "builds";
DROP TABLE IF EXISTS "import_commits";
DROP TABLE IF EXISTS "imports";
