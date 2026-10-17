"""Opt-in live extraction evaluation; structural scores require semantic adjudication."""

import argparse
import json
import time
from collections import Counter
from pathlib import Path
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field, TypeAdapter

from app.api.schemas import Contract, Note
from app.domain.extraction import PROMPT_VERSION, ExtractionError, OpenAIExtractor


class Source(Contract):
    participant: int = Field(ge=1, le=4)
    text: Note


class Gold(Contract):
    source: int = Field(ge=0)
    kind: Literal["desire", "concern", "constraint", "question", "suggestion"]
    meaning: Note


class Case(Contract):
    id: str
    split: Literal["development", "heldout"]
    sources: list[Source] = Field(min_length=1)
    gold: list[Gold]


def cases():
    path = Path(__file__).resolve().parents[1] / "evaluation/preferences.json"
    records = TypeAdapter(list[Case]).validate_json(path.read_text())
    if len({case.id for case in records}) != len(records):
        raise ValueError("Duplicate case IDs")
    for case in records:
        if any(gold.source >= len(case.sources) for gold in case.gold):
            raise ValueError("Gold reference outside source list")
    return records


def payload_for(case):
    return {
        "goal": "Choose our team project",
        "existing_interpretations": [],
        "new_sources": [
            {
                "source_id": str(uuid5(NAMESPACE_URL, f"feedbackform:{case.id}:{index}")),
                "participant_id": str(
                    uuid5(NAMESPACE_URL, f"feedbackform:person:{source.participant}")
                ),
                "kind": "idea_span",
                "text": source.text,
            }
            for index, source in enumerate(case.sources)
        ],
    }


def structural_score(case, payload, output):
    sources = {source["source_id"]: source for source in payload["new_sources"]}
    valid = all(
        signal.source_id in sources
        and signal.participant_id == sources[signal.source_id]["participant_id"]
        and signal.quote in sources[signal.source_id]["text"]
        for signal in output.preferences
    )
    expected = Counter(
        (payload["new_sources"][gold.source]["source_id"], gold.kind) for gold in case.gold
    )
    predicted = Counter((signal.source_id, signal.kind) for signal in output.preferences)
    return {
        "valid_attribution_and_quotes": valid,
        "source_kind_count_matches": sum((expected & predicted).values()),
        "expected_signal_count": sum(expected.values()),
        "predicted_signal_count": sum(predicted.values()),
        "semantic_review": "pending",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--split", choices=["development", "heldout"], default="development")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = cases()
    if args.validate_only:
        print(f"Validated {len(records)} synthetic cases; no model calls or quality measurement.")
        return
    if args.output is None:
        parser.error("Live evaluation requires --output for the adjudication artifact")
    extractor = OpenAIExtractor()
    if not extractor.configured:
        parser.error("Set OPENAI_API_KEY and OPENAI_MODEL on the server first")
    # Exclusive creation prevents accidental replacement of an earlier benchmark.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as destination:
        for case in records:
            if case.split != args.split:
                continue
            started = time.monotonic()
            payload = payload_for(case)
            row = {
                "prompt_version": PROMPT_VERSION,
                "case_id": case.id,
                "split": case.split,
                "model": extractor.model,
                "gold": [gold.model_dump() for gold in case.gold],
            }
            try:
                output, usage = extractor.extract(payload)
                row.update(
                    output=output.model_dump(),
                    usage=usage,
                    structural=structural_score(case, payload, output),
                )
            except ExtractionError as exc:
                row["error_code"] = str(exc)
            row["duration_ms"] = int((time.monotonic() - started) * 1000)
            destination.write(json.dumps(row) + "\n")
            destination.flush()
    print(f"Saved predictions for manual adjudication to {args.output}")


if __name__ == "__main__":
    main()
