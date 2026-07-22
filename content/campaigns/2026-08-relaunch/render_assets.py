#!/usr/bin/env python3
"""Render campaign SVG sources to PNG with ImageMagick."""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
IMAGE_RE = re.compile(r'<image href="([^"]+)"[^>]*/>')
SIZE_RE = re.compile(r'<svg[^>]+width="(\d+)"[^>]+height="(\d+)"')


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def render(svg: Path) -> None:
    png = svg.with_suffix(".png")
    source = svg.read_text(encoding="utf-8")
    match = IMAGE_RE.search(source)
    if not match:
        run("convert", "-background", "none", str(svg), str(png))
        return

    photo = (svg.parent / match.group(1)).resolve()
    size_match = SIZE_RE.search(source)
    if not size_match:
        raise RuntimeError(f"SVG nema eksplicitnu širinu i visinu: {svg}")
    width, height = size_match.groups()
    canvas = f"{width}x{height}"
    overlay_source = IMAGE_RE.sub("", source, count=1)
    with tempfile.TemporaryDirectory(prefix="aid-render-") as temp_dir:
        temp = Path(temp_dir)
        overlay_svg = temp / "overlay.svg"
        overlay_png = temp / "overlay.png"
        background_png = temp / "background.png"
        overlay_svg.write_text(overlay_source, encoding="utf-8")
        run(
            "convert", str(photo), "-resize", f"{canvas}^", "-gravity", "center",
            "-extent", canvas, str(background_png)
        )
        run("convert", "-background", "none", str(overlay_svg), str(overlay_png))
        run(
            "convert", str(background_png), str(overlay_png),
            "-define", "compose:args=78,22", "-compose", "blend", "-composite", str(png)
        )


def main() -> None:
    for folder in (ROOT / "posts", ROOT / "stories"):
        for svg in sorted(folder.glob("*.svg")):
            render(svg)


if __name__ == "__main__":
    main()
