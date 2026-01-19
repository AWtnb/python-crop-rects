import os
import sys
from pathlib import Path
from typing import Iterator

import pymupdf
from PIL import Image


def rect_sorter(a: pymupdf.Annot) -> tuple[float, float]:
    rect = a.rect
    return ((rect.y0 + rect.y1) / 2, (rect.x0 + rect.x1) / 2)


def as_images(
    page: pymupdf.Page, rects: list[pymupdf.Rect], dpi: int
) -> Iterator[Image.Image]:
    # TODO rectのちょっと内側を取得したい

    for rect in rects:
        pix = page.get_pixmap(clip=rect, dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # ty:ignore[invalid-argument-type]
        yield img


def save_merged_image(images: list[Image.Image], out_path: Path) -> None:
    x_offset = 0
    y_offset = 0

    padding = 10
    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images) + padding * (len(images) - 1)

    combined = Image.new("RGB", (max_width, total_height), (255, 255, 255))

    for img in images:
        combined.paste(img, (x_offset, y_offset))
        y_offset += img.height + padding

    combined.save(out_path)


def as_rects(annots: list[pymupdf.Annot]) -> list[pymupdf.Rect]:
    trim = 2
    rects: list[pymupdf.Rect] = []
    for annot in annots:
        rect = annot.rect
        inner_rect = rect + (trim, trim, -trim, -trim)
        rects.append(inner_rect)
    return rects


def crop_rects(pdf_path: Path) -> None:
    doc = pymupdf.Document(pdf_path)
    images: list[Image.Image] = []
    for i in range(doc.page_count):
        page: pymupdf.Page = doc[i]
        page_annots = list(page.annots())
        page_annots.sort(key=rect_sorter)
        rects = as_rects(page_annots)  # [a.rect for a in page_annots]
        [images.append(img) for img in as_images(page, rects, 150)]

    doc.close()
    save_merged_image(images, pdf_path.with_name(pdf_path.stem + "_crop.png"))


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
