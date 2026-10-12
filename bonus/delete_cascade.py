"""Delete a synthetic customer and linked tickets while preserving the ledger chain."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agent import ledger


ROOT = Path(__file__).resolve().parent.parent


def _replace(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def delete_customer(
    customer_id: str,
    customers_path: Path,
    corpus_dir: Path,
    ledger_path: Path,
) -> dict:
    if not ledger.verify(ledger_path):
        raise ValueError("refusing deletion because the input ledger does not verify")

    original_customers = customers_path.read_text(encoding="utf-8")
    customers = json.loads(original_customers)
    matches = [record for record in customers if record.get("customer_id") == customer_id]
    if len(matches) != 1:
        raise LookupError("customer must exist exactly once")

    ticket_ids = sorted(set(matches[0].get("related_tickets", [])))
    ticket_paths = [corpus_dir / f"ticket-{ticket_id:03d}.md" for ticket_id in ticket_ids]
    original_tickets = {path: path.read_text(encoding="utf-8") for path in ticket_paths if path.exists()}
    remaining = [record for record in customers if record.get("customer_id") != customer_id]
    target_hash = hashlib.sha256(customer_id.encode("utf-8")).hexdigest()
    args_hash = hashlib.sha256(
        json.dumps(
            {"customer_id_hash": target_hash, "related_tickets": ticket_ids},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    try:
        _replace(customers_path, json.dumps(remaining, ensure_ascii=False, indent=2) + "\n")
        for path in original_tickets:
            path.unlink()
        ledger.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "agent_id": "lab24-privacy-worker",
                "run_id": "delete-cascade",
                "tool": "delete_customer_cascade",
                "args_hash": args_hash,
                "classification": "restricted",
                "decision": "allow",
                "reason": f"deleted one synthetic customer and {len(original_tickets)} linked tickets",
            },
            ledger_path,
        )
        if not ledger.verify(ledger_path):
            raise RuntimeError("ledger failed verification after deletion")
    except Exception:
        _replace(customers_path, original_customers)
        for path, content in original_tickets.items():
            path.write_text(content, encoding="utf-8")
        raise

    return {
        "customer_id_hash": target_hash,
        "customers_removed": 1,
        "tickets_removed": len(original_tickets),
        "ledger_verify": True,
    }


def demo() -> dict:
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        customers = root / "customers.json"
        corpus = root / "corpus"
        audit = root / "ledger.jsonl"
        shutil.copy2(ROOT / "data" / "customers.json", customers)
        shutil.copytree(ROOT / "corpus", corpus)
        shutil.copy2(ROOT / "reports" / "ledger.jsonl", audit)
        before = ledger.verify(audit)
        result = delete_customer("KH-000001", customers, corpus, audit)
        result["ledger_before"] = before
        result["source_unchanged"] = (ROOT / "corpus" / "ticket-014.md").exists()
        return result


if __name__ == "__main__":
    print(json.dumps(demo(), sort_keys=True))
