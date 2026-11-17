"""
B2, part 1 — landlord-account-scoped screening report access.
"""
from app.models import PropertyManager, ScreeningReport, Property, Tenant


def can_access_screening_report(
    actor: PropertyManager,
    report: ScreeningReport,
    *,
    properties: list[Property],
    tenants: list[Tenant],
) -> bool:
    """
    Allow access only when the report's tenant belongs to a property
    managed under the actor's landlord account.

    Fail closed when a tenant/property is missing or ambiguous.
    """
    matching_tenants = [tenant for tenant in tenants if tenant.id == report.tenant_id]

    if len(matching_tenants) != 1:
        return False

    tenant = matching_tenants[0]
    matching_properties = [
        property_record
        for property_record in properties
        if property_record.id == tenant.property_id
    ]

    if len(matching_properties) != 1:
        return False

    property_record = matching_properties[0]

    return (
        bool(actor.landlord_account_id)
        and actor.landlord_account_id == property_record.landlord_account_id
    )
