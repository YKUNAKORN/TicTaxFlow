"""Filing-pack preview endpoints for ภ.ง.ด.94 / ภ.ง.ด.90.

INTEGRITY: these endpoints PREPARE a pack of figures for the user to copy
into RD's own e-Filing site themselves. They never file, submit, or send
anything to the Revenue Department -- see app/services/filing_pack.py's
module docstring. Route names stay `preview`/`forms`, never
`submit`/`file`.

`tax_year` convention: this endpoint accepts tax_year as a Christian Era
(CE) calendar year (e.g. 2569 is NOT accepted here -- pass 2026), matching
datetime.now().year (which is CE, and what app.core.config.settings.
DEFAULT_TAX_YEAR is set to) and the convention already used by
app.agents.accountant's tax_rules queries (get_active_tax_rules defaults
to DEFAULT_TAX_YEAR, a CE year). GET /filing/forms with no tax_year
resolves it to the newest CE year the seeded sample data covers.
CLAUDE.md flags the tax_rules.tax_year BE/CE convention as unconfirmed in
general -- this endpoint fixes ONE convention (CE) at the API boundary and
converts nowhere else, since app.agents.accountant already queries
tax_rules by the same CE DEFAULT_TAX_YEAR value elsewhere in this codebase.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user_id
from app.services.income_aggregator import resolve_data_year
from app.services.filing_pack import FormType, build_filing_pack, filing_deadline, period_range_for_form

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/preview", summary="Preview a filing pack for the current user")
async def preview_filing_pack(
    form_type: FormType = Query(..., description="PND94 (mid-year) or PND90 (annual)"),
    tax_year: int = Query(..., description="Christian Era (CE) calendar year, e.g. 2026"),
    user_id: str = Depends(get_current_user_id),
):
    """Build and return the filing pack for `user_id`. `user_id` always
    comes from the validated bearer token (get_current_user_id) -- never
    from a client-supplied parameter, per CLAUDE.md's auth rule.

    Invalid `form_type` (e.g. PND91) is rejected automatically by FastAPI's
    enum-typed Query validation with a 422, before this function body runs.
    """
    pack = build_filing_pack(user_id=user_id, form_type=form_type, tax_year=tax_year)
    return {"success": True, "data": pack}


@router.get("/forms", summary="List available filing forms and their deadlines")
async def list_available_forms(
    tax_year: Optional[int] = Query(
        default=None,
        description="Christian Era (CE) calendar year. Omit to use the most "
        "recent year the seeded sample data covers.",
    ),
    user_id: str = Depends(get_current_user_id),
):
    """Cheap listing of supported forms + their filing windows/deadlines --
    does NOT compute a full filing pack (no income aggregation, no tax
    estimate). `user_id` is required (auth'd) even though this call doesn't
    read user data yet, so the route consistently requires a valid token.

    When `tax_year` is omitted, it resolves to the newest CE year the
    seeded fixtures actually have rows for (`resolve_data_year`), so the
    frontend -- which feeds this value straight back into
    GET /filing/preview -- does not request a year whose filing pack would
    be all zeros. The response echoes the resolved `tax_year` so the client
    knows which year it got.
    """
    if tax_year is None:
        tax_year = resolve_data_year(datetime.now().year)

    forms = []
    for form_type in FormType:
        date_from, date_to = period_range_for_form(form_type, tax_year)
        forms.append({
            "form_type": form_type.value,
            "covers_period": {"date_from": date_from, "date_to": date_to},
            "deadline": filing_deadline(form_type, tax_year),
        })

    return {"success": True, "data": {"tax_year": tax_year, "forms": forms}}
