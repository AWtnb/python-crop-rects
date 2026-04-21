import csv
import re
import sys
from pathlib import Path


def main(dir_path: str) -> None:
    p = Path(dir_path)
    lines = []
    for f in p.iterdir():
        if f.suffix != ".csv":
            continue
        issue_name = f.stem.replace("_sorted", "")
        with open(f, encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, r in enumerate(reader):
                if i == 0:
                    continue
                article_id, _, authors = r
                for a in authors.split("／"):
                    if a:
                        author_name = re.sub(r"[ぁ-ん]{2,}", "", a)
                        elems = author_name.split(" ")
                        if len(elems) == 1:
                            lines.append((issue_name, article_id, author_name, a))
                        else:
                            lines.append((issue_name, article_id, elems[1], a))

    out_path = p.parent / "out.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("媒体", "記事ID", "著者（仮）", "各種情報"))
        writer.writerows(lines)


if __name__ == "__main__":
    main(sys.argv[1])
