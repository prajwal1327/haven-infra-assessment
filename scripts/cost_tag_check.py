"""
B2, part 2 — validate landlord-account cost tags in a Terraform plan.
"""
import json
import sys


REQUIRED_TAG = "landlord_account_id"


def check_plan(plan_path: str) -> int:
    """
    Return 0 when every created or updated resource has a non-empty
    landlord_account_id tag; otherwise return 1.
    """
    try:
        with open(plan_path, encoding="utf-8") as plan_file:
            plan = json.load(plan_file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: Unable to read Terraform plan: {exc}", file=sys.stderr)
        return 1

    if not isinstance(plan, dict) or not isinstance(
        plan.get("resource_changes"), list
    ):
        print(
            "ERROR: Invalid Terraform plan: resource_changes must be a list.",
            file=sys.stderr,
        )
        return 1

    missing_addresses = set()

    for resource in plan["resource_changes"]:
        if not isinstance(resource, dict):
            print("ERROR: Invalid resource_changes entry.", file=sys.stderr)
            return 1

        change = resource.get("change")
        if not isinstance(change, dict):
            print("ERROR: Resource entry has no valid change object.", file=sys.stderr)
            return 1

        actions = change.get("actions")

        # Only standalone creates and updates are in scope.
        if actions not in (["create"], ["update"]):
            continue

        address = resource.get("address")
        if not isinstance(address, str) or not address.strip():
            address = "<unknown resource address>"

        after = change.get("after")
        if not isinstance(after, dict):
            missing_addresses.add(address)
            continue

        tags = after.get("tags")
        tag_value = tags.get(REQUIRED_TAG) if isinstance(tags, dict) else None

        if not isinstance(tag_value, str) or not tag_value.strip():
            missing_addresses.add(address)

    if missing_addresses:
        print(f"FAIL: Resources missing non-empty {REQUIRED_TAG} tag:")
        for address in sorted(missing_addresses):
            print(f" - {address}")
        return 1

    print(f"PASS: All created and updated resources have {REQUIRED_TAG}.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            f"Usage: python {sys.argv[0]} <terraform-plan.json>",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(check_plan(sys.argv[1]))
