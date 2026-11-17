# Terminal Log — Haven Infrastructure Assessment

This document summarizes the key commands and observed results. It is not a raw terminal transcript.

## Environment

- Ubuntu 24.04.5 LTS
- Terraform v1.17.2
- Python 3.12.3
- pytest 9.2.0
- Git 2.43.0

## B0 — Terraform resource identity

The original count-based configuration was tested by removing a middle landlord account.

Observed original plan:
Plan: 4 to add, 0 to change, 3 to destroy

After migrating to for_each with stable landlord account IDs and moved blocks:
Plan: 2 to add, 0 to change, 0 to destroy

When testing removal of la-002 after the migration, only its keyed bucket was destroyed:
Plan: 2 to add, 0 to change, 1 to destroy

The original landlord account list was restored.

## B1 — Storage lifecycle

Terraform formatting, validation and planning were run after updating the lifecycle configuration.

Observed plan:
Plan: 2 to add, 0 to change, 0 to destroy

The lifecycle rule uses a sold-listing tag filter and S3 Intelligent-Tiering.

## B2 — Python implementation

Commands executed:

- python3 -m venv .venv
- source .venv/bin/activate
- python -m pip install -r requirements.txt
- python -m pytest -v

Observed result:
12 passed

The tests cover landlord-scoped screening report access, fail-closed authorization, duplicate records, Terraform plan tag validation, idempotency, multiple resource types, ignored actions and missing plan files.

The plan validator was executed against fixtures/plan.json.

Expected non-compliant resources:
- aws_lambda_function.mls_feed_sync
- aws_s3_bucket.listing_media

The validator returned exit code 1 because these two resources lack the required non-empty landlord_account_id tag.

## Safety checks

- No terraform apply was executed.
- app/seed_data.py was not modified.
- app/models.py was not modified.
- fixtures/plan.json was not modified.
- terraform/terraform.tfstate was not modified.
