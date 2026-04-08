"""
Framework auto-detection tool.

Scans a workspace directory and reports which FiveM/RedM framework is in use
based on fxmanifest.lua dependencies, require/import patterns, and global usage.
"""

from __future__ import annotations

import os
import re


MANIFEST_SIGNALS: dict[str, str] = {
    "es_extended": "esx",
    "esx_": "esx",
    "qbx_core": "qbox",
    "qb-core": "qbcore",
    "qb-": "qbcore",
    "ox_core": "oxcore",
    "ox_lib": "oxcore",
    "vorp_core": "vorp",
    "rsg-core": "rsg",
}

CODE_SIGNALS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"""exports\s*\[\s*['"]es_extended['"]\s*\]"""), "esx"),
    (re.compile(r"""ESX\s*=\s*exports"""), "esx"),
    (re.compile(r"""getSharedObject"""), "esx"),
    (re.compile(r"""exports\s*\[\s*['"]qbx_core['"]\s*\]"""), "qbox"),
    (re.compile(r"""exports\.qbx_core"""), "qbox"),
    (re.compile(r"""require\s+['"]@qbx_core"""), "qbox"),
    (re.compile(r"""exports\s*\[\s*['"]qb-core['"]\s*\]"""), "qbcore"),
    (re.compile(r"""QBCore\s*=\s*exports"""), "qbcore"),
    (re.compile(r"""GetCoreObject"""), "qbcore"),
    (re.compile(r"""require\s+['"]@ox_core"""), "oxcore"),
    (re.compile(r"""require\s+['"]@ox_lib"""), "oxcore"),
    (re.compile(r"""exports\s*\[\s*['"]ox_lib['"]\s*\]"""), "oxcore"),
    (re.compile(r"""exports\.vorp_core"""), "vorp"),
    (re.compile(r"""VORPcore\s*="""), "vorp"),
    (re.compile(r"""exports\s*\[\s*['"]rsg-core['"]\s*\]"""), "rsg"),
    (re.compile(r"""RSGCore\s*=\s*exports"""), "rsg"),
]

SCANNABLE_EXTENSIONS = {".lua", ".js", ".ts"}
MAX_FILE_SIZE = 256 * 1024


def detect_framework(workspace_path: str = ".") -> str:
    """Detect the framework used in a FiveM/RedM resource workspace.

    Returns a summary with the detected framework, confidence, and evidence.
    """

    if not os.path.isdir(workspace_path):
        return f"Error: directory not found: {workspace_path}"

    scores: dict[str, int] = {
        "esx": 0, "qbcore": 0, "qbox": 0, "oxcore": 0,
        "vorp": 0, "rsg": 0, "standalone": 0,
    }
    evidence: dict[str, list[str]] = {
        "esx": [], "qbcore": [], "qbox": [], "oxcore": [],
        "vorp": [], "rsg": [], "standalone": [],
    }

    _scan_manifests(workspace_path, scores, evidence)
    _scan_code(workspace_path, scores, evidence)

    if all(v == 0 for v in scores.values()):
        scores["standalone"] = 1
        evidence["standalone"].append("No framework signals detected")

    best = max(scores, key=lambda k: scores[k])
    total = sum(scores.values())
    confidence = scores[best] / total if total > 0 else 0

    if confidence < 0.5 and scores[best] < 3:
        confidence_label = "low"
    elif confidence < 0.75:
        confidence_label = "medium"
    else:
        confidence_label = "high"

    lines = [
        f"Detected framework: {best}",
        f"Confidence: {confidence_label} ({scores[best]} signals, {confidence:.0%} of total)",
        "",
    ]

    if evidence[best]:
        lines.append("Evidence:")
        for e in evidence[best][:10]:
            lines.append(f"  - {e}")
        lines.append("")

    others = {k: v for k, v in scores.items() if k != best and v > 0}
    if others:
        lines.append("Other signals found:")
        for k, v in sorted(others.items(), key=lambda x: -x[1]):
            lines.append(f"  {k}: {v} signals")
            for e in evidence[k][:3]:
                lines.append(f"    - {e}")

    return "\n".join(lines)


def _scan_manifests(
    workspace_path: str,
    scores: dict[str, int],
    evidence: dict[str, list[str]],
) -> None:
    """Scan fxmanifest.lua files for dependency/shared_script signals."""
    for root, _dirs, files in os.walk(workspace_path):
        if "node_modules" in root or ".git" in root:
            continue

        for fname in files:
            if fname != "fxmanifest.lua":
                continue

            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, workspace_path)

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(MAX_FILE_SIZE)
            except OSError:
                continue

            for signal, framework in MANIFEST_SIGNALS.items():
                if signal in content:
                    scores[framework] += 3
                    evidence[framework].append(f"{relpath}: manifest references '{signal}'")


def _scan_code(
    workspace_path: str,
    scores: dict[str, int],
    evidence: dict[str, list[str]],
) -> None:
    """Scan .lua/.js/.ts files for framework-specific code patterns."""
    for root, _dirs, files in os.walk(workspace_path):
        if "node_modules" in root or ".git" in root:
            continue

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SCANNABLE_EXTENSIONS:
                continue

            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, workspace_path)

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(MAX_FILE_SIZE)
            except OSError:
                continue

            for pattern, framework in CODE_SIGNALS:
                if pattern.search(content):
                    scores[framework] += 1
                    evidence[framework].append(f"{relpath}: matches pattern for {framework}")
