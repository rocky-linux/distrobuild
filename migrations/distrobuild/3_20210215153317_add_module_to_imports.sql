-- upgrade --
ALTER TABLE "imports" ADD "module" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "imports" DROP COLUMN "module";
