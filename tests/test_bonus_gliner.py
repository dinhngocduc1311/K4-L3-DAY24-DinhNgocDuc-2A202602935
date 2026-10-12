from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bonus.compare_pii import load_rows, regex_metrics, score


ROOT = Path(__file__).resolve().parent.parent


def test_shared_metric_and_regex_baseline():
    rows = load_rows()
    metrics = regex_metrics(rows)
    assert len(rows) == 120
    assert metrics == {"gold": 118, "pred": 118, "tp": 118, "precision": 1.0, "recall": 1.0}
    assert score(rows[:1], [rows[0]["entities"]]) == {
        "gold": 1, "pred": 1, "tp": 1, "precision": 1.0, "recall": 1.0
    }


def test_real_gliner_run_is_recorded_for_the_same_testset():
    result = json.loads((ROOT / "reports" / "bonus-gliner.log").read_text(encoding="utf-8"))
    testset = ROOT / result["dataset"]
    assert result["dataset"] == "tests/vn_pii_testset.jsonl"
    assert result["dataset_sha256"] == hashlib.sha256(testset.read_bytes()).hexdigest()
    assert result["examples"] == 120
    assert result["model"] == "urchade/gliner_multi_pii-v1"
    assert result["model_revision"] == "1fcf13e85f4eef5394e1fcd406cf2ca9ea82351d"
    assert result["regex"]["gold"] == result["gliner"]["gold"] == 118
    assert 0.0 <= result["gliner"]["precision"] <= 1.0
    assert 0.0 <= result["gliner"]["recall"] <= 1.0
