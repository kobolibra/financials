#!/usr/bin/env python3
"""Produce version-masked reader material and verify its review before reveal."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets
import shutil

STAGES = ("first", "final")
FORMATS = ("report.html", "desktop.png", "mobile.png")
LABELS = ("A", "B")
ROLES = ("finance", "visual")
CHOICES = (*LABELS, "TIE")


def fingerprint(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def declared_source(report):
    match = re.search(r'<script[^>]*\bid="ledger-data"[^>]*>(.*?)</script>',
                      report.read_text(encoding="utf-8"), re.DOTALL)
    if not match:
        raise ValueError("report has no embedded source ledger")
    return json.loads(match.group(1))["source"]["original_bytes_sha256"]


def material(source, baseline, candidate):
    files = {"original.pdf": source}
    if source.suffix.lower() != ".pdf" or not source.is_file():
        raise ValueError("original PDF is required")
    with source.open("rb") as data:
        if data.read(5) != b"%PDF-":
            raise ValueError("original must contain PDF bytes")
    source_sha = fingerprint(source)
    versions = ["baseline", "candidate"]
    secrets.SystemRandom().shuffle(versions)
    dirs = {"baseline": baseline, "candidate": candidate}
    mapping = dict(zip(LABELS, versions))
    for label, version in mapping.items():
        for stage in STAGES:
            for name in FORMATS:
                path = dirs[version] / stage / name
                if not path.is_file() or not path.stat().st_size:
                    raise ValueError(f"missing or empty {version}/{stage}/{name}")
                with path.open("rb") as data:
                    if name.endswith(".png") and data.read(8) != b"\x89PNG\r\n\x1a\n":
                        raise ValueError(f"screenshot must contain PNG bytes: {version}/{stage}/{name}")
                if name == "report.html" and declared_source(path) != source_sha:
                    raise ValueError(f"report source does not match the frozen PDF: {version}/{stage}")
                files[f"{label}/{stage}/{name}"] = path
    return files, mapping


def prepare(source, baseline, candidate, out):
    files, mapping = material(source, baseline, candidate)
    digests = {name: fingerprint(path) for name, path in files.items()}
    if all(digests[f"A/{stage}/report.html"] == digests[f"B/{stage}/report.html"]
           for stage in STAGES):
        raise ValueError("baseline and candidate reports are identical at both stages")

    out.mkdir(parents=True)
    packet = out / "reviewer"
    for name, src in files.items():
        target = packet / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
    seal = {"schema": "financials.editorial_review_packet.v1", "sha256": digests}
    save(packet / "manifest.json", seal)
    save(out / "private-key.json", {"labels": mapping, "manifest_sha256": fingerprint(packet / "manifest.json")})
    fields = {"preferred": "NOT_CHECKED", "locators": [], "finding": ""}
    save(packet / "review.json", {
        "reviewer_independence": "NOT_CHECKED",
        "roles": {role: {"reviewer": "", **{stage: fields for stage in STAGES}} for role in ROLES},
    })


def assess(packet):
    reviewer_dir = packet / "reviewer"
    manifest_path = reviewer_dir / "manifest.json"
    key = read(packet / "private-key.json")
    if key["manifest_sha256"] != fingerprint(manifest_path):
        raise ValueError("reviewer manifest changed after the packet was sealed")
    for name, expected in read(manifest_path)["sha256"].items():
        if fingerprint(reviewer_dir / name) != expected:
            raise ValueError(f"review material changed: {name}")
    review = read(reviewer_dir / "review.json")
    if review["reviewer_independence"] != "DECLARED_INDEPENDENT_OF_AUTHORING":
        return {"status": "NOT_CHECKED", "reason": "independence declaration missing"}
    choices = {}
    for name in ROLES:
        role = review["roles"][name]
        if not isinstance(role["reviewer"], str) or not role["reviewer"].strip():
            raise ValueError(f"missing reviewer identity for {name}")
        choices[name] = {}
        for stage in STAGES:
            item = role[stage]
            preferred = item["preferred"]
            locators = item["locators"]
            if (preferred not in CHOICES or not isinstance(locators, list)
                    or not locators or any(not isinstance(x, str) or not x.strip() for x in locators)
                    or not isinstance(item["finding"], str) or not item["finding"].strip()):
                raise ValueError(f"incomplete {name}/{stage} review")
            choices[name][stage] = key["labels"].get(preferred, preferred)
    return {"status": "REVIEW_RECORDED", "preference": choices,
            "independence": "SELF_DECLARED_BY_REVIEWERS",
            "certifies_generalization": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    pack = commands.add_parser("prepare")
    for field in ("source", "baseline", "candidate", "out"):
        pack.add_argument("--" + field, required=True, type=Path)
    commands.add_parser("assess").add_argument("packet", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.source, args.baseline, args.candidate, args.out)
            print(args.out / "reviewer")
        else:
            print(json.dumps(assess(args.packet), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
