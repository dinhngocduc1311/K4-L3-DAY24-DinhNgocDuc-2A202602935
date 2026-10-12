"""Run the Rego port through OPA and compare it with agent.policy."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from dataclasses import asdict
from pathlib import Path

from agent.policy import PolicyContext, check


ROOT = Path(__file__).resolve().parent.parent
POLICY = Path(__file__).with_name("policy.rego")
OPA_DATA = Path(__file__).with_name("opa_data.json")
FUTURE = "2099-01-01T00:00:00+00:00"
EXPIRED = "2000-01-01T00:00:00+00:00"


def parity_cases() -> list[tuple[str, PolicyContext, bool]]:
    base = {
        "data_classification": "internal",
        "request_purpose": "summarize-tickets",
        "agent_owner": "lab24-agent/run-a",
        "delegation_depth": 0,
        "egress_enabled": False,
        "principal_id": "support_l1",
        "requested_tool": "search_docs",
        "agent_scopes": ("search_docs",),
        "parent_scopes": (),
        "expires_at": FUTURE,
    }

    def context(**changes) -> PolicyContext:
        return PolicyContext(**(base | changes))

    return [
        ("valid direct call", context(), True),
        ("invalid classification", context(data_classification="secret"), False),
        ("restricted egress", context(data_classification="restricted", egress_enabled=True), False),
        ("negative delegation", context(delegation_depth=-1), False),
        ("unknown principal", context(principal_id="unknown"), False),
        ("purpose denied", context(request_purpose="privacy-audit"), False),
        ("principal tool denied", context(requested_tool="read_customer", agent_scopes=("read_customer",)), False),
        ("agent scope denied", context(agent_scopes=()), False),
        (
            "parent scope denied",
            context(
                principal_id="dpo",
                requested_tool="read_customer",
                request_purpose="support-reply",
                data_classification="restricted",
                delegation_depth=1,
                agent_scopes=("read_customer",),
                parent_scopes=("search_docs",),
            ),
            False,
        ),
        (
            "valid delegated call",
            context(
                principal_id="dpo",
                requested_tool="read_customer",
                request_purpose="support-reply",
                data_classification="restricted",
                delegation_depth=1,
                agent_scopes=("read_customer",),
                parent_scopes=("read_customer",),
            ),
            True,
        ),
        ("expired authority", context(expires_at=EXPIRED), False),
        ("malformed expiry", context(expires_at="not-a-time"), False),
        ("expiry without UTC offset", context(expires_at="2099-01-01T00:00:00"), False),
    ]


def _rego_decision(opa: Path, context: PolicyContext) -> dict:
    with tempfile.TemporaryDirectory() as folder:
        input_path = Path(folder) / "input.json"
        input_path.write_text(json.dumps(asdict(context)), encoding="utf-8")
        completed = subprocess.run(
            [
                str(opa), "eval", "--format=json", "--fail", "--strict-builtin-errors",
                "-d", str(POLICY), "-d", str(OPA_DATA), "-i", str(input_path),
                "data.lab24.decision",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    return json.loads(completed.stdout)["result"][0]["expressions"][0]["value"]


def run(opa: Path) -> list[dict]:
    subprocess.run([str(opa), "fmt", "--fail", str(POLICY)], check=True, capture_output=True)
    subprocess.run([str(opa), "check", "--strict", str(POLICY)], check=True, capture_output=True)
    results = []
    for name, context, expected in parity_cases():
        python_allow, python_reason = check(context)
        rego = _rego_decision(opa, context)
        passed = (
            python_allow is expected
            and rego.get("allow") is expected
            and bool(python_reason.strip())
            and bool(str(rego.get("reason", "")).strip())
        )
        results.append({
            "case": name,
            "expected": expected,
            "python_allow": python_allow,
            "rego_allow": rego.get("allow"),
            "reasons_non_empty": bool(python_reason.strip() and str(rego.get("reason", "")).strip()),
            "passed": passed,
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--opa", type=Path, default=shutil.which("opa"))
    args = parser.parse_args()
    if args.opa is None or not args.opa.exists():
        parser.error("OPA binary not found; pass --opa PATH")

    version = subprocess.run(
        [str(args.opa), "version"], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout.splitlines()[0]
    results = run(args.opa)
    print(f"OPA {version}")
    for result in results:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    passed = sum(result["passed"] for result in results)
    print(f"OPA_PARITY={passed}/{len(results)}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
