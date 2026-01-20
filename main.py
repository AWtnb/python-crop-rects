import os
import sys
from pathlib import Path

import pymupdf


def annots_sorter(a: pymupdf.Annot) -> tuple[float, float]:
    rect = a.rect
    return ((rect.y0 + rect.y1) / 2, (rect.x0 + rect.x1) / 2)


def as_rects(annots: list[pymupdf.Annot]) -> list[pymupdf.Rect]:
    trim = 1
    rects: list[pymupdf.Rect] = []
    for annot in annots:
        rect = annot.rect
        inner_rect = rect + (trim, trim, -trim, -trim)
        rects.append(inner_rect)
    return rects


def crop_rects(pdf_path: Path) -> None:
    doc = pymupdf.Document(pdf_path)
    for i in range(doc.page_count):
        page: pymupdf.Page = doc[i]
        page_annots = list(page.annots())
        page_annots.sort(key=annots_sorter)
        for i, rect in enumerate(as_rects(page_annots)):
            pix = page.get_pixmap(clip=rect, dpi=200)
            pix.save(pdf_path.with_name(f"{pdf_path.stem}_{i:03}.png"))

    doc.close()


def main(args: list[str]) -> None:
    if len(args) < 2:
        print("使用方法：" + f"`uv run .\\{os.path.basename(__file__)} target\\path`")
        return
    p = Path(args[1])
    if p.is_dir() or p.suffix != ".pdf":
        print("PDFファイルを指定してください")
        return
    crop_rects(p)


if __name__ == "__main__":
    main(sys.argv)
