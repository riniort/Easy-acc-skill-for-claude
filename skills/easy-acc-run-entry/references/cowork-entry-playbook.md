# Cowork Computer-Use Entry Playbook (validated live 2026-06-19)

Step-by-step UI flow for Path A (Cowork computer use), confirmed end-to-end against the live
EASY-ACC app on the `test` company. Follow this exactly; every step here was observed working.

## 0. Launch & grant

- Module processes (under `G:\Program Files\ECACC32\`): GL = `glmain32.exe`, AR = `armain32.exe`,
  AP = `apmain32.exe`. The computer-use access grant resolves these only by the **running .exe
  basename** — not the window title or display name. If a module isn't running, launch it from
  the ECACC32 folder first, then request access to its `.exe`.
- Bringing a module forward (open_application) re-shows the **company selector** each time.

## 0.5 Thai input language — PREFLIGHT (critical, AR/AP)

Customer/vendor codes are Thai-letter + number (e.g. `น 102`, `พ 601`, `อ 115`). They only type
correctly when the **Windows input language is Thai (Kedmanee)**. This is the single biggest
blocker for AR/AP automation.

- **Symptom of wrong layout:** under ENG, a Thai keystroke renders as `?` (e.g. `? 102`), and
  EASY-ACC pops `รหัสลูกค้าไม่ถูกต้อง. คุณต้องการสร้างใหม่ไหม?` (invalid code — create new?).
  Answer **No** — never create a master record.
- **Clipboard paste does NOT fix it** (`write_clipboard` + Ctrl+V still yields `?`). The failure
  is at the keystroke-injection layer. Thai layout is the only fix.
- Thai layout is safe for the **whole form** — digits, `/` in dates, and Latin `IV…`/note codes
  all still type correctly while Thai is active.
- **The layout silently reverts to ENG** after focus changes, app switches, or `Ipsmonitor`
  interrupts. So **re-verify before *every* party-code field**, not just once per session.

How to set/verify:

- Verify by zooming the taskbar tray language chip (`ENG` vs `ไทย`).
- Switch by **clicking the tray chip → choosing "ไทย Thai - Kedmanee"**. `Alt+Shift` did NOT
  switch on the live machine — do not rely on the hotkey.
- **Failure detection (hard stop):** after typing a party code and Tab, the party **name must
  auto-fill**. If the name is blank, the field shows `?`, or the invalid-code dialog appears,
  the layout dropped — dismiss with No, re-set Thai, clear the field, re-key. **Never save a
  party code that did not resolve to a name on readback.**

## 1. Select the company — VERIFY THE PATH

- Dialog title `Select Directory` / `เลือกแฟ้มข้อมูลกิจการ`. Columns: `ชื่อกิจการ` | `แฟิมข้อมูล`.
- **Match on the data-folder path, never the display name.** The list mixes test and live books
  (e.g. a live one at `M:\APP backup (live)\ECA\TEST`). The list order differs per module and
  scrolls by selection — scroll until the exact target row is visible, click it, confirm the
  path, then click `เลือก` (Select).
- Confirm the status bar after load: `Company` (top-right), `Period:`, `Path:`.

## 2. Open Transaction Entry

- Click the first toolbar button (tooltip `สมุดรายวันทั่วไป` for GL / `บันทึกรายการประจำวัน`).
- Verify the dialog: title `Transaction Entry`, correct module radio, field labels per
  `screen-state-map.md`.

## 3. Date — must be inside the active period

- The form auto-fills `วันที่` with **today**, which is often outside the active period.
- Saving an out-of-period date raises: `วันที่บันทึกไม่ถูกต้อง หรือไม่อยู่ในงวดบัญชี`.
- Click the date field → `Ctrl+A` → type a date inside the period (e.g. period `1/1/2568` →
  use a `2568` date) → `Tab`.

## 4. Header fields

- `เลขที่เอกสาร` (GL) / `เลขที่ใบกำกับ` (AR/AP): type the doc/invoice number. **GL เลขที่เอกสาร
  max length = 10 chars** (longer is silently truncated).
- GL also: `คำอธิบาย` (description).

## 4.5 Transaction radio (AR/AP)

- The radio (`รายการ I/C/H/T/X`) **resets to `ลูกหนี้` every time the entry form reopens** — set
  it on every record. For a **cash sale** choose `เงินสด` (history CD = `C`); `ลูกหนี้` = `I`.
- Cash sales still take a customer code and still auto-fill name + account.

## 5. Party + account (AR/AP) — prefer typing the code

- **Ensure Thai layout is active first (§0.5).**
- **Prefer type-the-code + Tab over the `...` lookup.** Type the party code directly into
  `รหัสลูกค้า` (AR) / `รหัสเจ้าหนี้` (AP) → `Tab`. The `...` lookup reached from the entry field
  opens the **customer/vendor master EDITOR** (Edit Customer), which is risky for bulk entry and
  slow (long master list) — avoid it for routine posting.
- On a valid code + Tab, EASY-ACC **auto-fills the party name** (the readback anchor) and the
  default GL account `บัญชีแยกประเภท` (e.g. customers defaulted to `401 ขายสินค้า` on the live
  book). **Read the account back and override only if it differs from the intended account.**
- **Hard stop:** if the name does not populate after Tab, do not continue — the Thai layout
  almost certainly dropped (§0.5). Dismiss any dialog with No, re-set Thai, re-key.

## 6. Amounts — let EASY-ACC compute VAT (AR/AP)

- Type `จำนวนเงิน` (before-VAT amount) → `Tab`. The app auto-sets `ภาษีขาย`/`ภาษีซื้อ = 7.00%`,
  `ยอดเงินสุทธิ`, and `รวมเป็นเงิน` (100 → net 100, total 107). Supply before-VAT; reconcile,
  don't re-type VAT.

## 7. GL grid lines — account lookup + amount-cell quirk

- Focus the row's `รหัสบัญชี` cell → press `Return` → a `...` lookup appears → click it →
  Account Lookup opens (`รหัสบัญชี`/`ชื่อบัญชี`/`ประเภทบัญชี`) → double-click to select;
  `ชื่อบัญชี` auto-fills.
- **Quirk:** after selecting the account, focus jumps to `เช็ค/ใบสำคัญ`. Typing the amount
  immediately lands there by mistake. Instead, **click the `เดบิต` (or `เครดิต`) cell
  directly**, verify it's selected (zoom), then type the amount.
- `Return` commits the line and advances to the next row.
- A GL journal must balance: footer `ยอดรวม` debit must equal credit before `ตกลง` enables.

## 8. Read back, then save

- Re-read every field/line (zoom). Confirm totals.
- `ตกลง` (Save) is enabled only when the entry is valid/balanced. Click it as a discrete final
  step. **Do not use Enter to save.**
- **Success signal:** the form **resets to blank with no popup**. A failure instead shows an
  error dialog and keeps the data. AR/AP also show the saved row immediately in the
  **Transactions History** grid (CD = `I` for AR ลูกหนี้, `A` for AP เจ้าหนี้); GL needs a report.

## 9. Verify (GL)

- Reports → `สมุดรายวันทั่วไป` → `แสดงแบบปกติ` → set the date range to cover the entry → `ตาราง`
  (on-screen grid). Filter the `เลขที่เอกสาร` column to the doc no. Note: the report prints the
  doc number only on a voucher's **first** line; later lines show blank `เลขที่เอกสาร`.

## Recovery notes

- A monitor utility (`Ipsmonitor`) can steal focus and minimize the EASY-ACC windows; recover
  with open_application on the module exe.
- On any unexpected popup/modal, stop and surface it — do not dismiss blindly.
