# Error Recovery

The actuator result (runner output on Path B, Claude's own readback on Path A) is the
authoritative UI state. On `blocked`, `needs_human`, or any mismatch: stop typing, do not
save, write an attempt log to `logs/attempted/`, and report.

## Stop conditions → action

| Stop condition | Action |
|---|---|
| EASY-ACC window not detected | Abort. Ask user to open EASY-ACC on the correct company. |
| Company name mismatch | Abort. Wrong company file open — do not proceed. |
| Path mismatch (status bar) | Abort. Wrong data folder. |
| Period mismatch vs document date | Abort. Ask user to change period or correct the date. |
| Screen id UNKNOWN | Abort. Navigate to the correct module screen, re-detect. |
| Field cannot be focused | Abort field group. Screenshot. Report which field. |
| Readback mismatch | Re-clear and retype once; if it still differs, abort + screenshot. |
| VAT/WHT/total mismatch | Abort. Re-run prepare-entry validation. |
| Duplicate risk high | Abort. Require human review. |
| Unexpected modal/popup | Abort. Screenshot. Do not dismiss blindly. Ask operator. |
| Print prompt after save | Do not assume — behavior unmapped (open item). Screenshot, ask. |
| No save confirmation detected | Treat as not saved. Do not retry blindly; verify in history grid. |

## Error dialog → action quick reference (observed live)

| Dialog text (Thai) | Meaning | Likely cause | Action |
|---|---|---|---|
| `รหัสลูกค้าไม่ถูกต้อง. คุณต้องการสร้างใหม่ไหม?` | Customer code invalid — create new? | Thai keystroke dropped (input layout = ENG → `?`), or a genuine typo | Click **No** (never create a master record). Re-set Thai (Kedmanee), clear field, re-key, Tab, confirm the name resolves. |
| `กรุณาใส่รหัสลูกค้า` | Please enter customer code | Party field empty — usually a dropped Thai keystroke earlier | Click **OK**. Re-set Thai layout, re-enter the code, and re-check the date didn't reset to today. |
| `วันที่บันทึกไม่ถูกต้อง หรือไม่อยู่ในงวดบัญชี` | Recording date invalid / outside the accounting period | Document date outside the book's active period | **Stop