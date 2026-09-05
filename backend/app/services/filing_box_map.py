"""Frozen box/item-number mapping for ภ.ง.ด.90 and ภ.ง.ด.94.

This is a STATIC, hand-authored constant -- never computed by an LLM
per-request. Mapping the same computed figure to the same form box every
time is exactly the kind of thing that must NOT vary run to run.

SOURCING HONESTY (read before editing a `note`/`source_page` below):

- PND90 (ภ.ง.ด.90): `data/documents/Ins90_241268.pdf` extracts CLEANLY with
  pdftotext (no ToUnicode CMap problem), so its page numbers below are real
  PDF-page citations, confirmed by directly running
  `pdftotext -layout Ins90_241268.pdf` and finding, e.g., page 3 line
  "7   40 (8)" -- item 7 on the form is Section 40(8) income. Rows sourced
  this way have `source_page` set to an int and `note` says "confirmed via
  pdftotext page N of Ins90_241268.pdf".

- PND94 (ภ.ง.ด.94): `data/documents/Ins94_070666.pdf` is the RD's official
  PND94 instructions PDF, but for TAX YEAR 2566 (2023) -- no 2568/2569
  vintage could be found via web search (RD does not appear to republish
  PND94 instructions annually the way it does PND90/91). Worse, its
  embedded Thai font has no ToUnicode CMap, so pdftotext/pypdf extraction
  of this PDF yields garbled Thai text for item labels -- page numbers for
  PND94 boxes could NOT be reliably read off the PDF text layer, and no
  page-rasterization tool (pdftoppm) was available to OCR it either.
  PND94 rows below therefore have `source_page = None` and are instead
  cross-referenced against the PND94 form's structural layout (which has
  been stable across the 2560/2562/2565/2566/2567/2568 PIT94 form PDFs) via
  2 independent current Thai professional-accounting sources:
  https://www.itax.in.th/pedia/%E0%B8%A0-%E0%B8%87-%E0%B8%94-90/ (iTAX,
  general PND90/94 income-item structure) and
  https://www.krungsri.com/th/krungsri-the-coach/taxes/tax-knowledge/half-year-tax
  (Krungsri, PND94 half-year calculation steps: income -> expense deduction
  -> halved allowances -> bracket tax), both retrieved 2026-09-05. `note`
  says exactly this for every PND94 row -- no page number is invented.
"""
from typing import TypedDict, Optional


class BoxMapRow(TypedDict):
    label_th: str
    label_en: str
    form_item: str
    field: str  # key into the filing pack's computed values this row maps to
    source_page: Optional[int]
    note: str


# Uses the plain string form-type values ("PND90" / "PND94") rather than
# importing filing_pack.FormType, to avoid a circular import (filing_pack
# imports this module). filing_pack.py's FormType is a str Enum whose
# values are exactly these strings.
PND90_BOX_MAP: list[BoxMapRow] = [
    {
        "label_th": "เงินได้ตามมาตรา 40(8)",
        "label_en": "Section 40(8) income (business/trade, incl. online selling)",
        "form_item": "ภ.ง.ด.90 ข้อ 7",
        "field": "gross_income",
        "source_page": 3,
        "note": "Confirmed via pdftotext -layout on data/documents/Ins90_241268.pdf, page 3: "
        "form item 7 is listed against Section 40(8) income.",
    },
    {
        "label_th": "หักค่าใช้จ่าย (เหมา 60% หรือค่าใช้จ่ายจริง)",
        "label_en": "Expense deduction (60% flat, or actual documented expenses)",
        "form_item": "ภ.ง.ด.90 ข้อ 9 (โดยประมาณ)",
        "field": "expense_deduction",
        "source_page": None,
        "note": "Item numbers 1-7 (income by Section 40 type) are confirmed via pdftotext on "
        "Ins90_241268.pdf, but the exact item number for the expense-deduction line "
        "could not be confirmed the same way (surrounding Thai labels on those later "
        "pages did not extract cleanly enough to be certain). Item number given here is "
        "a best-effort estimate from the form's well-known sequential structure "
        "(income items 1-7, then totals/expenses/allowances) -- treat as approximate, "
        "not a verified page citation.",
    },
    {
        "label_th": "เงินได้สุทธิหลังหักค่าใช้จ่ายและค่าลดหย่อน",
        "label_en": "Net taxable income after expenses and allowances",
        "form_item": "ภ.ง.ด.90 (เงินได้สุทธิ)",
        "field": "taxable_income",
        "source_page": None,
        "note": "Not independently page-confirmed; standard PND90 structure per RD form layout.",
    },
    {
        "label_th": "ภาษีที่ต้องชำระ",
        "label_en": "Tax due",
        "form_item": "ภ.ง.ด.90 (ภาษีที่ต้องชำระทั้งสิ้น)",
        "field": "tax_due",
        "source_page": None,
        "note": "Not independently page-confirmed; standard PND90 structure per RD form layout.",
    },
]

