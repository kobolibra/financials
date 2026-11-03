#!/usr/bin/env python3
"""Fail-closed handoff contract: current Git tree, Skill, manuals and actual company index.

Run from any current working directory: python scripts/check_handoff.py
No GitHub tokens, internet access, nonstandard packages or ChatGPT memory required.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check_skill(manifest: dict, skill: str) -> list[str]:
    errors = []
    match = re.search(r"(?m)^version:\s*([^\s]+)\s*$", skill)
    version = match.group(1) if match else None
    if version != manifest["skill"]["version"]:
        errors.append(f"SKILL_VERSION_MISMATCH: manifest {manifest['skill']['version']}, actual {version}")
    if len(skill) < 15000:
        errors.append("SKILL_INCOMPLETE: full company Skill unexpectedly short")
    if "FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON" not in skill:
        errors.append("SKILL_SANKEY_GATE_ABSENT: no explicit source-reason omission contract")
    return errors


def check_catalog(manifest: dict, catalog: dict, homepage: str) -> list[str]:
    errors = []
    issuers = catalog.get("issuers", [])
    actual_codes = [x.get("code") for x in issuers]
    actual_routes = [x.get("href") for x in issuers]
    expected_codes = manifest["site"]["company_codes"]
    expected_count = manifest["site"]["company_count"]
    if len(issuers) != expected_count or actual_codes != expected_codes:
        errors.append(f"CATALOG_STATUS_DRIFT: expected {expected_count} {expected_codes}, actual {actual_codes}")
    if len(set(actual_codes)) != len(actual_codes) or len(set(actual_routes)) != len(actual_routes):
        errors.append("CATALOG_DUPLICATE_ISSUER_OR_ROUTE")
    shown = re.findall(r'<a\s+class="company"\s+href="([^"]+)"', homepage)
    if sorted(shown) != sorted(actual_routes):
        errors.append(f"ROOT_CATALOG_DRIFT: publication HTML differs from source issuer routes ({len(shown)} shown)")
    if 'href="/optical-2026h1.html"' not in homepage:
        errors.append("MISSING_OPTICAL_COMPARATIVE_TOPIC")
    if 'href="./research/2026-h1-v10/index.html"' in homepage:
        errors.append("REGRESSION_DUPLICATED_FOUR_COMPANY_FRONT_DOOR")
    if "canonical_company_directory" not in manifest or manifest["canonical_company_directory"] != "/":
        errors.append("WRONG_PRODUCTION_ENTRY")
    for x in actual_routes:
        if not (ROOT / "public" / x.lstrip("/")).is_file():
            errors.append(f"MISSING_CANONICAL_REPORT: {x}")
    return errors


def check_current_state(state: str, readme: str, manifest: dict) -> list[str]:
    errors = []
    if "ACTIVE PROJECT STATE" not in state[:150]:
        errors.append("STALE_PROJECT_STATE_HEADER")
    if "LATEST ACTUAL PRODUCTION IS 2026-11-03 V9" in state[:800]:
        errors.append("STALE_V9_RELEASE_IN_ACTIVE_STATE")
    if manifest["skill"]["version"] not in state.lower():
        errors.append("CURRENT_STATE_SKILL_VERSION_MISMATCH")
    if "NOT_CHECKED" not in state or "NOT_CHECKED" not in readme:
        errors.append("MISSING_EXPLICIT_UNVERIFIED_RESEARCH_GATES")
    if "START_HERE.md" not in readme[:500] or "https://financials-in-visuals.pages.dev/" not in readme:
        errors.append("README_NO_CURRENT_FRONT_DOOR")
    if "不需要 GitHub Actions" in readme:
        errors.append("STALE_README_DISABLES_REAL_RELEASE_QA")
    return errors


def check_repo() -> list[str]:
    errors = []
    mandatory = [
        "README.md", "START_HERE.md", "AGENTS.md", "PROJECT_STATE.md",
        "project-status.json", "docs/HANDOFF_PROTOCOL.md",
        "docs/NEW_SESSION_PROMPT.md", "docs/REPORT_RELEASE_CHECKLIST.md",
        "docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md",
        ".github/copilot-instructions.md",
        "skills/ashare-financial-storytelling/SKILL.md",
        "site/research_catalog.json", "site/portal_builder.py",
        "public/index.html", "scripts/check_handoff.py",
        ".github/workflows/verify-handoff.yml",
    ]
    for p in mandatory:
        if not (ROOT / p).is_file():
            errors.append(f"MISSING_HANDOFF_SOURCE: {p}")
    if errors:
        return errors

    manifest = json.loads(load("project-status.json"))
    catalog = json.loads(load("site/research_catalog.json"))
    if manifest.get("production_branch") != "main" or manifest.get("production_url") != "https://financials-in-visuals.pages.dev/":
        errors.append("WRONG_PRODUCTION_REPO_OR_URL")
    if manifest.get("repository") != "kobolibra/financials":
        errors.append("WRONG_GITHUB_REPOSITORY")
    if manifest.get("last_verified_release", {}).get("warning", "") == "":
        errors.append("STORED_CI_MUST_BE_EXPLICITLY_HISTORICAL")

    skill = load(manifest["skill"]["path"])
    errors += check_skill(manifest, skill)
    for p in manifest["skill"]["required_manuals"]:
        if not (ROOT / p).is_file() or len(load(p)) < 2000:
            errors.append(f"MANUAL_MISSING_OR_TRUNCATED: {p}")
    if len(manifest["skill"]["required_manuals"]) != 5:
        errors.append("RESEARCH_MANUAL_COUNT_NOT_FIVE")
    errors += check_catalog(manifest, catalog, load("public/index.html"))
    errors += check_current_state(load("PROJECT_STATE.md"), load("README.md"), manifest)

    if not all(term in load("AGENTS.md") for term in
               ["SKILL.md", "NOT_CHECKED", "START_HERE.md", "REPORT_RELEASE_CHECKLIST"]):
        errors.append("AGENT_INSTRUCTIONS_NOT_ACTIVATING_SKILL_AND_GATES")
    if not all(term in load("docs/NEW_SESSION_PROMPT.md") for term in
               ["START_HERE.md", "SKILL.md", "01", "02", "03", "04", "05", "Cloudflare", "NOT_CHECKED"]):
        errors.append("NEW_CHAT_PROMPT_INCOMPLETE")
    if manifest.get("limitations", {}).get("independent_second_human_analyst") != "NOT_CHECKED":
        errors.append("UNSUPPORTED_HUMAN_REVIEW_CLAIM")
    if manifest.get("limitations", {}).get("all_seven_full_material_note_reviews") != "NOT_CHECKED":
        errors.append("UNSUPPORTED_SEVEN_ISSUER_NOTE_REVIEW_CLAIM")
    if "收入 37,651,189.26" not in load("docs/2026H1_OPTICAL_REVENUE_NOTE_CLASSIFICATION_AUDIT.md") or "27,106,113.32" not in load("docs/2026H1_OPTICAL_REVENUE_NOTE_CLASSIFICATION_AUDIT.md"):
        errors.append("OPTICAL_NOTE_AUDIT_SOURCE_LINK_MISSING")
    if "其他业务（附注）" not in load("public/300394.html"):
        errors.append("TIANFU_SOURCE_CLASSIFICATION_REGRESSED")
    if "其他（业务类型）" not in load("public/300502.html"):
        errors.append("EOPTOLINK_SOURCE_CLASSIFICATION_REGRESSED")
    if "未列示差额（计算）" in load("public/300394.html") or "未列示差额（计算）" in load("public/300502.html"):
        errors.append("FAKE_FINANCIAL_SANKEY_BALANCING_NODE_REGRESSED")

    for p in ["README.md", "START_HERE.md", "AGENTS.md", "PROJECT_STATE.md",
              "docs/HANDOFF_PROTOCOL.md", "docs/NEW_SESSION_PROMPT.md",
              "skills/ashare-financial-storytelling/SKILL.md"]:
        if chr(92) + chr(96) in load(p):
            errors.append(f"ESCAPED_MARKDOWN_CODE_TICKS: {p}")

    return errors


if __name__ == "__main__":
    try:
        problems = check_repo()
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print("HANDOFF_CONTRACT_ERROR:", type(exc).__name__, str(exc), file=sys.stderr)
        sys.exit(1)
    if problems:
        for problem in problems:
            print("HANDOFF_FAIL", problem, file=sys.stderr)
        sys.exit(2)
    print("HANDOFF_CONTRACT_PASS: skill v8.3.2, 5 manuals, 7 issuer URLs, 1 homepage, real optical note categories, clear NOT_CHECKED gates and no stale handoff entry")
