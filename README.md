# EASY-ACC Automation

A Claude Cowork plugin that turns Claude into a careful accounting-data-entry coworker for
**EASY-ACC**, a legacy Thai Windows desktop accounting system. EASY-ACC has no API, MCP, or
database write interface, so Claude prepares and validates data, then operates the EASY-ACC
Windows UI like a human (via Cowork computer use) — with guards and human confirmation.

## What it does

- **Prepares & validates** AR sales, AP expenses, and GL journals from text, OCR, PDFs, images,
  or spreadsheets into a normalized transaction payload (Thai field labels, 7% VAT, WHT, dates,
  duplicate checks).
- **Routes** each transaction to the right module (AR / AP / GL / BI-Billing).
- **Enters & saves** validated transactions into the EASY-ACC UI — only when you ask — with
  screen/company/period/path guards, field readback, and an explicit save confirmation.

## Skills

| Skill | What it does | Risk |
|---|---|---|
| **easy-acc-prepare-entry** | Convert source docs into a validated transaction payload. No side effects. Auto-invocable. | Low |
| **easy-acc-run-entry** | Drive the EASY-ACC UI to input/save a validated payload. Manual-only (never auto-runs). | High |

The two skills are designed to be used in sequence: prepare → review → run.

## How to use

1. "Prepare this vendor invoice for EASY-ACC AP: …" → Claude builds and validates the payload.
2. Review the summary Claude produces.
3. "Enter it into EASY-ACC" → Claude opens the right module on the correct company, fills the
   fields, reads them back, shows a confirmation summary, and saves only after you confirm.

## Requirements & safety

- **Windows + EASY-ACC installed** (modules `glmain32.exe`, `armain32.exe`, `apmain32.exe`).
- **Cowork computer use** (Path A) drives the UI — Pro/Max, research preview. For higher-volume
  or scheduled/headless runs, a custom local Windows runner (Path B) implementing the
  `easy-acc-run-entry` UI contract can be swapped in; the skill logic is identical either way.
- Claude **never** saves without explicit confirmation, **never** edits EASY-ACC data files,
  and **stops** on company/path/period/screen mismatch, readback mismatch, duplicate risk, or
  any unexpected popup.
- Always verify the company **data-folder path** (not the display name) before posting — the
  selector mixes test and live books.

## Validated against the live app (2026-06-19)

GL, AR, and AP entry screens were field-map verified, and one real balanced GL journal plus an
AR sale and AP expense were entered and saved end-to-end in a test company. Findings (period
enforcement, doc-no length limit, auto-VAT, account-cell behavior, company-select safety) are
baked into the skill references — see `skills/*/references/`.

## Out of scope / open items

- BI/Billing itemized invoice screen is not yet mapped.
- Company-specific WHT location/rates, auto-numbering, and the `จำนวนเงิน` basis should be
  confirmed against the company data bank before production use.
