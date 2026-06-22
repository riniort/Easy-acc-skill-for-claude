# Transaction Routing Rules

Choose the target workflow from transaction **evidence**, not from vague user wording alone.

| Evidence | Route | Notes |
|---|---|---|
| Customer sale with item/service lines and tax invoice | BI/Billing | Needs BI screen capture before full automation (blocked, §21.1) |
| Simple AR receivable entry shown in local screenshot | AR | Use AR UI field map |
| Supplier expense invoice | AP | Use AP UI field map |
| Supplier invoice with VAT + WHT | AP | WHT handling must be configured from data bank (location unconfirmed) |
| Purchase invoice with VAT and non-VAT items | AP or PO | Depends on whether inventory is involved |
| Customer deposit deducted from sale | BI/Billing | Needs deposit pseudo-item rules |
| Credit note / debit note | BI/Billing or AR | Depends on company workflow and document type |
| Manual adjustment with debit/credit lines | GL | Require accounting lead approval |
| Unknown party code, unknown account, unclear VAT | Human review | Do not input |

## Screen IDs

| Module | screen_id | Window title (guard) |
|---|---|---|
| AR | `UI-AR-TRANSACTION-ENTRY-v1` | EASY-ACC Accounting System - Account Receivable |
| AP | `UI-AP-TRANSACTION-ENTRY-v1` | EASY-ACC Accounting System - Account Payable |
| GL | `UI-GL-TRANSACTION-ENTRY-v1` | EASY-ACC Accounting System - General Ledger |
| BI | `UI-BI-BILLING-ENTRY-v1` | (not yet captured — blocked) |

## Routing guardrails

- If route resolves to BI/Billing, set `automation_status = blocked_unsupported_case` until
  the BI screen map exists, unless the user explicitly accepts AR fallback for a simple
  receivable.
- If party code or account code is a name only (no code), route output is `ready_for_review`
  at best — codes are required for UI input.
- GL route always sets `required_human_confirmation = true` and needs accounting-lead sign-off.
