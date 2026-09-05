# SOURCES.md — Phase 3A (ภ.ง.ด.94/90 filing pack) figures

Every figure here was checked against the cited source on **2026-09-05**. If
you change a number in `app/core/tax_constants.py` or `app/services/tax_estimator.py`,
update this table in the same change.

| Constant | Value | Source | Notes |
|---|---|---|---|
| `tax_estimator.PIT_BRACKETS` | 0-150k@0%, 150k-300k@5%, 300k-500k@10%, 500k-750k@15%, 750k-1M@20%, 1M-2M@25%, 2M-4M@30%, 4M+@35% | https://rd.go.th/english/6045.html | In effect since tax year 2560 (2017); current as of tax year 2568/2569. |
| `PND94_FLAT_EXPENSE_RATE` | 0.60 (60%) | Royal Decree No. 629 (B.E. 2560/2017), reported via https://www.prachachat.net/finance/news-50328 | Supersedes the old graduated 60-85% table at rd.go.th/6052.html (that page is dated "last updated 2016", pre-decree -- not used). Corroborated by PEAK/iTAX current guides. Base is GROSS income, not net of marketplace fees. |
| `PND94_ALLOWANCE_HALVING_FACTOR` | 0.5 | https://www.rd.go.th/60580.html | Example confirmed in source: personal allowance 30,000 THB (PND94) vs 60,000 THB (PND90 annual); per-child 15,000 THB (PND94) vs 30,000 THB (annual). |
| `PND94_SINGLE_THRESHOLD` | 60,000 THB | https://www.rd.go.th/60580.html | Half-year Section 40(5)-(8) income threshold requiring a single taxpayer to file PND94. |
| `PND94_MARRIED_THRESHOLD` | 120,000 THB | https://www.rd.go.th/60580.html | Same threshold for a married couple filing together. |
| PND90 paper filing window | 1 Jan - 31 Mar (year after tax year) | https://www.rd.go.th/46202.html | RD's recurring annual extension-announcement pattern. |
| PND90 online (e-Filing) deadline | 8 Apr (year after tax year) | https://www.rd.go.th/46202.html, corroborated by Thairath/Thansettakij (Sep 2026) reporting 8 Apr 2569 deadline for tax year 2568 | |
| PND94 paper filing window | 1 Jul - 30 Sep (same tax year) | https://www.rd.go.th/60580.html | Covers Section 40(5)-(8) income earned Jan-Jun. |
| PND94 online (e-Filing) deadline | ~8 Oct (same tax year) | RD historical extension pattern; corroborated by Krungsri/KTC 2568 filing guides | |
| `LATE_FILING_FINE_MAX` | 2,000 THB | https://www.rd.go.th/37392.html | มาตรา 35 criminal fine; applies even when no tax is due. |
| `LATE_PAYMENT_SURCHARGE_MONTHLY_RATE` | 1.5% per month (or part-month) | https://www.rd.go.th/37392.html | เงินเพิ่ม on unpaid tax, from day after filing deadline. Only applies when tax is owed. |
| `PENALTY_MAX_MULTIPLIER` | up to 2x tax due | https://www.rd.go.th/37392.html | เบี้ยปรับ, varies by how underpayment is discovered. |

## Known gap (not a fabricated fact)

`Ins94_070666.pdf` (indexed into the RAG corpus) is the RD's official PND94
filing-instructions PDF for **tax year 2566 (2023)**, the most recent one
findable via web search — RD does not appear to republish PND94 instructions
every year the way it does for PND90/91, and no 2568/2569-specific PND94
instructions PDF could be located. The form's box/item layout has been
structurally stable across the 2560/2562/2565/2566/2567/2568 PND94 form PDFs
(cross-referenced), so the box numbers in `app/services/filing_box_map.py`
are still used, but see that file's header comment for exactly which rows
carry a real PDF page citation vs. a cross-reference citation from secondary
professional-accounting sources.
