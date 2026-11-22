"""Train intent + urgency classifiers from labelled ticket JSON.

Uses label fields and ticket text only through this script (CAP-10 / findings D5).
Does not print full ticket bodies.

Word + character TF-IDF improves robustness for non_fluent wording (fairness).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline


def _text(row: dict) -> str:
    return f"{row.get('subject') or ''}\n{row.get('body') or ''}".strip()


def _features() -> FeatureUnion:
    return FeatureUnion(
        [
            (
                "word",
                TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=20000),
            ),
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    max_features=15000,
                ),
            ),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CloudServe Assistant classifiers")
    parser.add_argument("--input", required=True, help="Path to labelled tickets JSON array")
    parser.add_argument("--output", required=True, help="Directory for classifier artifact")
    parser.add_argument(
        "--test-size",
        type=float,
        default=None,
        help="Override TRAIN_TEST_SIZE from .env",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override TRAIN_SEED from .env",
    )
    args = parser.parse_args()

    from src.config import get_settings

    settings = get_settings()
    test_size = args.test_size if args.test_size is not None else settings.train_test_size
    seed = args.seed if args.seed is not None else settings.train_seed

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise SystemExit("Input must be a non-empty JSON array of tickets")

    texts: list[str] = []
    intents: list[str] = []
    urgencies: list[str] = []
    for row in data:
        labels = row.get("labels") or {}
        intent = labels.get("intent")
        urgency = labels.get("urgency")
        if not intent or not urgency:
            continue
        texts.append(_text(row))
        intents.append(str(intent))
        urgencies.append(str(urgency))

    if len(texts) < 20:
        raise SystemExit(f"Need at least 20 labelled rows; got {len(texts)}")

    X_train, X_test, y_i_train, y_i_test, y_u_train, y_u_test = train_test_split(
        texts,
        intents,
        urgencies,
        test_size=test_size,
        random_state=seed,
        stratify=intents if len(set(intents)) > 1 else None,
    )

    intent_pipeline = Pipeline(
        [
            ("features", _features()),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    urgency_pipeline = Pipeline(
        [
            ("features", _features()),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )

    intent_pipeline.fit(X_train, y_i_train)
    urgency_pipeline.fit(X_train, y_u_train)

    print("=== Intent (held-out) ===")
    print(classification_report(y_i_test, intent_pipeline.predict(X_test), zero_division=0))
    print("=== Urgency (held-out) ===")
    print(classification_report(y_u_test, urgency_pipeline.predict(X_test), zero_division=0))

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "intent_pipeline": intent_pipeline,
        "urgency_pipeline": urgency_pipeline,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "source": str(Path(args.input).resolve()),
        "features": "word+char_wb",
    }
    dest = out / settings.classifier_filename
    joblib.dump(bundle, dest)
    print(f"Wrote {dest} (train={len(X_train)} test={len(X_test)})")


if __name__ == "__main__":
    main()
