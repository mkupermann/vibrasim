.PHONY: db-migrate db-migrate-planA-mark-implemented db-migrate-planA5-mark-implemented

DB_HOST ?= localhost
DB_PORT ?= 5433
DB_USER ?= vibrasim
DB_NAME ?= vibrasim

db-migrate:
	@echo "Applying migrations 0001-0003 in order..."
	@for f in db/migrations/0001*.sql db/migrations/0002*.sql db/migrations/0003*.sql; do \
	  echo ">> $$f"; \
	  PGPASSWORD=vibrasim psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) -f "$$f"; \
	done
	@echo "done."

db-migrate-planA-mark-implemented:
	@if [ -z "$(MERGE_SHA)" ]; then echo "MERGE_SHA= required"; exit 1; fi
	PGPASSWORD=vibrasim psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) \
	  -v merge_sha="'$(MERGE_SHA)'" -f db/migrations/0004_mark_planA_implemented.sql

db-migrate-planA5-mark-implemented:
	@if [ -z "$(MERGE_SHA)" ]; then echo "MERGE_SHA= required"; exit 1; fi
	PGPASSWORD=vibrasim psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) \
	  -v merge_sha="'$(MERGE_SHA)'" -f db/migrations/0005_planA5_perf_amendment.sql
