#!/usr/bin/env python3
"""
preflight_check.py — Gate a payload before EASY-ACC UI entry.

Re-runs the prepare-entry validator, then enforces run-entry policy:
the payload must be ready_for_ui_input AND explicitly allow input.
Does NOT touch EASY-ACC. Pure standard library.

Usage:
    python preflight_check.py <payload.json> [--expect-company NAME] [--expect-period-be 2569]

Exit: 0 = cleared to attempt input, 1 = blocked.
"""

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATOR = os.path.normpath(
    os.path.join(HERE, "..", "..", "easy-acc-prepare-entry", "scripts", "validate_payload.py")
)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_payload", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv=None):
    ap = argparse.ArgumentParser(description="Preflight gate before EASY-ACC UI entry.")
    ap.add_argument("payload")
    ap.add_argument("--expect-company", default=None)
    ap.add_argument("--expect-period-be", type=int, default=None)
    args = ap.parse_args(argv)

    blockers = []

    try:
        with open(args.payload, encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"cleared": False, "blockers": [f"load: {e}"]},
                         ensure_ascii=False, indent=2))
        return 1

    try:
        validator = load_validator()
        vres = validator.validate(payload, args.expect_company, args.expect_period_be)
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"cleared": False, "blockers": [f"validator error: {e}"]},
                         ensure_ascii=False, indent=2))
        return 1

    if not vres["valid"]:
        blockers.append("payload failed validation")
    if not vres["ready_for_ui_input"]:
        blockers.append("payload not ready_for_ui_input")

    if payload.get("automation_status") != "ready_for_ui_input":
        blockers.append(f"automation_status={payload.get('automation_status')!r}")
    if not payload.get("validation", {}).get("passed"):
        blockers.append("validation.passed is not true")

    pol = payload.get("ui_input_policy", {}) or {}
    if not pol.get("allow_input"):
        blockers.append("ui_input_policy.allow_input is not true")
    if not payload.get("target_module"):
        blockers.append("target_module missing")
    if payload.get("target_screen_id") in (None, "UNKNOWN"):
        blockers.append("target_screen_id unknown")
    if payload.get("evidence_level") == "inferred":
        blockers.append("evidence_level is inferred")
    if (payload.get("duplicate_check", {}) or {}).get("risk_level") == "high":
        blockers.append("duplicate risk high")

    cleared = len(blockers) == 0
    print(json.dumps({
        "cleared": cleared,
        "actuator_hint": payload.get("actuator", "cowork_computer_use"),
        "mode": pol.get("mode", "dry_run"),
        "validation": vres,
        "blockers": blockers,
    }, ensure_ascii=False, indent=2))
    return 0 if cleared else 1


if __name__ == "__main__":
    sys.exit(main())
