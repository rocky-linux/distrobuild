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
