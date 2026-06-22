# Validation Rules Claude Must Enforce

## 1. Date validation

- Accept Thai BE dates such as `18/6/2569`.
- Normalize to `DD/MM/YYYY` with BE year for EASY-ACC UI display (BE = AD + 543).
- Detect AD year and convert only when clear (e.g. a 4-digit year < 2200 that is clearly AD).
- **Stop** if date format is ambiguous.
- **Stop** if document date does not match the active EASY-ACC period.
- Due date must not be earlier than document date.

## 2. Amount and VAT validation

Default VAT rate is **7%** unless project/company config says otherwise.

```text
vat_amount                = round(amount_before_vat * 0.07, 2)
total_amount              = amount_before_vat + vat_amount
amount_before_vat_from_gross = round(total_amount / 1.07, 2)
vat_from_gross           = total_amount - amount_before_vat_from_gross
```

Tolerance:

```yaml
amount_tolerance: 0.01
vat_tolerance: 0.01
```

**Prefer reconciling over recomputing (AR/AP).** On the AR/AP screens EASY-ACC computes VAT and
the grand total itself once you enter the before-VAT amount. Supply the before-VAT amount and
**reconcile** the app's computed grand total against the source document total within
`amount_tolerance` — do not type VAT yourself. This handles half-satang rounding correctly
(observed live: 1,121.50 → VAT 78.51 → total 1,200.01).

**Stop** if:

- VAT does not reconcile (outside tolerance).
- Gross amount is lower than VAT.
- Negative amount is not explicitly a credit note / debit correction.
- Field behavior of `จำนวนเงิน` is not known for the target screen (basis unverified).

## 3. WHT validation (AP expense with withholding tax)

- Identify WHT rate: commonly 1%, 2%, 3%, 5%, or a configured value.
- Compute from the before-VAT service amount unless the data bank says otherwise.
- **Stop** if WHT base is unclear.
- **Stop** if vendor tax ID is missing.
- **Stop** if the transaction mixes goods and services but the WHT base is not separated.
- WHT field location on the EASY-ACC AP screen is unconfirmed — flag for run-entry.

## 4. GL balance validation

- `total_debit` must equal `total_credit` within `amount_tolerance`.
- Every line needs an account code and either a debit or a credit (not both non-zero).
- **Stop** if unbalanced.

## 5. Duplicate detection

Generate duplicate keys before UI input:

```json
{
  "duplicate_keys": [
    "target_module + tax_invoice_no + party_code",
    "document_date + party_code + total_amount",
    "tax_invoice_no + vendor_tax_id",
    "source_file_hash"
  ]
}
```

| Level | Condition | Action |
|---|---|---|
| `low` | Unique document number and amount | Continue |
| `medium` | Similar amount/date/party but document differs | Ask review |
| `high` | Same party + same invoice number | Block |
| `unknown` | No search too