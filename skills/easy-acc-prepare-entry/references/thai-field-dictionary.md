# Thai Field Dictionary

Use exact Thai labels when referring to UI fields. Labels below are confirmed against
`databank img/AR.png`, `AP.png`, and `GL.png`.

## AR Transaction Entry — `UI-AR-TRANSACTION-ENTRY-v1`

Radio group label: `รายการ (I/C/H/T/X):` — options: `ลูกหนี้` · `เงินสด` · `เช็ค` · `บัตรเครดิต` · `อื่นๆ`

| Field ID | Thai label | Meaning | Required |
|---|---|---|---|
| `transaction_radio` | รายการ (I/C/H/T/X) | AR transaction type radio | Yes |
| `document_date` | วันที่ | Transaction date | Yes |
| `tax_invoice_no` | เลขที่ใบกำกับ | Tax invoice / document number | Yes for VAT sale |
| `customer_code` | รหัสลูกค้า | Customer code (lookup `...`) | Yes |
| `account_code` | บัญชีแยกประเภท | Revenue / AR-related account (lookup `...`) | Yes |
| `amount_before_vat` | จำนวนเงิน | Amount (basis company-specific, verify) | Yes |
| `discount` | ส่วนลดพิเศษ | Discount | Optional, default 0 |
| `output_vat` | ภาษีขาย | Output VAT | Required for VAT sale |
| `net_total` | ยอดเงินสุทธิ | Net subtotal (display, computed) | Readback only |
| `grand_total` | รวมเป็นเงิน | Grand total (display, computed) | Readback only |
| `due_date` | วันที่ครบกำหนด | Due date | Required for credit sale |
| `salesperson_code` | รหัสพนักงานขาย | Salesperson | Optional |
| `note` | หมายเหตุ | Note | Recommended |

History grid columns: `วันที่` · `CD` · `เลขที่ใบกำกับ` · `รหัสบัญชี` · `รหัสลูกค้า` · `รวมเป็นเงิน` · `หมายเหตุ`

## AP Transaction Entry — `UI-AP-TRANSACTION-ENTRY-v1`

Radio group label: `รายการ (A/C/H):` — options: `เจ้าหนี้` · `เงินสด` · `เช็ค`

| Field ID | Thai label | Meaning | Required |
|---|---|---|---|
| `transaction_radio` | รายการ (A/C/H) | AP transaction type radio | Yes |
| `document_date` | วันที่ | Transaction date | Yes |
| `tax_invoice_no` | เลขที่ใบกำกับ | Supplier tax invoice / document number | Yes for VAT purchase |
| `vendor_code` | รหัสเจ้าหนี้ | Creditor/vendor code (lookup `...`) | Yes |
| `account_code` | บัญชีแยกประเภท | Expense / payable account (lookup `...`) | Yes |
| `amount_before_vat` | จำนวนเงิน | Amount (basis company-specific, verify) | Yes |
| `discount` | ส่วนลดพิเศษ | Discount | Optional, default 0 |
| `input_vat` | ภาษีซื้อ | Input VAT | Required if VAT claim |
| `input_vat_sequence_no` | เลขที่จัดลำดับภาษี | VAT sequence number (lookup `...`) | Required if company tracks it |
| `net_total` | ยอดเงินสุทธิ | Net subtotal (display, computed) | Readback only |
| `grand_total` | รวมเป็นเงิน | Grand total (display, computed) | Readback only |
| `due_date` | วันที่ครบกำหนด | Due date | Required for credit purchase |
| `note` | หมายเหตุ | Note | Recommended |

History grid columns: `วันที่` · `CD` · `เลขที่ใบกำกับ` · `รหัสเจ้าหนี้` · `รหัสบัญชี` · `รวมเป็นเงิน` · `หมายเหตุ`

> The AP capture shows **no WHT field** on this screen. WHT/retention may live on a deeper
> detail screen — unconfirmed (see `source-index.md` item 9). Do not assume a screen field.

## GL Transaction Entry — `UI-GL-TRANSACTION-ENTRY-v1`

| Field ID | Thai label | Meaning | Required |
|---|---|---|---|
| `journal_book_code` | สมุดรายวันทั่วไป | Journal book code (lookup `...`, default `00`) | Yes |
| `document_date` | วันที่ | Voucher date | Yes |
| `document_no` | เลขที่เอกสาร | Voucher number | Yes |
| `description` | คำอธิบาย | Journal description | Yes |

Grid columns (one row per line):

| Field ID | Thai label | Meaning | Required |
|---|---|---|---|
| `account_code` | รหัสบัญชี | Account code | Yes |
| `account_name` | ชื่อบัญชี | Account name | Readback validation |
| `voucher_ref` | เช็ค/ใบสำคัญ | Cheque/voucher ref | Optional |
| `line_date` | ลงวันที่ | Line date | Optional / use document date |
| `debit` | เดบิต | Debit amount | Per line |
| `credit` | เครดิต | Credit amount | Per line |

Footer: `ยอดรวม:` shows total debit and total credit (must balance).

## Date format

EASY-ACC displays Thai Buddhist-era (BE) dates as `D/M/YYYY` (e.g. `18/6/2569`).
Normalize to `DD/MM/YYYY` BE for UI display. BE = AD + 543.
