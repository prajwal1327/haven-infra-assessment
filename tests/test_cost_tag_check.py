"""
Tests for generic and repeatable Terraform cost-tag validation.
"""
import json
from pathlib import Path

from scripts.cost_tag_check import check_plan


PLAN_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "plan.json"


def test_fixture_flags_only_resources_missing_landlord_account_tag(capsys):
    result = check_plan(str(PLAN_FIXTURE))

    captured = capsys.readouterr()

    assert result == 1
    assert "aws_s3_bucket.listing_media" in captured.out
    assert "aws_lambda_function.mls_feed_sync" in captured.out

    assert "aws_s3_bucket.landlord_media[0]" not in captured.out
    assert "aws_lambda_function.screening_report_export" not in captured.out
    assert "aws_s3_bucket.archive_media" not in captured.out
    assert "aws_s3_bucket.decommissioned_media" not in captured.out


def test_check_is_idempotent(capsys):
    first_result = check_plan(str(PLAN_FIXTURE))
    first_output = capsys.readouterr().out

    second_result = check_plan(str(PLAN_FIXTURE))
    second_output = capsys.readouterr().out

    assert first_result == second_result == 1
    assert first_output == second_output
    assert first_output.count("aws_s3_bucket.listing_media") == 1
    assert first_output.count("aws_lambda_function.mls_feed_sync") == 1


def test_validator_handles_multiple_resource_types_and_blank_tags(
    tmp_path, capsys
):
    plan = {
        "resource_changes": [
            {
                "address": "google_storage_bucket.example",
                "change": {
                    "actions": ["create"],
                    "after": {"tags": {"landlord_account_id": "la-001"}},
                },
            },
            {
                "address": "aws_lambda_function.example",
                "change": {
                    "actions": ["update"],
                    "after": {"tags": {"landlord_account_id": "   "}},
                },
            },
            {
                "address": "azurerm_storage_account.example",
                "change": {
                    "actions": ["create"],
                    "after": {"tags": {}},
                },
            },
        ]
    }

    plan_file = tmp_path / "custom-plan.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")

    result = check_plan(str(plan_file))
    output = capsys.readouterr().out

    assert result == 1
    assert "aws_lambda_function.example" in output
    assert "azurerm_storage_account.example" in output
    assert "google_storage_bucket.example" not in output


def test_valid_plan_passes(tmp_path, capsys):
    plan = {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.example",
                "change": {
                    "actions": ["create"],
                    "after": {"tags": {"landlord_account_id": "la-001"}},
                },
            },
            {
                "address": "aws_lambda_function.example",
                "change": {
                    "actions": ["update"],
                    "after": {"tags": {"landlord_account_id": "la-002"}},
                },
            },
        ]
    }

    plan_file = tmp_path / "valid-plan.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")

    result = check_plan(str(plan_file))
    output = capsys.readouterr().out

    assert result == 0
    assert "PASS:" in output


def test_noop_and_delete_are_ignored(tmp_path, capsys):
    plan = {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.noop",
                "change": {"actions": ["no-op"], "after": {"tags": {}}},
            },
            {
                "address": "aws_s3_bucket.deleted",
                "change": {"actions": ["delete"], "after": None},
            },
        ]
    }

    plan_file = tmp_path / "ignored-plan.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")

    result = check_plan(str(plan_file))
    output = capsys.readouterr().out

    assert result == 0
    assert "PASS:" in output
    assert "noop" not in output
    assert "deleted" not in output


def test_missing_plan_file_fails(capsys, tmp_path):
    result = check_plan(str(tmp_path / "does-not-exist.json"))

    captured = capsys.readouterr()

    assert result == 1
    assert "ERROR:" in captured.err
