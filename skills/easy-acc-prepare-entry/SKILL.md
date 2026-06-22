---
name: easy-acc-prepare-entry
description: Prepare and validate EASY-ACC sale, expense, AR, AP, and GL transaction payloads from user input, OCR text, invoices, receipts, or spreadsheets. Use for sale entry, expense entry, AP/AR transaction preparation, VAT validation, WHT validation, GL journal preparation, duplicate checks, and transaction routing before any EASY-ACC UI automation. Use whenever the user wants accounting data prepared, normalized, or checked before automated EASY-ACC input.
argument-hint: "[source-file-or-transaction-description]"
allowed-tools:
  - Read
  - Grep
  - Glob
---

# EASY-ACC Prepare Entry Skill

You are the preparation and validation layer for EASY-ACC Accounting System automation.

EASY-ACC is a legacy Thai Windows desktop accounting app. It has **no native MCP, no
Claude connector, no REST API, and no safe DB-write API**. This skill only prepares and
validates data — it never enters anything into EASY-ACC. Actual entry is performed by the
`easy-acc-run-entry` skill via an external UI actuator (Cowork computer use or a custom
runner). See `../easy-acc-run-entry/SKILL.md`.

## Required project knowledge

First read or search these files when available:

1. `easy_acc_ai_automation_databank.md` — main source of truth (if present in project root).
2. `references/transaction-routing.md` — module routing rules.
3. `references/validation-rules.md` — VAT, WHT, date, amount, and duplicate checks.
4. `references/thai-field-dictionary.md` — exact Thai field labels.
5. `schemas/easy_acc_transaction.schema.json` — output contract.
6. `references/source-index.md` — where each rule comes from and what is still blocked.

> The companion `easy_acc_ai_automation_databank.md` may not yet be in the project. When it
> is absent, rely on the references in this skill and the screen captures, and treat any
> company-specific rule (WHT rates, auto-numbering, `จำนวนเงิน` basis) as **unverified** —
> see the open items in `references/source-index.md`.

## Hard safety rules

- Never claim the transaction has been entered into EASY-ACC unless the run-entry skill or UI automation actuator confirms it.
- Never directly edit EASY-ACC data files.
- Never infer missing required fields silently.
- Never mark a transaction ready for UI input if date, document number, party code, amount, VAT, or module route is uncertain.
- Preserve Thai field names exactly.
- Output validation results and stop reasons clearly.

## Work process

1. Parse the source input.
2. Classify transaction type:
   - sale_invoice
   - service_sale
   - online_sale
   - customer_deposit
   - sale_credit_note
   - sale_debit_note
   - ap_expense
   - ap_purchase_invoice
   - ap_expense_with_wht
   - ap_expense_with_retention
   - mixed_vat_purchase
   - late_input_vat
   - gl_journal
   - human_review_required
3. Route to EASY-ACC module (see `references/transaction-routing.md`):
   - BI/Billing for itemized sale invoice workflows.
   - AR for Account Receivable transaction entry shown in local UI map.
   - AP for expense / supplier invoice workflows.
   - GL only for explicit journal vouchers or corrections approved by accounting lead.
4. Normalize fields (see `references/thai-field-dictionary.md`).
5. Validate amounts, VAT, WHT, dates, document number, party code, and duplicate risk
   (see `references/validation-rules.md`).
6. Produce a structured JSON payload conforming to the schemas.
7. Produce a human-readable summary.
8. Set `automation_status`:
   - `ready_for_review`
   - `ready_for_ui_input`
   - `blocked_missing_data`
   - `blocked_validation_error`
   - `blocked_duplicate_risk`
   - `blocked_unsupported_case`

## Output format

Always output:

```json
{
  "schema_version": "easy_acc_transaction_v1",
  "automation_status": "ready_for_review",
  "transaction_type": "ap_expense",
  "target_module": "AP",
  "target_screen_id": "UI-AP-TRANSACTION-ENTRY-v1",
  "evidence_level": "configured_map",
  "required_human_confirmation": true,
  "source": {
    "source_type": "manual_text|ocr|excel|pdf|image|email",
    "source_reference": ""
  },
  "fields": {},
  "calculations": {},
  "validation": {
    "passed": false,
    "checks": [],
    "errors": [],
    "warnings": []
  },
  "duplicate_check": {
    "risk_level": "unknown|low|medium|high",
    "keys": []
  },
  "ui_input_policy": {
    "allow_prepare": true,
    "allow_input": false,
    "allow_save": false
  }
}
```

Validate output with the bundled script before handing off:

```bash
python .claude/skills/easy-acc-prepare-entry/scripts/validate_payload.py <payload.json>
```

## Readiness rule

Only set `automation_status = "ready_for_ui_input"` when every required field is known,
calculations pass, duplicate risk is not high, and the target screen is known. Write the
prepared payload to `logs/prepared/<doc-no>.json` for the run-entry skill to consume.
