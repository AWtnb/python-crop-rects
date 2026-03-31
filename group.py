import csv
import os
import sys
from pathlib import Path
from typing import NamedTuple


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

    out_path = p / f"{list(d.keys())[0][:5]}.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "type", "text"])
        for base_name, results in d.items():
            title_lines = []
            non_title_lines = []
            for r in results:
                if r.is_title:
                    [title_lines.append(line) for line in r.lines]
                else:
                    [non_title_lines.append(line) for line in r.lines]
            if len(title_lines) != 0:
                writer.writerow([base_name, "タイトル", " ".join(title_lines)])
            if len(non_title_lines) != 0:
                writer.writerow([base_name, "著者", " ".join(non_title_lines)])


if __name__ == "__main__":
    main(sys.argv)
