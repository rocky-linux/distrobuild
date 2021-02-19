-- upgrade --
ALTER TABLE "imports" DROP COLUMN "commit";
CREATE TABLE IF NOT EXISTS "import_commits" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "commit" VARCHAR(255) NOT NULL,
    "import__id" BIGINT NOT NULL REFERENCES "imports" ("id") ON DELETE CASCADE
);;
-- downgrade --
ALTER TABLE "imports" ADD "commit" VARCHAR(255);
DROP TABLE IF EXISTS "import_commits";
