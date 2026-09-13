"""Run the return-reason classifier against the hand-labelled evaluation set."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import anthropic

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = PROJECT_ROOT / "n8n-workflows" / "classifier_prompt.md"
DATASET_PATH = PROJECT_ROOT / "eval" / "dataset.jsonl"
RESULTS_PATH = PROJECT_ROOT / "eval" / "results.md"
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
MAX_CASES_PER_RUN = 30
MAX_TOKENS = 128
CATEGORIES = (
    "Niezgodność z opisem lub zdjęciem",
    "Wada jakościowa, uszkodzenie fabryczne",
    "Uszkodzenie w transporcie",
    "Błędna wysyłka, nie ten produkt",
    "Niedopasowanie, rozmiar, kolor, dopasowanie",
    "Zmiana decyzji klienta",
    "Opóźniona dostawa, zamówienie nieaktualne",
    "Inne, nieokreślone",
)


def load_dataset() -> list[dict[str, str]]:
    records = [json.loads(line) for line in DATASET_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(records) != MAX_CASES_PER_RUN:
        raise ValueError(f"Expected exactly {MAX_CASES_PER_RUN} eval cases, got {len(records)}")
    return records


def render_prompt(template: str, record: dict[str, str]) -> str:
    return template.replace("{{reason_text}}", record["reason_text"]).replace(
        "{{condition_note}}", record["condition_note"]
    )


def parse_classifier_response(response_text: str) -> dict[str, Any]:
    candidate = response_text.strip()
    candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate, flags=re.IGNORECASE)
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"Classifier did not return a JSON object: {response_text!r}")
    result = json.loads(candidate[start : end + 1])
    category = result.get("category")
    confidence = result.get("confidence")
    if category not in CATEGORIES:
        raise ValueError(f"Unknown category: {category!r}")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError(f"Invalid confidence: {confidence!r}")
    return {"category": category, "confidence": float(confidence)}


def classify(client: anthropic.Anthropic, prompt: str) -> dict[str, Any]:
    # Cost contract: Claude Haiku 4.5 at $1/M input and $5/M output; max 30 calls/run;
    # max $0.041/run using <=700 input tokens + 128 output tokens per call;
    # provider hard cap: Anthropic workspace budget <=$1/month, configured manually;
    # concurrency 1; retries 0; no amplifier path or idempotent mutation applies.
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    text_blocks = [block.text for block in response.content if block.type == "text"]
    return parse_classifier_response("\n".join(text_blocks))


def write_results(results: list[dict[str, Any]]) -> None:
    correct = sum(item["correct"] for item in results)
    accuracy = correct / len(results)
    matrix: dict[str, Counter[str]] = defaultdict(Counter)
    for item in results:
        matrix[item["expected"]][item["predicted"]] += 1

    lines = [
        "# Wynik ewaluacji klasyfikatora",
        "",
        f"- Model: `{MODEL}`",
        f"- Przypadki: {len(results)}",
        f"- Poprawne: {correct}/{len(results)}",
        f"- Trafność: {accuracy:.2%}",
        f"- Próg: >85% ({'spełniony' if accuracy > 0.85 else 'niespełniony'})",
        "",
        "## Macierz pomyłek",
        "",
        "| Oczekiwana kategoria | Predykcja | Liczba |",
        "|---|---|---:|",
    ]
    for expected, predictions in sorted(matrix.items()):
        for predicted, count in sorted(predictions.items()):
            lines.append(f"| {expected} | {predicted} | {count} |")

    lines.extend(["", "## Przypadki", "", "| ID | Oczekiwane | Predykcja | Confidence | Wynik |", "|---|---|---|---:|---|"])
    for item in results:
        mark = "OK" if item["correct"] else "BŁĄD"
        lines.append(
            f"| {item['id']} | {item['expected']} | {item['predicted']} | {item['confidence']:.2f} | {mark} |"
        )
    RESULTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY is missing. Set it in the terminal environment; never commit it.", file=sys.stderr)
        return 2

    template = PROMPT_PATH.read_text(encoding="utf-8")
    dataset = load_dataset()
    client = anthropic.Anthropic(api_key=api_key)
    results = []
    for record in dataset:
        prediction = classify(client, render_prompt(template, record))
        results.append(
            {
                "id": record["id"],
                "expected": record["expected_category"],
                "predicted": prediction["category"],
                "confidence": prediction["confidence"],
                "correct": prediction["category"] == record["expected_category"],
            }
        )

    write_results(results)
    accuracy = sum(item["correct"] for item in results) / len(results)
    print(f"accuracy={accuracy:.2%} cases={len(results)} results={RESULTS_PATH}")
    return 0 if accuracy > 0.85 else 1


if __name__ == "__main__":
    raise SystemExit(main())
