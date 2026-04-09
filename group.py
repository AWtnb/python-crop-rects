import csv
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple


def format_author_line(line: str) -> str:
    line = re.sub(r"\s*・\s*", "", line)
    line = re.sub(r"([ぁ-ん])\s+([ぁ-ん])", lambda m: m.group(1) + m.group(2), line)
    line = re.sub(r"[（）\(\)「」【】\|]", "", line)
    line = line.replace("=", " ")
    return line


class ExtractResult(NamedTuple):
    base_file: str
    is_title: bool
    lines: list[str]


def main(args: list[str]) -> None:
    if len(args) < 2:
        print("使用方法：" + f"`uv run .\\{os.path.basename(__file__)} target\\path`")
        return

    p = Path(args[1])
    if not p.is_dir():
        return

    d: dict[str, list[ExtractResult]] = {}
    for f in p.iterdir():
        if f.suffix != ".txt":
            continue

        lines = [
            line for line in f.read_text("utf-8").strip().splitlines() if line.strip()
        ]

        base_name = f.stem.split("_")[0]
        result = ExtractResult(base_name, f.stem.endswith("_title"), lines)
        if base_name not in d:
            d[base_name] = [result]
        else:
            d[base_name].append(result)

    for suffix in ["", "_sorted"]:
        out_path = p / f"{list(d.keys())[0][:5]}{suffix}.csv"
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["file", "title", "author"])
            for base_name, results in d.items():
                title_lines = []
                author_lines = []
                for r in results:
                    if r.is_title:
                        [title_lines.append(line) for line in r.lines]
                    else:
                        [author_lines.append(line) for line in r.lines]
                writer.writerow(
                    [
                        base_name,
                        " ".join(title_lines),
                        format_author_line(" ".join(author_lines)),
                    ]
                )


if __name__ == "__main__":
    main(sys.argv)
