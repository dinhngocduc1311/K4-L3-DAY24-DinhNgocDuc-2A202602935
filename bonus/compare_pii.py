"""Compare the required regex PII gate with a real GLiNER model."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import time
from pathlib import Path

from agent import pii


ROOT = Path(__file__).resolve().parent.parent
TESTSET = ROOT / "tests" / "vn_pii_testset.jsonl"
MODEL = "urchade/gliner_multi_pii-v1"
MODEL_REVISION = "1fcf13e85f4eef5394e1fcd406cf2ca9ea82351d"
LABEL_TO_TYPE = {
    "national id number": "VN_CCCD",
    "phone number": "VN_PHONE",
    "bank account number": "VN_BANK_ACCOUNT",
    "email address": "EMAIL",
}


def load_rows(path: Path = TESTSET) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def score(rows: list[dict], predictions: list[list[dict]]) -> dict:
    gold_count = pred_count = true_positive = 0
    for row, predicted in zip(rows, predictions, strict=True):
        gold = row["entities"]
        gold_count += len(gold)
        pred_count += len(predicted)
        matched = set()
        for entity in predicted:
            for index, expected in enumerate(gold):
                overlaps = (
                    entity["type"] == expected["type"]
                    and entity["start"] < expected["end"]
                    and expected["start"] < entity["end"]
                )
                if index not in matched and overlaps:
                    matched.add(index)
                    true_positive += 1
                    break
    return {
        "gold": gold_count,
        "pred": pred_count,
        "tp": true_positive,
        "precision": true_positive / pred_count if pred_count else 0.0,
        "recall": true_positive / gold_count if gold_count else 0.0,
    }


def regex_metrics(rows: list[dict]) -> dict:
    return score(rows, [pii.detect(row["text"]) for row in rows])


def gliner_metrics(rows: list[dict], model_name: str, revision: str, threshold: float) -> dict:
    from gliner import GLiNER

    model = GLiNER.from_pretrained(model_name, revision=revision)
    labels = list(LABEL_TO_TYPE)
    predictions = []
    for row in rows:
        entities = model.predict_entities(row["text"], labels, threshold=threshold)
        predictions.append([
            {
                "type": LABEL_TO_TYPE[entity["label"]],
                "start": entity["start"],
                "end": entity["end"],
            }
            for entity in entities
            if entity["label"] in LABEL_TO_TYPE
        ])
    return score(rows, predictions)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--revision", default=MODEL_REVISION)
    parser.add_argument("--threshold", type=float, default=0.3)
    args = parser.parse_args()
    rows = load_rows()
    started = time.perf_counter()
    result = {
        "dataset": str(TESTSET.relative_to(ROOT)).replace("\\", "/"),
        "dataset_sha256": hashlib.sha256(TESTSET.read_bytes()).hexdigest(),
        "examples": len(rows),
        "gliner_package": importlib.metadata.version("gliner"),
        "model": args.model,
        "model_revision": args.revision,
        "threshold": args.threshold,
        "regex": regex_metrics(rows),
        "gliner": gliner_metrics(rows, args.model, args.revision, args.threshold),
    }
    result["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
