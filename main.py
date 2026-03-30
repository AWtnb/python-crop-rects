import os
import sys
from pathlib import Path

import pymupdf


def annots_sorter(a: pymupdf.Annot) -> tuple[float, float]:
    rect = a.rect
    return ((rect.y0 + rect.y1) / 2, (rect.x0 + rect.x1) / 2)


def trim_rect(rect: pymupdf.Rect, pt: int) -> pymupdf.Rect:
    return rect + (pt, pt, -pt, -pt)


def crop_rects(pdf_path: Path) -> None:
    doc = pymupdf.Document(pdf_path)
    counter = 1
    for i in range(doc.page_count):
        page: pymupdf.Page = doc[i]
        page_annots = list(page.annots())
        page_annots.sort(key=annots_sorter)
        for annot in page_annots:
            rect = trim_rect(annot.rect, 1)
            pix = page.get_pixmap(clip=rect, dpi=200)
            comment = annot.info.get("content", "")
            suffix = "_commented" if comment != "" else ""
            pix.save(pdf_path.with_name(f"{pdf_path.stem}_{counter:03}{suffix}.png"))
            counter += 1
    doc.close()


def main(args: list[str]) -> None:
    if len(args) < 2:
        print("使用方法：" + f"`uv run .\\{os.path.basename(__file__)} target\\path`")
        return

    p = Path(args[1])
    if p.is_dir():
        for f in p.iterdir():
            if f.suffix == ".pdf":
                crop_rects(f)
        return

    if p.suffix != ".pdf":
        print("無効なパスです")
        return

    crop_rects(p)


if __name__ == "__main__":
    main(sys.argv)
