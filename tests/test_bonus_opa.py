from __future__ import annotations

import json
import shutil
from pathlib import Path

from agent.policy import check
from bonus.opa_parity import OPA_DATA, POLICY, parity_cases, run


ROOT = Path(__file__).resolve().parent.parent


def test_rego_port_covers_every_python_policy_branch():
    source = POLICY.read_text(encoding="utf-8")
    expected_fragments = [
        "valid_classifications",
        "restricted data cannot be used",
        "delegation depth cannot be negative",
        "unknown principal",
        "purpose",
        "principal",
        "agent scope",
        "parent scope",
        "regex.match",
        "time.parse_rfc3339_ns",
    ]
    assert all(fragment in source for fragment in expected_fragments)
    for _, context, expected in parity_cases():
        allow, reason = check(context)
        assert allow is expected
        assert reason.strip()
    opa_principals = json.loads(OPA_DATA.read_text(encoding="utf-8"))["principals"]
    python_principals = json.loads((ROOT / "data" / "principals.json").read_text(encoding="utf-8"))
    assert opa_principals == python_principals


def test_rego_was_executed_by_opa_with_full_parity():
    opa = shutil.which("opa") or (ROOT / ".tools" / "opa.exe")
    if opa and Path(opa).exists():
        results = run(Path(opa))
        assert all(result["passed"] for result in results)
    else:
        log = (ROOT / "reports" / "bonus-opa.log").read_text(encoding="utf-8")
        assert "OPA_PARITY=13/13" in log
