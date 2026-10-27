#!/usr/bin/python3
"""Genera la marca de agua del arranque (Plymouth): estrella de Luma + «luma».

Uso: render_boot.py <salida.png>
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QFontDatabase, QGuiApplication, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

SHARE = Path("/usr/share")


def main():
    out = sys.argv[1]
    share = Path(sys.argv[2]) if len(sys.argv) > 2 else SHARE
    app = QGuiApplication(sys.argv[:1])  # noqa: F841 (necesaria para QPainter y fuentes)
    for font in (share / "fonts" / "luma").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))

    w, h = 280, 96
    img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    QSvgRenderer(str(share / "luma" / "logo-mark.svg")).render(p, QRectF(8, 8, 80, 80))
    font = QFont("DM Sans")
    font.setPixelSize(58)
    font.setWeight(QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 97)
    p.setFont(font)
    p.setPen(QColor("#FFFFFF"))
    p.drawText(QRectF(96, 0, w - 96, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "luma")
    p.end()
    img.save(out)
    print(f"Marca de agua generada en {out}")


if __name__ == "__main__":
    main()
