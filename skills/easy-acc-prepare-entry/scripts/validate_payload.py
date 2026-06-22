#!/usr/bin/env python3
"""
validate_payload.py — Pre-UI validator for EASY-ACC transaction payloads.

Pure standard library (no external deps) so it runs anywhere Python 3.8+ is available.
It does NOT touch EASY-ACC. It only checks a prepared JSON payload before UI automation.

Usage:
    python validate_payload.py <payload.json>
    python validate_payload.py <payload.json> --expect-company "<COMPANY>" --expect-period-be 2569

Exit code 0 = valid & ready_for_ui_input, 1 = valid but not ready, 2 = invalid/errors.
"""

import argparse
import json
import re
import sys

VAT_RATE = 0.07
AMOUNT_TOL = 0.01
VAT_TOL = 0.01

SUPPORTED_MODULES = {"AR", "AP", "GL", "BI"}
SUPPORTED_SCREENS = {
    "UI-AR-TRANSACTION-ENTRY-v1",
    "UI-AP-TRANSACTION-ENTRY-v1",
    "UI-GL-TRANSACTION-ENTRY-v1",
    "UI-BI-BILLING-ENTRY-v1",
}
DATE_RE = re.compile(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$")


def parse_be_date(s):
    """Return (day, month, year) for a D/M/YYYY string, or None if unparseable."""
    if not isinstance(s, str):
        return None
    m = DATE_RE.match(s)
    if not m:
        return None
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= d <= 31 and 1 <= mo <= 12):
        return None
    return d, mo, y


