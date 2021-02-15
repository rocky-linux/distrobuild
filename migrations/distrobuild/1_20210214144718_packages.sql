-- upgrade --
CREATE TABLE IF NOT EXISTS "packages" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "name" VARCHAR(255) NOT NULL,
    "responsible_user_id" VARCHAR(255),
    "is_module" BOOL NOT NULL  DEFAULT False,
    "is_package" BOOL NOT NULL  DEFAULT False,
    "part_of_module" BOOL NOT NULL  DEFAULT False,
    "latest_dist_commit" TEXT,
    "el8" BOOL NOT NULL  DEFAULT False,
    "repo" VARCHAR(10)
);
COMMENT ON COLUMN "packages"."repo" IS 'BASEOS: BASEOS\nAPPSTREAM: APPSTREAM\nPOWERTOOLS: POWERTOOLS';;
CREATE TABLE IF NOT EXISTS "packagemodule" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "package_id" BIGINT NOT NULL REFERENCES "packages" ("id") ON DELETE RESTRICT,
    "module_parent_package_id" BIGINT NOT NULL REFERENCES "packages" ("id") ON DELETE RESTRICT
);;
-- downgrade --
DROP TABLE IF EXISTS "packages";
DROP TABLE IF EXISTS "packagemodule";
