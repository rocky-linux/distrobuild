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