def approx(a, b, tol):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def validate(payload, expect_company=None, expect_period_be=None):
    checks, errors, warnings = [], [], []

    def ok(name):
        checks.append(name)

    def err(name, msg):
        errors.append({"check": name, "message": msg})

    def warn(name, msg):
        warnings.append({"check": name, "message": msg})

    # schema_version_present
    if payload.get("schema_version") == "easy_acc_transaction_v1":
        ok("schema_version_present")
    else:
        err("schema_version_present", "schema_version must be 'easy_acc_transaction_v1'")

    module = payload.get("target_module")
    screen = payload.get("target_screen_id")
    fields = payload.get("fields", {}) or {}
    calc = payload.get("calculations", {}) or {}
    ttype = payload.get("transaction_type")

    # target_module_supported
    if module in SUPPORTED_MODULES:
        ok("target_module_supported")
    else:
        err("target_module_supported", f"unsupported target_module: {module!r}")

    # target_screen_id_supported
    if screen in SUPPORTED_SCREENS:
        ok("target_screen_id_supported")
        if screen == "UI-BI-BILLING-ENTRY-v1":
            warn("bi_blocked", "BI/Billing screen map is not yet captured (blocked).")
    else:
        err("target_screen_id_supported", f"unsupported target_screen_id: {screen!r}")

    # document_date_valid_be_or_ad + period_matches_date
    is_gl = module == "GL"
    date_str = fields.get("document_date")
    parsed = parse_be_date(date_str)
    if parsed:
        ok("document_date_valid_be_or_ad")
        _, _, year = parsed
        if year < 2400:
            warn("date_year_ad", f"document_date year {year} looks AD; confirm BE conversion.")
        if expect_period_be is not None:
            if year == expect_period_be:
                ok("period_matches_date")
            else:
                err("period_matches_date",
                    f"document_date year {year} != expected period {expect_period_be}")
    else:
        err("document_date_valid_be_or_ad", f"unparseable/ambiguous date: {date_str!r}")

    # company guard
    if expect_company is not None:
        cg = (payload.get("company_guard") or {}).get("expected_company_name", "")
        if expect_company.lower() in (cg or "").lower():
            ok("company_guard_matches")
        else:
            warn("company_guard_matches",
                 f"expected company {expect_company!r} not found in company_guard")

    # party_code_present + document_number_present_when_required
    if is_gl:
        ok("party_code_present")  # N/A for GL
        if fields.get("document_no"):
            ok("document_number_present_when_required")
        else:
            err("document_number_present_when_required", "GL document_no missing")
    else:
        party = fields.get("customer_code") if module == "AR" else fields.get("vendor_code")
        if party:
            ok("party_code_present")
        else:
            err("party_code_present", f"{module} party code missing")
        vat = fields.get("output_vat" if module == "AR" else "input_vat")
        if vat:  # VAT transaction needs a tax invoice number
            if fields.get("tax_invoice_no"):
                ok("document_number_present_when_required")
            else:
                err("document_number_present_when_required",
                    "tax_invoice_no required for VAT transaction")
        else:
            ok("document_number_present_when_required")

    # amounts_are_numeric + vat_reconciles
    if is_gl:
        ok("amounts_are_numeric")
        ok("vat_reconciles")  # N/A
    else:
        before = fields.get("amount_before_vat")
        vat = fields.get("output_vat" if module == "AR" else "input_vat", 0) or 0
        if isinstance(before, (int, float)):
            ok("amounts_are_numeric")
            if vat:
                expected_vat = round(before * VAT_RATE, 2)
                if approx(vat, expected_vat, VAT_TOL):
                    ok("vat_reconciles")
                else:
                    err("vat_reconciles",
                        f"VAT {vat} != expected {expected_vat} (7% of {before})")
                total = calc.get("computed_total")
                if total is not None and not approx(total, before + vat, AMOUNT_TOL):
                    err("total_reconciles",
                        f"computed_total {total} != {before}+{vat}={before + vat}")
                else:
                    ok("total_reconciles")
            else:
                ok("vat_reconciles")  # non-VAT case
        else:
            err("amounts_are_numeric", "amount_before_vat is missing or non-numeric")

    # wht_reconciles_when_required
    if calc.get("wht_required"):
        base = calc.get("wht_base")
        rate = calc.get("wht_rate")
        amt = calc.get("wht_amount")
        if base and rate is not None and amt is not None and approx(amt, round(base * rate, 2), AMOUNT_TOL):
            ok("wht_reconciles_when_required")
        else:
            err("wht_reconciles_when_required",
                f"WHT does not reconcile: base={base} rate={rate} amount={amt}")
    else:
        ok("wht_reconciles_when_required")

    # gl_balanced_when_gl
    if is_gl:
        lines = fields.get("lines", []) or []
        tot_d = round(sum(float(l.get("debit", 0) or 0) for l in lines), 2)
        tot_c = round(sum(float(l.get("credit", 0) or 0) for l in lines), 2)
        if lines and approx(tot_d, tot_c, AMOUNT_TOL) and tot_d > 0:
            ok("gl_balanced_when_gl")
        else:
            err("gl_balanced_when_gl", f"GL not balanced: debit={tot_d} credit={tot_c}")
    else:
        ok("gl_balanced_when_gl")

    # duplicate_keys_generated
    dup = payload.get("duplicate_check", {}) or {}
    if dup.get("keys"):
        ok("duplicate_keys_generated")
        if dup.get("risk_level") == "high":
            err("duplicate_risk", "duplicate risk is high — blocked")
        elif dup.get("risk_level") in (None, "unknown"):
            warn("duplicate_risk", "duplicate risk unknown — review before save")
    else:
        warn("duplicate_keys_generated", "no duplicate keys generated")

    # ui_policy_safe
    pol = payload.get("ui_input_policy", {}) or {}
    if pol.get("allow_save") and not pol.get("requires_human_confirmation", True):
        warn("ui_policy_safe", "allow_save true without requires_human_confirmation")
    else:
        ok("ui_policy_safe")

    # evidence level gate
    if payload.get("evidence_level") == "inferred":
        warn("evidence_level", "evidence_level is 'inferred' — not eligible for save")

    valid = len(errors) == 0
    status = payload.get("automation_status")
    ready = (
        valid
        and status == "ready_for_ui_input"
        and dup.get("risk_level") != "high"
        and payload.get("evidence_level") != "inferred"
    )
    return {
        "valid": valid,
        "ready_for_ui_input": ready,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate an EASY-ACC transaction payload.")
    ap.add_argument("payload", help="path to payload .json")
    ap.add_argument("--expect-company", default=None)
    ap.add_argument("--expect-period-be", type=int, default=None)
    args = ap.parse_args(argv)

    try:
        with open(args.payload, encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"valid": False, "ready_for_ui_input": False,
                          "errors": [{"check": "load", "message": str(e)}]},
                         ensure_ascii=False, indent=2))
        return 2

    result = validate(payload, args.expect_company, args.expect_period_be)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["valid"]:
        return 2
    return 0 if result["ready_for_ui_input"] else 1


if __name__ == "__main__":
    sys.exit(main())
