# Design Notes

## B2 — idempotency key

The cost-tag validator uses the Terraform resource `address` as its deduplication key. For example, `aws_s3_bucket.listing_media` identifies one resource in a plan.

Non-compliant addresses are stored in a Python set, so duplicate entries for the same address are reported only once.

The validator checks only resources with planned actions exactly equal to `["create"]` or `["update"]`. It verifies that `landlord_account_id` exists as a non-empty string in the resulting resource tags.

Output is deterministic because the same plan produces the same checks, duplicate addresses are removed by the set, addresses are sorted before printing, and the exit code depends on whether any non-compliant addresses exist.

This provides idempotency without storing state between executions. Running the script twice against an unchanged plan produces identical output and exit code.

## B2 — screening report access boundary

The authorization boundary is `landlord_account_id`, because a landlord account is the billing and ownership boundary in the supplied domain model.

The function resolves the report's tenant and then the tenant's property. It permits access only when the property's landlord account matches the property manager's landlord account.

The function fails closed when the tenant or property is missing or ambiguous, or when the manager does not have a matching non-empty landlord account ID.

This avoids using tenant or property identifiers as substitutes for landlord-level authorization.

## B0 — stable Terraform resource identity

The original `count` implementation identified landlord buckets by list index. Removing a middle element shifted indexes and caused Terraform to propose unintended replacements and destruction.

The implementation uses `for_each` with landlord account IDs as keys. Explicit `moved` blocks map the four existing count-based state addresses to their new keyed addresses.

This preserves the existing resources during migration. Removing one landlord account after migration affects only that account's bucket.

The migration blocks cover the four existing seeded resources. Any additional legacy count-based addresses in another state must be mapped and verified before migration.

## B1 — storage lifecycle and deletion requirements

Glacier Flexible Retrieval has a 90-day minimum storage duration. Deleting an object after only 10 days in that class can incur a prorated charge for the remaining 80 days.

The redesign uses S3 Intelligent-Tiering for sold listing photos. It avoids the Glacier Flexible Retrieval minimum-duration penalty and supports automatic access-tier optimization. Optional asynchronous Archive Access and Deep Archive Access tiers are excluded because the workload has a seller deletion requirement.

The lifecycle rule filters for objects tagged `listing_status=sold`. The application must apply this tag when a listing is sold. The lifecycle transition's 30-day clock is measured from object creation, not from the time the tag is applied.

The application, rather than the lifecycle rule, owns the seller deletion SLA. Its deletion workflow must account for object versions, replicas, retention settings, and legal holds where applicable. Intelligent-Tiering monitoring and automation charges and lifecycle request costs must also be considered.

## Verification and operational safeguards

- Terraform formatting and validation were run.
- Terraform plans were reviewed with `-refresh=false`.
- No `terraform apply` was run.
- The Python test suite completed with 12 passing tests.
- The plan validator reported the two expected resources missing `landlord_account_id`.
- The supplied seed data, models, plan fixture, and Terraform state were left unchanged.
