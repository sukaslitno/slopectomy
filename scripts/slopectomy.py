#!/usr/bin/env python3
"""Review Russian text for clustered synthetic-prose cliches.

The checker is intentionally conservative: it reports stylistic signals and
never labels a text as AI-generated. The rules live in ../references/rules.json
so the catalog can be audited or extended without changing the scanner.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from bisect import bisect_right
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
RULES_PATH = SCRIPT_DIR.parent / "references" / "rules.json"
DEFAULT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".vue",
    ".html",
    ".htm",
    ".py",
    ".rb",
    ".go",
    ".rs",
    ".java",
    ".swift",
}
IGNORED_DIRS = {".git", ".hg", ".svn", "node_modules", "dist", "build", "coverage", ".next", ".nuxt", "vendor"}
LABELS = {
    "isolated": "Изолированный штамп или обычная литературная инерция",
    "patina": "Заметный синтетический налёт",
    "strong_cluster": "Сильный кластер признаков",
    "dense": "Очень плотное совпадение с каталогом",
}


def load_rules(path: Path = RULES_PATH) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = data.get("rules")
    if not isinstance(rules, list):
        raise ValueError("rules.json must contain a rules array")
    return rules


def compile_patterns(rule: Dict[str, Any]) -> List[re.Pattern[str]]:
    patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in rule.get("patterns", [])]
    patterns.extend(re.compile(re.escape(value), re.IGNORECASE) for value in rule.get("literals", []))
    return patterns


def mask_ranges(text: str) -> str:
    """Mask code, URLs, links, and placeholders without changing offsets."""

    masked = list(text)
    protected = [
        r"```[\s\S]*?```",
        r"`[^`\n]+`",
        r"https?://\S+",
        r"\[[^\]]+\]\([^\)]+\)",
        r"\{\{[^}]*\}\}",
        r"\{[A-Za-z_][^}\n]{0,80}\}",
    ]
    for expression in protected:
        for match in re.finditer(expression, text, re.IGNORECASE):
            for index in range(match.start(), match.end()):
                if masked[index] != "\n":
                    masked[index] = " "
    return "".join(masked)


def paragraphs(text: str) -> List[Tuple[int, int, str]]:
    result: List[Tuple[int, int, str]] = []
    start = 0
    for match in re.finditer(r"\n\s*\n+", text):
        end = match.start()
        if text[start:end].strip():
            result.append((start, end, text[start:end]))
        start = match.end()
    if text[start:].strip():
        result.append((start, len(text), text[start:]))
    if not result and text.strip():
        result.append((0, len(text), text))
    return result


def paragraph_number(position: int, paragraph_starts: Sequence[int]) -> int:
    return bisect_right(paragraph_starts, position)


def excerpt(text: str, start: int, end: int, radius: int = 70) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    value = re.sub(r"\s+", " ", text[left:right]).strip()
    if left:
        value = "…" + value
    if right < len(text):
        value += "…"
    return value


def diagnosis(category_count: int) -> Tuple[str, str]:
    if category_count <= 2:
        return "isolated", LABELS["isolated"]
    if category_count <= 4:
        return "patina", LABELS["patina"]
    if category_count <= 6:
        return "strong_cluster", LABELS["strong_cluster"]
    return "dense", LABELS["dense"]


def scan_text(text: str, source: str, rules: Sequence[Dict[str, Any]], max_hits_per_rule: int = 5) -> Dict[str, Any]:
    masked = mask_ranges(text)
    paragraph_data = paragraphs(text)
    paragraph_starts = [item[0] for item in paragraph_data]
    findings: List[Dict[str, Any]] = []

    for rule in rules:
        matches: List[Tuple[int, int, str]] = []
        for pattern in compile_patterns(rule):
            for match in pattern.finditer(masked):
                if not match.group(0).strip():
                    continue
                span = (match.start(), match.end(), match.group(0))
                if any(start < span[1] and span[0] < end for start, end, _ in matches):
                    continue
                matches.append(span)
        matches.sort()
        for start, end, value in matches[:max_hits_per_rule]:
            paragraph = paragraph_number(start, paragraph_starts) if paragraph_starts else 1
            findings.append(
                {
                    "rule_id": rule["id"],
                    "category": rule["name"],
                    "kind": rule.get("kind", "unknown"),
                    "confidence": rule.get("confidence", "medium"),
                    "weight": rule.get("weight", 1),
                    "match": re.sub(r"\s+", " ", text[start:end]).strip(),
                    "excerpt": excerpt(text, start, end),
                    "line": text.count("\n", 0, start) + 1,
                    "paragraph": paragraph,
                    "near_end": bool(text) and start >= len(text) * 0.75,
                }
            )

    findings.sort(key=lambda item: (item["line"], item["category"], item["match"]))
    category_ids = {item["rule_id"] for item in findings}
    score = sum(next(rule.get("weight", 1) for rule in rules if rule["id"] == rule_id) for rule_id in category_ids)
    level, label = diagnosis(len(category_ids))
    clusters: List[Dict[str, Any]] = []
    by_paragraph: Dict[int, set[str]] = {}
    for item in findings:
        by_paragraph.setdefault(item["paragraph"], set()).add(item["rule_id"])
    for number, ids in sorted(by_paragraph.items()):
        if len(ids) >= 3:
            clusters.append({"paragraph": number, "category_count": len(ids), "rule_ids": sorted(ids)})

    return {
        "source": source,
        "category_count": len(category_ids),
        "weighted_score": score,
        "level": level,
        "diagnosis": label,
        "findings": findings,
        "paragraph_clusters": clusters,
    }


def iter_files(paths: Iterable[Path], include: str | None) -> Iterable[Path]:
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in DEFAULT_EXTENSIONS and (include is None or path.match(include)):
                yield path
            continue
        if not path.is_dir():
            continue
        for child in path.rglob("*"):
            if child.is_dir() or any(part in IGNORED_DIRS for part in child.parts):
                continue
            if child.suffix.lower() not in DEFAULT_EXTENSIONS:
                continue
            if include is not None and not child.match(include):
                continue
            yield child


def read_documents(args: argparse.Namespace) -> List[Tuple[str, str]]:
    if args.text is not None:
        return [("<text>", args.text)]
    documents: List[Tuple[str, str]] = []
    for path in iter_files([Path(value) for value in args.paths], args.include):
        try:
            documents.append((str(path), path.read_text(encoding="utf-8", errors="replace")))
        except OSError as error:
            print(f"warning: cannot read {path}: {error}", file=sys.stderr)
    return documents


def render_text(report: Dict[str, Any]) -> str:
    lines = [
        f"{report['source']}",
        f"Вывод: {report['diagnosis']}",
        f"Независимых категорий: {report['category_count']}; взвешенный балл: {report['weighted_score']}",
    ]
    if report["paragraph_clusters"]:
        lines.append("Кластеры по абзацам: " + ", ".join(str(item["paragraph"]) for item in report["paragraph_clusters"]))
    if not report["findings"]:
        lines.append("Совпадений по каталогу не найдено.")
        return "\n".join(lines)
    lines.append("")
    for item in report["findings"]:
        lines.append(f"строка {item['line']} [{item['confidence']}] {item['category']}")
        lines.append(f"  совпадение: {item['match']}")
        lines.append(f"  контекст: {item['excerpt']}")
    return "\n".join(lines)


def render_markdown(reports: Sequence[Dict[str, Any]]) -> str:
    lines = ["# Slopectomy report", "", "The report describes stylistic signals. It does not identify authorship or prove model use.", ""]
    for report in reports:
        lines.extend(
            [
                f"## {report['source']}",
                "",
                f"**Verdict:** {report['diagnosis']}",
                f"**Distinct categories:** {report['category_count']}",
                f"**Weighted score:** {report['weighted_score']}",
                "",
            ]
        )
        if not report["findings"]:
            lines.append("No catalogued matches found.")
            lines.append("")
            continue
        lines.extend(["| Line | Category | Confidence | Match |", "|---:|---|---|---|"])
        for item in report["findings"]:
            match = item["match"].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {item['line']} | {item['category']} | {item['confidence']} | {match} |")
        lines.append("")
        if report["paragraph_clusters"]:
            lines.append("Paragraph clusters: " + ", ".join(str(item["paragraph"]) for item in report["paragraph_clusters"]))
            lines.append("")
    return "\n".join(lines).rstrip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="Review one text string")
    source.add_argument("paths", nargs="*", help="Text files or directories")
    parser.add_argument("--include", help="Filename glob when scanning directories, for example '*.md'")
    parser.add_argument("--format", choices=("text", "md", "json"), default="text")
    parser.add_argument("--max-hits-per-rule", type=int, default=5)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.text is None and not args.paths:
        parser.error("provide at least one path when --text is not used")
    if args.max_hits_per_rule < 1:
        parser.error("--max-hits-per-rule must be positive")

    try:
        rules = load_rules()
        documents = read_documents(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    reports = [scan_text(text, source, rules, args.max_hits_per_rule) for source, text in documents]
    if args.format == "json":
        print(json.dumps({"reports": reports}, ensure_ascii=False, indent=2))
    elif args.format == "md":
        print(render_markdown(reports))
    else:
        print("\n\n".join(render_text(report) for report in reports) or "No readable text files found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
