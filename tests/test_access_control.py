"""
Tests for landlord-account-scoped screening report access.
"""
from dataclasses import replace

from app.access_control import can_access_screening_report


def test_manager_can_access_report_in_own_landlord_account(
    property_managers, properties, tenants, screening_reports
):
    assert can_access_screening_report(
        property_managers[0],
        screening_reports[0],
        properties=properties,
        tenants=tenants,
    ) is True


def test_manager_cannot_access_another_landlords_report(
    property_managers, properties, tenants, screening_reports
):
    assert can_access_screening_report(
        property_managers[0],
        screening_reports[1],
        properties=properties,
        tenants=tenants,
    ) is False


def test_missing_tenant_fails_closed(
    property_managers, properties, screening_reports
):
    assert can_access_screening_report(
        property_managers[0],
        screening_reports[0],
        properties=properties,
        tenants=[],
    ) is False


def test_missing_property_fails_closed(
    property_managers, tenants, screening_reports
):
    assert can_access_screening_report(
        property_managers[0],
        screening_reports[0],
        properties=[],
        tenants=tenants,
    ) is False


def test_duplicate_tenant_id_fails_closed(
    property_managers, properties, tenants, screening_reports
):
    duplicate_tenants = tenants + [replace(tenants[0], name="Conflicting tenant")]

    assert can_access_screening_report(
        property_managers[0],
        screening_reports[0],
        properties=properties,
        tenants=duplicate_tenants,
    ) is False


def test_duplicate_property_id_fails_closed(
    property_managers, properties, tenants, screening_reports
):
    duplicate_properties = properties + [
        replace(properties[0], landlord_account_id="la-002")
    ]

    assert can_access_screening_report(
        property_managers[0],
        screening_reports[0],
        properties=duplicate_properties,
        tenants=tenants,
    ) is False
