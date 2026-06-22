---
name: easy-acc-run-entry
description: Manually run a validated EASY-ACC transaction payload into the EASY-ACC UI via the chosen actuator (Cowork computer use or a custom local Windows runner). Use only for supervised EASY-ACC UI data entry, after prepared data has passed validation and the user explicitly asks to input it into EASY-ACC. Never invoke automatically.
disable-model-invocation: true
argument-hint: "[path-to-validated-json]"
allowed-tools:
  - Read
  - Bash
---

# EASY-ACC Run Entry Skill

You are the controlled execution layer for EASY-ACC UI automation.

EASY-ACC has **no native MCP, API, or DB-write interface**. This skill drives the EASY-ACC
**Windows UI like a human**, through one of two swappable actuators (the rules below are
identical for both — only who performs the clicks changes):

- **Path A — Cowork computer use (default):** Claude performs the screenshot / click / type /
  readback itself via computer use. No runner needed. Pro/Max, research preview. Best for
  prototyping and low-volume supervised entry.
- **Path B — Custom local runner:** Claude calls a developer-owned Windows runner
  (pywinauto / pyautogui / AutoHotkey / Power Automate Desktop) that exposes the
  `references/ui-automation-contract.md` tool contract. More deterministic; any plan;
  required for Team/Enterprise, scheduled/headless, or high volume.

Choose the actuator at run time via the `actuator` field (`cowork_computer_use` or
`local_runner`). Everything else in this skill is the same on both paths.

Because this skill can cause real accounting data changes, it is **manual only**
(`disable-model-invocation: true`).

## Required inputs

A validated transaction payload (from `easy-acc-prepare-entry`) with:

- `automation_status = ready_for_ui_input`
- `validation.passed = true`
- `ui_input_policy.allow_input = true`
- `target_module` known
- `target_screen_id` known
- required fields complete

Re-run the validator before doing anything:

```bash
python ../easy-acc-prepare-entry/scripts/validate_payload.py <payload.json> \
  --expect-company "<COMPANY>" --expect-period-be 2569
```

## Hard stop rules

Stop immediately if:

- EASY-ACC window title is not detected.
- Company name does not match expected company.
- Period does not match the transaction date.
- Path/status bar does not match expected data folder.
- Any required field cannot be focused, typed, or read back.
- A Thai party code (customer/vendor) does not resolve to a name on readback — this almost
  always means the Windows input language dropped to ENG and the code was typed as `?`. Re-set
  Thai (Kedmanee) layout and re-key; never save an unresolved party code. See
  `references/cowork-entry-playbook.md` §0.5.
- Any amount readback differs from prepared payload.
- VAT/WHT/totals do not match.
- Duplicate transaction risk is high.
- A modal/error/print prompt appears and the behavior is not mapped.
- User has not confirmed save.

See `references/error-recovery.md` for what to do on each stop.

## Execution flow

1. Load payload and run preflight (`scripts/preflight_check.py`).
2. Confirm operating mode:
   - `dry_run`
   - `supervised_input_no_save`
   - `supervised_input_with_save`
   - `production_input_with_save`
3. Detect EASY-ACC process/window (screenshot on Path A; `get_app_state` on Path B).
4. Validate company, module, period, and path against `company_guard`.
5. Navigate to target screen; verify by title, field labels, and anchors
   (`references/screen-state-map.md`). For Path A, follow the exact validated click flow in
   `references/cowork-entry-playbook.md`.
6. Input fields using **focus → clear → type → readback → compare** for each field group.
7. Validate computed fields and totals against the payload.
8. Show the human-confirmation summary (`references/save-confirmation-rules.md`) and ask for
   final confirmation unless policy explicitly allows unattended save.
9. Save (`ตกลง`) only after confirmation.
10. Capture confirmation / document number / transaction-history row.
11. Write audit log to `logs/saved/` (or `logs/attempted/` if blocked).
12. Return result.

## Required response after run

```json
{
  "run_status": "completed|blocked|failed|saved|dry_run_completed",
  "actuator": "cowork_computer_use|local_runner",
  "saved": false,
  "document_reference": "",
  "target_module": "AP",
  "target_screen_id": "UI-AP-TRANSACTION-ENTRY-v1",
  "checks_performed": [],
  "blocked_reason": "",
  "audit_log_path": ""
}
```

## Non-negotiable

Using Cowork computer use does **not** relax any save or validation rule. If Claude cannot
read a field back and confirm it, it stops — whether the typing was done by computer use or a
runner. No blind save. The `ตกลง` (save) button is always a separate final action after
validation and explicit confirma