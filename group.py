import csv
import os
import sys
from pathlib import Path


def main(args: list[str]) -> None:
    if len(args) < 2:
        print("使用方法：" + f"`uv run .\\{os.path.basename(__file__)} target\\path`")
        return

    p = Path(args[1])
    if not p.is_dir():
        return

    d: dict[str, list[str]] = {}
    for f in p.iterdir():
        if f.suffix != ".txt":
            continue

        key = f.stem.split("_")[0]
        lines = [
            line for line in f.read_text("utf-8").strip().splitlines() if line.strip()
        ]
        if key not in d:
            d[key] = lines
        else:
            d[key].extend(lines)

    out_path = p / f"{list(d.keys())[0][:5]}.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "text"])
        for k, v in d.items():
            writer.writerow([k, " ".join(v)])


if __name__ == "__main__":
    main(sys.argv)
