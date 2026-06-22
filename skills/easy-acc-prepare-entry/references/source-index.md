# Source Index & Evidence Levels

This file records where each rule in the prepare-entry skill comes from, and what is still
unverified. Update it whenever the databank or new screenshots arrive.

## Sources

| Source | Status | Covers |
|---|---|---|
| `easy_acc_claude_cowork_skill_guide.md` | Present (project root) | Skill design, payload contract, validation policy, guardrails |
| `databank img/AR.png` | Present | AR Transaction Entry field layout, radios, history grid, guards |
| `databank img/AP.png` | Present | AP Transaction Entry field layout, radios, history grid, guards |
| `databank img/GL.png` | Present | GL Transaction Entry grid, totals, guards |
| `easy_acc_ai_automation_databank.md` | **MISSING** | Company-specific WHT, auto-numbering, correction workflow, deposit/credit-note rules |

## Confirmed from screen captures

- Company guard text: `<COMPANY_NAME>` (set per company at run time)
- Path guard text: `Path: <DATA_FOLDER_PATH>` (the company's data folder, e.g. `…\ECA\<company>`)
- AR/AP period shown: `1/1/2569`
- GL period shown: `1/1/2568`  ← **note the year difference; verify which period is active before GL entry**
- Save / cancel / exit buttons: `ตกลง` / `ยกเลิก` / `ออก`
- Lookup affordance `...` present on: AR รหัสลูกค้า, AR/AP บัญชีแยกประเภท, AP รหัสเจ้าหนี้, AP เลขที่จัดลำดับภาษี, GL สมุดรายวันทั่วไป

## Live verification — 2026-06-19 (Path A dry-run, GL + AR + AP)

Ran a supervised dry-run against the live app (no typing, no save). Findings:

- GL module process is **`glmain32.exe`** (under `G:\Program Files\ECACC32\`). AR = `armain32`,
  AP = `apmain32`. The computer-use grant must target the **`.exe` basename**, e.g.
  `glmain32.exe` — display name / window title do not resolve.
- On launch, GL shows a **"Select company data folder"** dialog (`เลือกแฟ้มข้อมูลกิจการ`) first.
  The list contains multiple books per company plus `... GL` variants, and may include live
  books. **Select by the data-folder path, never the display name.**
- Opened a test book → status bar showed the test company's `<COMPANY_NAME>`, its
  `<DATA_FOLDER_PATH>`, and `Period: 1/1/2568`.
- **GL, AR, and AP Transaction Entry screens ALL VERIFIED** against `screen-state-map.md` —
  every header field, radio option, grid/history column, footer/displays, and the
  `ตกลง/ยกเลิก/ออก` buttons match exactly. AP screen confirmed to have **no WHT field**.
  Module processes: GL `glmain32.exe`, AR `armain32.exe`, AP `apmain32.exe` (launch AR/AP from
  the ECACC32 folder first so the grant resolver can see them).
- **Period/date mismatch confirmed live:** the entry form auto-filled `วันที่ = 19/6/2569`
  (today, BE 2569) while the active period is `1/1/2568`. This is exactly blocker #10 / the
  date-vs-period validation rule — the guard is relevant and must be enforced per company.

## Live end-to-end SAVE test — 2026-06-19 (GL, test company)

Saved a real balanced GL journal into the `test` book and verified it via the journal report.

- **Period enforcement is hard at the app level.** Saving with date `19/6/2569` (outside the
  active 2568 period) raised: `วันที่บันทึกไม่ถูกต้อง หรือไม่อยู่ในงวดบัญชี`
  ("recording date invalid or not within the accounting period"). Changing the date to
  `19/6/2568` cleared it. → The prepare-entry period guard is mandatory, not advisory.
- **เลขที่เอกสาร (doc no) max length = 10 chars.** Typed `TESTCLAUDE01`, app stored `TESTCLAUDE`.
  Keep GL document numbers ≤ 10 chars (or expect truncation).
- **Account entry flow (GL grid):** focus account cell → a `...` lookup button appears →
  opens "Account Lookup" (รหัสบัญชี / ชื่อบัญชี / ประเภทบัญชี); double-click selects and
  auto-fills ชื่อบัญชี. Then the row advances to เช็ค/ใบสำคัญ — **click the เดบิต/เครดิต cell
  directly** (typing right after account selection lands in เช็ค/ใบสำคัญ by mistake).
- **Save behavior:** ตกลง enabled only when ยอดรวม debit == credit. On success the form
  **resets to a blank entry** (no popup). On failure it shows an error and keeps the data —
  use form-reset-without-error as the success signal, then confirm in a report.
- **Verification path:** Reports → สมุดรายวันทั่วไป → แสดงแบบปกติ → set date range → ตาราง
  (on-screen grid). Filter the เลขที่เอกสาร column to the doc no. Note: the report prints the
  doc number only on a voucher's **first** line; later lines show blank เลขที่เอกสาร.
- Accounts used were generic asset accounts (a cash account and a bank account) from the test
  book's chart.
- Saved voucher confirmed: `19/6/2568 · TESTCLAUDE · <cash acct> เดบิต 100.00` (credit
  `<bank acct>` 100.00).

## Live SAVE test — 2026-06-19 (AR + AP, test company)

Saved one AR sale and one AP expense into the `test` book; both confirmed in-screen.

- **AR/AP auto-calc VAT and auto-fill the account.** Selecting the customer/vendor
  auto-populated the default GL account (`บัญชีแยกประเภท`), and after entering `จำนวนเงิน`, the
  app set `ภาษีขาย/ภาษีซื้อ = 7.00%`, `ยอดเงินสุทธิ`, and `รวมเป็นเงิน` automatically
  (100 → net 100, total 107). So prepare-entry should supply the before-VAT amount and let
  EASY-ACC compute VAT, OR validate that 7% reconciles to the total.
- **AR/AP show a Transactions History grid** that displays the saved row immediately
  (unlike GL, which needs a report). Use it for post-save readback/verification.
  - CD column = transaction-type code: `C` = เงินสด (cash), `I` = ลูกหนี้ (AR receivable),
    `A` = เจ้าหนี้ (AP).
- **เลขที่ใบกำกับ** accepted an 8-char invoice number fine.
- **Company-select list differs per module and is NOT safe to pick blindly.** It listed many
  books (and `... GL` variants), including live ones; the list scrolls by selection.
  **Always verify the `แฟ้มข้อมูล` data-folder path before clicking เลือก** — do not match on the
  display name alone (some are live books).
- Each module re-prompts for company when brought to front via open_application.
- A background monitor utility can steal focus and minimize the EASY-ACC windows;
  recover with open_application on the module exe.

> **Guard is per-company.** `company_guard` values are placeholders — set them to the actual
> target company (its `<COMPANY_NAME>`, `<DATA_FOLDER_PATH>`, and active period BE year) at run
> time, read from the live status bar.

## Live AR batch lessons — 2026-06-19 (61 cash-sale invoices)

From a real bulk AR session. The big ones:

- **Thai input language is the #1 blocker.** Customer/vendor codes are Thai-letter + number
  and only type correctly when the Windows layout is **Thai (Kedmanee)**. Under ENG, Thai
  keystrokes become `?` and the code is rejected. **Clipboard paste does not fix it.** The
  layout silently reverts to ENG after focus changes/interruptions, so re-verify before *every*
  party field. Treat an unresolved party name on readback as a hard stop. (Full guidance in
  `easy-acc-run-entry/references/cowork-entry-playbook.md` §0.5 and `error-recovery.md`.)
- **Prefer typing the party code + Tab over the `...` lookup.** The lookup from the entry field
  opens the master EDITOR (risky for bulk entry, slow); direct code entry is faster/safer once
  the layout is correct.
- **Cash vs receivable radio** (`รายการ I/C/H/T/X`) resets to `ลูกหนี้` on every reopen — set it
  per record; cash sale = `เงินสด` (CD `C`).
- **VAT reconciles to the satang**, including half-satang rounding (e.g. 1,121.50 → VAT 78.51 →
  1,200.01). prepare-entry should reconcile the computed grand total to the source total within
  0.01 rather than recomputing VAT itself.
- Date field auto-fills today — always overwrite with the document date.

## Evidence levels used in payloads

| Level | Meaning |
|---|---|
| `verified_ui` | Read back from the live EASY-ACC screen |
| `verified_source` | Taken directly from a source document field |
| `configured_map` | From this skill's field map / screenshots |
| `inferred` | Derived/guessed — never allowed for save |

## Open / blocked items (mirror of guide §21)

These remain UNVERIFIED until the databank or live testing confirms them. Mark any payload
that depends on them as `evidence_level: inferred` 