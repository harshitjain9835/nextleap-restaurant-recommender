"""Extract mermaid blocks from markdown and flag common syntax pitfalls."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def check_block(name: str, index: int, source: str) -> list[str]:
    issues: list[str] = []
    lines = source.splitlines()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("section ") and line.startswith("  section"):
            issues.append(f"L{i}: gantt section should use 4-space indent, not 2")
        if re.search(r"\{[^}\"]*>[^}\"]*\}", line):
            issues.append(f"L{i}: '>' inside diamond node — quote the label")
        if re.search(r"\[[^\"\]]*:[^\"\]]*\]", line):
            issues.append(f"L{i}: colon inside unquoted [] node label")
        if "Restaurant[]" in line:
            issues.append(f"L{i}: '[]' in sequence message may break parser")

    if source.strip().startswith("gantt"):
        for line in lines:
            if line.startswith("  section ") and not line.startswith("    section "):
                issues.append("gantt: mis-indented section line")

    return [f"{name} #{index}: {msg}" for msg in issues]


def main() -> int:
    exit_code = 0
    for path in sorted(ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        blocks = PATTERN.findall(text)
        if not blocks:
            continue
        print(f"{path.name}: {len(blocks)} diagram(s)")
        for idx, block in enumerate(blocks, 1):
            issues = check_block(path.name, idx, block)
            if issues:
                exit_code = 1
                for issue in issues:
                    print(f"  WARN {issue}")
            else:
                print(f"  OK   block {idx} ({block.strip().splitlines()[0]})")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
