# Save Confirmation Rules

## Never save when evidence is weak

Do not allow save when any field/condition has:

```yaml
evidence_level: inferred
confidence_below: 0.90
required_field_missing: true
readback_failed: true
duplicate_risk: high
screen_id: UNKNOWN
company_guard_failed: true
period_guard_failed: true
```

## Operating modes

| Mode | Types into UI? | Saves? | Use |
|---|---|---|---|
| `dry_run` | No | No | Plan + guard checks only |
| `supervised_input_no_save` | Yes | No | Fill + readback, leave unsaved for human |
| `supervised_input_with_save` | Yes | Yes, after explicit confirm | Normal supervised entry |
| `production_input_with_save` | Yes | Yes, if unattended officially enabled | High-volume, only after blockers closed |

## Human confirmation summary (show before save)

```text
Ready to input/save in EASY-ACC:
Module: AP
Screen: UI-AP-TRANSACTION-ENTRY-v1
Date: 18/06/2569
Vendor: V0001
Tax invoice no.: AP-6906001
Amount before VAT: 1,000.00
Input VAT: 70.00
Total: 1,070.00
Due date: 18/07/2569
Note: ค่าบริการสำนักงาน

Please confirm: save / input only / cancel
```

Only proceed when the user explicitly chooses **save**, or an approved production unattended
mode is officially enabled. `input only` → leave unsaved. `cancel` → abort, write attempt log.

## Save mechanics

- `ตกลง` is the only save action. Click it as a discrete final step.
- Do not use Enter to save unless verified (it may move focus or open a lookup).
- After save: capture confirmation popup, document reference, and the new transaction-history
  row; screenshot to `logs/saved/`.

## Correction policy (after a wrong save)

1. Do not overwrite silently.
2. Check whether the transaction has payment/receipt/billing layers.
3. Follow correction rules from the data bank.
4. Create a correction payload via `easy-acc-prepare-entry`.
5. Require accounting-lead review for GL-level corrections.
