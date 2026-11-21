"""
Framework auto-detection tool.

Scans a workspace directory and reports which FiveM/RedM framework is in use
based on fxmanifest.lua dependencies, require/import patterns, and global usage.
"""

from __future__ import annotations

import os
import re

from tools.manifest_common import walk_workspace


# Manifest signals match a quoted dependency or script token such as
# 'es_extended', '@qbx_core/...' or "rsg-core", not bare substrings, so
# unrelated names (for example qb-target or esx_menu) do not count.
def _manifest_token(name: str) -> re.Pattern[str]:
    return re.compile(r"""['"]@?""" + re.escape(name) + r"""[/'"]""")


MANIFEST_SIGNALS: list[tuple[re.Pattern[str], str, str]] = [
    (_manifest_token("es_extended"), "es_extended", "esx"),
    (_manifest_token("qbx_core"), "qbx_core", "qbox"),
    (_manifest_token("qb-core"), "qb-core", "qbcore"),
    (_manifest_token("ox_core"), "ox_core", "oxcore"),
    (_manifest_token("vorp_core"), "vorp_core", "vorp"),
    (_manifest_token("rsg-core"), "rsg-core", "rsg"),
]

# Libraries are reported but do not decide the framework: ox_lib is used by
# ESX, QBCore, Qbox and standalone resources alike.
LIBRARY_SIGNALS: list[tuple[re.Pattern[str], str]] = [
    (_manifest_token("ox_lib"), "ox_lib"),
    (_manifest_token("oxmysql"), "oxmysql"),
]

LUA_COMMENT_RE = re.compile(r"--.*")

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

    libraries: set[str] = set()
    _scan_workspace(workspace_path, scores, evidence, libraries)

    if all(v == 0 for v in scores.values()):
        scores["standalone"] = 1
        evidence["standalone"].append("No framework signals detected")

    best = max(scores, key=lambda k: scores[k])
    tied = [k for k, v in scores.items() if v == scores[best]]
    total = sum(scores.values())
    confidence = scores[best] / total if total > 0 else 0

    if confidence < 0.5 and scores[best] < 3:
        confidence_label = "low"
    elif confidence < 0.75:
        confidence_label = "medium"
    else:
        confidence_label = "high"

    if len(tied) > 1:
        lines = [
            f"Detected framework: multiple frameworks / bridge ({', '.join(tied)})",
            f"Confidence: tie ({scores[best]} signals each). The resource supports "
            "several frameworks or bridges between them.",
            "",
        ]
        for k in tied:
            if evidence[k]:
                lines.append(f"Evidence for {k}:")
                for e in evidence[k][:5]:
                    lines.append(f"  - {e}")
        lines.append("")
    else:
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

    if libraries:
        lines.append(f"Libraries: {', '.join(sorted(libraries))}")
        lines.append("")

    others = {k: v for k, v in scores.items() if k not in tied and v > 0}
    if others:
        lines.append("Other signals found:")
        for k, v in sorted(others.items(), key=lambda x: -x[1]):
            lines.append(f"  {k}: {v} signals")
            for e in evidence[k][:3]:
                lines.append(f"    - {e}")

    return "\n".join(lines)


def _read(fpath: str) -> str | None:
    try:
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            return f.read(MAX_FILE_SIZE)
    except OSError:
        return None


def _scan_workspace(
    workspace_path: str,
    scores: dict[str, int],
    evidence: dict[str, list[str]],
    libraries: set[str],
) -> None:
    """Walk the workspace once, scoring fxmanifest.lua signals and code patterns."""
    for root, files in walk_workspace(workspace_path):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            is_manifest = fname == "fxmanifest.lua"
            if not is_manifest and ext not in SCANNABLE_EXTENSIONS:
                continue

            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, workspace_path)
            content = _read(fpath)
            if content is None:
                continue

            if is_manifest:
                manifest = LUA_COMMENT_RE.sub("", content)
                for pattern, signal, framework in MANIFEST_SIGNALS:
                    if pattern.search(manifest):
                        scores[framework] += 3
                        evidence[framework].append(f"{relpath}: manifest references '{signal}'")
                for pattern, library in LIBRARY_SIGNALS:
                    if pattern.search(manifest):
                        libraries.add(library)

            if ext in SCANNABLE_EXTENSIONS:
                for pattern, framework in CODE_SIGNALS:
                    if pattern.search(content):
                        scores[framework] += 1
                        evidence[framework].append(f"{relpath}: matches pattern for {framework}")
