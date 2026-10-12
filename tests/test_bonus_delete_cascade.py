from __future__ import annotations

import json
import shutil

import pytest

from agent import ledger
from bonus.delete_cascade import delete_customer


def _entry() -> dict:
    return {
        "ts": "2026-10-12T00:00:00+00:00",
        "agent_id": "test",
        "run_id": "before-delete",
        "tool": "search_docs",
        "args_hash": "0" * 64,
        "classification": "internal",
        "decision": "allow",
        "reason": "valid fixture entry",
    }


def test_delete_cascades_to_tickets_and_preserves_ledger(tmp_path):
    root = tmp_path / "copy"
    corpus = root / "corpus"
    root.mkdir()
    shutil.copy2("data/customers.json", root / "customers.json")
    shutil.copytree("corpus", corpus)
    audit = root / "ledger.jsonl"
    ledger.append(_entry(), audit)

    original = json.loads((root / "customers.json").read_text(encoding="utf-8"))[0]
    sensitive_values = [
        original[key] for key in ("customer_id", "name", "cccd", "phone", "bank_account", "email")
    ]
    result = delete_customer(original["customer_id"], root / "customers.json", corpus, audit)

    remaining = (root / "customers.json").read_text(encoding="utf-8")
    remaining += "\n" + "\n".join(path.read_text(encoding="utf-8") for path in corpus.glob("*.md"))
    assert all(value not in remaining for value in sensitive_values)
    assert not (corpus / "ticket-014.md").exists()
    assert not (corpus / "ticket-015.md").exists()
    assert (corpus / "ticket-016.md").exists()
    assert result["customers_removed"] == 1
    assert result["tickets_removed"] == 2
    assert original["customer_id"] not in json.dumps(result)
    assert ledger.verify(audit) is True
    last = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
    assert last["tool"] == "delete_customer_cascade"
    assert last["reason"]


def test_delete_rejects_unknown_customer_without_mutation(tmp_path):
    customers = tmp_path / "customers.json"
    shutil.copy2("data/customers.json", customers)
    audit = tmp_path / "ledger.jsonl"
    ledger.append(_entry(), audit)
    before = customers.read_bytes()
    with pytest.raises(LookupError):
        delete_customer("KH-NOT-FOUND", customers, tmp_path, audit)
    assert customers.read_bytes() == before
    assert ledger.verify(audit) is True
