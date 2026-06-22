# easy-acc-prepare-entry

Safe preparation + validation layer for EASY-ACC automation. **No side effects** — it never
touches EASY-ACC. It converts source documents (text, OCR, PDF, image, Excel rows) into a
normalized, validated transaction JSON payload that the `easy-acc-run-entry` skill can later
input into the EASY-ACC UI.

## What it does

- Classifies the transaction (sale / AR / AP expense / WHT / GL journal / human-review).
- Routes to the correct EASY-ACC module (AR, AP, GL, BI/Billing).
- Normalizes fields to exact Thai labels.
- Validates dates (Thai BE), amounts, VAT (7% default), WHT, due dates, document numbers,
  party codes, and duplicate risk.
- Emits a JSON payload and a human-readable confirmation summary.

## Invoke

```text
/easy-acc-prepare-entry Prepare this vendor invoice for EASY-ACC AP input:
Date 18/6/2569, Vendor V0001, invoice AP-6906001, service fee 1,000, VAT 70, due 18/7/2569.
```

## Validate a payload

```bash
python scripts/validate_payload.py ../../../logs/prepared/AP-6906001.json
```

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Skill instructions and output contract |
| `references/source-index.md` | Source map + open/blocked items |
| `references/transaction-routing.md` | Module routing rules |
| `references/thai-field-dictionary.md` | Exact Thai field labels per screen |
| `references/validation-rules.md` | Date / VAT / WHT / duplicate rules |
| `references/examples.md` | Worked payload examples (AR / AP / GL) |
| `schemas/*.schema.json` | JSON Schemas (base, AR, AP, GL) |
| `scripts/validate_payload.py` | Pre-UI payload validator |

## Safety

This skill is auto-invocable (read-only). It sets `ui_input_policy.allow_input=false` and
`allow_save=false` by default. Only `easy-acc-run-entry` can change UI state, and only with
explicit human confirmation.
