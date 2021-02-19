-- upgrade --
ALTER TABLE "builds" ADD "commit" VARCHAR(255) NOT NULL;
ALTER TABLE "builds" ADD "branch" VARCHAR(255) NOT NULL;
ALTER TABLE "import_commits" ADD "branch" VARCHAR(255) NOT NULL;
-- downgrade --
ALTER TABLE "builds" DROP COLUMN "commit";
ALTER TABLE "builds" DROP COLUMN "branch";
ALTER TABLE "import_commits" DROP COLUMN "branch";
