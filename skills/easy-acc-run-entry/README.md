# easy-acc-run-entry

**High-risk, manual-only** execution layer that inputs a validated payload into the EASY-ACC
Windows UI. It can change real accounting data, so it is gated with
`disable-model-invocation: true` and never runs automatically.

## Two swappable actuators (same rules for both)

- **Path A — Cowork computer use** (default): Claude operates mouse/keyboard/screen directly.
  No setup. Pro/Max, research preview.
- **Path B — Custom local runner**: Claude calls a Windows automation runner implementing
  `references/ui-automation-contract.md`. More deterministic, any plan.

Select per run with the `actuator` field. The skill logic, guards, readback, confirmation
summary, and audit logging are identical regardless of actuator.

## Invoke

```text
/easy-acc-run-entry logs/prepared/AP-6906001.json
```

## Preflight

```bash
python scripts/preflight_check.py ../../../logs/prepared/AP-6906001.json \
  --expect-company "<COMPANY>" --expect-period-be 2569
```

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Execution flow, stop rules, output contract |
| `references/ui-automation-contract.md` | Path B tool contract / Path A capability checklist |
| `references/screen-state-map.md` | Per-screen detection anchors and field order |
| `references/save-confirmation-rules.md` | When save is allowed + confirmation summary |
| `references/error-recovery.md` | What to do on each stop condition |
| `scripts/preflight_check.py` | Re-validates payload + checks run policy before entry |

## Golden rules

- No save without explicit human confirmation (or officially enabled unattended mode).
- Stop on company / path / period / screen mismatch, readback mismatch, or unexpected popup.
- Every attempt writes an audit log (`logs/attempted/` or `logs/saved/`).
- Computer use does not relax any 