PND94_BOX_MAP: list[BoxMapRow] = [
    {
        "label_th": "เงินได้ตามมาตรา 40(5)-(8) (ม.ค.-มิ.ย.)",
        "label_en": "Section 40(5)-(8) income, Jan-Jun half year",
        "form_item": "ภ.ง.ด.94 (เงินได้ตามมาตรา 40(5)-(8))",
        "field": "gross_income",
        "source_page": None,
        "note": "Cross-referenced, not PDF-page-cited: data/documents/Ins94_070666.pdf is the RD's "
        "official PND94 instructions PDF but for tax year 2566 (2023), and its embedded Thai "
        "font has no ToUnicode CMap, so pdftotext/pypdf extraction of Thai item labels is "
        "unreliable for this PDF (unlike Ins90_241268.pdf, which extracted cleanly). Source: "
        "form structure cross-referenced against itax.in.th/pedia (ภ.ง.ด.90 page, general "
        "Section 40 income-item layout shared with PND94) and krungsri.com's half-year-tax "
        "guide (PND94 calculation steps), both retrieved 2026-09-05.",
    },
    {
        "label_th": "หักค่าใช้จ่าย (เหมา 60% หรือค่าใช้จ่ายจริง)",
        "label_en": "Expense deduction (60% flat, or actual documented expenses)",
        "form_item": "ภ.ง.ด.94 (หักค่าใช้จ่าย)",
        "field": "expense_deduction",
        "source_page": None,
        "note": "Cross-referenced from krungsri.com's half-year-tax guide (step 2: deduct expenses "
        "per Section 40(8) rules) -- no PDF page citation available, see gross_income row's note "
        "for why. Retrieved 2026-09-05.",
    },
    {
        "label_th": "ค่าลดหย่อน (ครึ่งหนึ่งของสิทธิเต็มปี)",
        "label_en": "Allowances (half of the full annual PND90 amount)",
        "form_item": "ภ.ง.ด.94 (ค่าลดหย่อนต่างๆ)",
        "field": "total_allowances",
        "source_page": None,
        "note": "Cross-referenced from rd.go.th/60580.html (RD FAQ, fact #5: allowances halved on "
        "PND94 vs PND90) and krungsri.com's half-year-tax guide (step 3). No PDF page citation "
        "available for this PDF vintage -- see gross_income row's note. Retrieved 2026-09-05.",
    },
    {
        "label_th": "เงินได้สุทธิหลังหักค่าใช้จ่ายและค่าลดหย่อน",
        "label_en": "Net taxable income after expenses and (halved) allowances",
        "form_item": "ภ.ง.ด.94 (เงินได้สุทธิ)",
        "field": "taxable_income",
        "source_page": None,
        "note": "Cross-referenced from krungsri.com's half-year-tax guide (step 4: apply this net "
        "figure to the progressive bracket rates). No PDF page citation available for this PDF "
        "vintage -- see gross_income row's note.",
    },
    {
        "label_th": "ภาษีที่ต้องชำระ",
        "label_en": "Tax due",
        "form_item": "ภ.ง.ด.94 (ภาษีที่ต้องชำระทั้งสิ้น)",
        "field": "tax_due",
        "source_page": None,
        "note": "Cross-referenced from krungsri.com's half-year-tax guide (step 5: bracket tax "
        "computation, 5%-35%). No PDF page citation available for this PDF vintage -- see "
        "gross_income row's note.",
    },
]


def get_box_map(form_type_value: str) -> list[BoxMapRow]:
    """Look up the frozen box map by form-type string value ("PND90" /
    "PND94"). Takes a plain string (not filing_pack.FormType) to avoid a
    circular import -- filing_pack.py passes `form_type.value`."""
    if form_type_value == "PND90":
        return PND90_BOX_MAP
    if form_type_value == "PND94":
        return PND94_BOX_MAP
    raise ValueError(f"No box map for form_type: {form_type_value!r}")
