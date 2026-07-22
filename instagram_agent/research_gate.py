#!/usr/bin/env python3
"""Validate the mandatory fresh benchmark and creative score for campaign items."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path


class ResearchGateError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchGateError(f"Ne mogu učitati {path}: {exc}") from exc


def gate_path(manifest_path: Path, manifest: dict) -> Path:
    value = manifest.get("research_gate_path")
    if not value:
        raise ResearchGateError("Manifest nema research_gate_path.")
    return (manifest_path.parent / value).resolve()


def validate_research_gate(
    manifest_path: Path,
    manifest: dict,
    content_ids: list[str] | None = None,
    today: date | None = None,
) -> dict:
    path = gate_path(manifest_path, manifest)
    gate = load_json(path)
    if gate.get("schema_version") != 1:
        raise ResearchGateError("Research gate mora imati schema_version=1.")
    researched = date.fromisoformat(gate["researched_at"])
    expires = date.fromisoformat(gate["expires_at"])
    validity_days = (expires - researched).days
    if validity_days < 0 or validity_days > 7:
        raise ResearchGateError("Research gate mora vrijediti od 0 do najviše 7 dana.")
    current = today or date.today()
    if researched > current:
        raise ResearchGateError(f"Research datum je u budućnosti: {researched}.")
    if current > expires:
        raise ResearchGateError(
            f"Benchmark je istekao {expires}; prije nove izmjene ili odobrenja ponoviti aktualno istraživanje."
        )
    sources = gate.get("sources", [])
    if len(sources) < 3 or any(not source.get("url") for source in sources):
        raise ResearchGateError("Research gate zahtijeva najmanje tri evidentirana izvora.")
    benchmark = (path.parent / gate["benchmark_file"]).resolve()
    if not benchmark.is_file():
        raise ResearchGateError(f"Nedostaje benchmark datoteka: {benchmark}")
    rubric = gate.get("rubric", {})
    maxima = list(rubric.values())
    if len(maxima) != 7 or sum(maxima) != 100:
        raise ResearchGateError("Creative rubric mora imati sedam kriterija i ukupno 100 bodova.")
    minimum = int(gate.get("minimum_score", 80))
    requested = content_ids or [item["id"] for item in manifest.get("items", [])]
    items = gate.get("items", {})
    results = {}
    for content_id in requested:
        record = items.get(content_id)
        if not record:
            raise ResearchGateError(f"{content_id}: nema research gate zapisa.")
        scorecard = record.get("scorecard", [])
        if len(scorecard) != len(maxima):
            raise ResearchGateError(f"{content_id}: scorecard nema svih sedam kriterija.")
        if any(not isinstance(value, int) or value < 0 or value > maxima[index] for index, value in enumerate(scorecard)):
            raise ResearchGateError(f"{content_id}: scorecard sadrži nevaljan rezultat.")
        score = sum(scorecard)
        if score < minimum or record.get("status") != "pass":
            raise ResearchGateError(f"{content_id}: research gate nije prošao ({score}/100).")
        if len(record.get("patterns", [])) < 2 or not record.get("rejected") or not record.get("expected_signal"):
            raise ResearchGateError(f"{content_id}: nedostaju obrasci, odbijena alternativa ili signal uspjeha.")
        results[content_id] = score
    return {
        "path": str(path),
        "benchmark": str(benchmark),
        "researched_at": researched.isoformat(),
        "expires_at": expires.isoformat(),
        "scores": results,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Validate AID content research gate")
    result.add_argument("--manifest", type=Path, required=True)
    result.add_argument("--id", action="append", dest="content_ids")
    return result


def main() -> int:
    args = parser().parse_args()
    manifest_path = args.manifest.resolve()
    try:
        manifest = load_json(manifest_path)
        result = validate_research_gate(manifest_path, manifest, args.content_ids)
    except (ResearchGateError, KeyError, ValueError) as exc:
        print(f"RESEARCH GATE BLOKIRAN: {exc}", file=sys.stderr)
        return 1
    for content_id, score in result["scores"].items():
        print(f"PASS {content_id}: {score}/100")
    print(f"Benchmark vrijedi do {result['expires_at']}; validirano {len(result['scores'])} sadržaja.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
