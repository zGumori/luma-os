#!/usr/bin/python3
"""Genera el fondo de pantalla de Luma OS («Destello») como paquete de Plasma.

Uso: render_wallpapers.py <directorio de salida> [ancho alto]

Crea <salida>/Luma con la versión clara (contents/images) y oscura
(contents/images_dark): Plasma cambia entre ellas según el esquema de color.

«Destello»: una estrella de Luma gigante, recortada por el borde y rellena de luz,
con un resplandor difuminado y una estrella pequeña y nítida que la acompaña.
Minimalista, abstracto y propio de Luma (docs/DESIGN.md).
"""

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QRadialGradient,
)

PALETTES = {
    False: dict(  # claro: azul sobre blanco cálido
        bg=("#F6F4F0", "#ECEAE4"), glow="#5B8CFF", glow_alpha=150,
        stops=[(0, "#DCEBFF"), (0.4, "#7FB0FF"), (0.75, "#2F6BFF"), (1, "#5B3BE0")], small="#1A1D29"),
    True: dict(  # oscuro: luz cálida de naranja a magenta sobre negro
        bg=("#07080D", "#0B0C14"), glow="#FF7A45", glow_alpha=210,
        stops=[(0, "#FFD29A"), (0.35, "#FF7A45"), (0.7, "#E8366F"), (1, "#5B2BD9")], small="#FFFFFF"),
}


def color(hex_value, alpha=255):
    c = QColor(hex_value)
    c.setAlpha(alpha)
    return c


def star_path(cx, cy, r_v, r_h, waist):
    """Destello de cuatro puntas con lados cóncavos (la estrella de Luma)."""
    p = QPainterPath(QPointF(cx, cy - r_v))
    p.quadTo(cx + waist, cy - waist, cx + r_h, cy)
    p.quadTo(cx + waist, cy + waist, cx, cy + r_v)
    p.quadTo(cx - waist, cy + waist, cx - r_h, cy)
    p.quadTo(cx - waist, cy - waist, cx, cy - r_v)
    return p


def blur(img, factor=40):
    """Desenfoque amplio: reduce en varios pasos y vuelve a ampliar suavemente."""
    w, h = img.width(), img.height()
    small = img
    for k in (2, 4, 8, factor):
        small = small.scaled(max(2, w // k), max(2, h // k), Qt.AspectRatioMode.IgnoreAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)
    for k in (8, 4, 2, 1):
        small = small.scaled(w // k, h // k, Qt.AspectRatioMode.IgnoreAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)
    return small


def render(w, h, dark):
    pal = PALETTES[dark]
    s = h / 1080
    # Lienzo de 16 bits por canal para degradados limpios
    img = QImage(w, h, QImage.Format.Format_RGBX64)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    bg = QLinearGradient(0, 0, 0, h)
    bg.setColorAt(0, QColor(pal["bg"][0]))
    bg.setColorAt(1, QColor(pal["bg"][1]))
    p.fillRect(img.rect(), bg)

    cx, cy = w * 0.70, h * 0.62
    shape = star_path(cx, cy, h * 0.95, h * 0.70, h * 0.075)

    # Resplandor difuminado detrás de la estrella
    glow = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    glow.fill(Qt.GlobalColor.transparent)
    g = QPainter(glow)
    g.setRenderHint(QPainter.RenderHint.Antialiasing)
    g.setPen(Qt.PenStyle.NoPen)
    g.setBrush(color(pal["glow"], pal["glow_alpha"]))
    g.drawPath(shape)
    g.end()
    p.drawImage(0, 0, blur(glow))

    # Estrella rellena de luz
    grad = QLinearGradient(cx - h * 0.4, cy - h * 0.9, cx + h * 0.3, cy + h * 0.9)
    for t, col in pal["stops"]:
        grad.setColorAt(t, QColor(col))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(grad))
    p.drawPath(shape)
    highlight = QRadialGradient(cx - h * 0.05, cy - h * 0.35, h * 0.5)
    highlight.setColorAt(0, color("#FFFFFF", 90))
    highlight.setColorAt(1, color("#FFFFFF", 0))
    p.setBrush(QBrush(highlight))
    p.drawPath(shape)

    # Estrella compañera, pequeña y nítida
    p.setBrush(color(pal["small"], 235))
    p.drawPath(star_path(w * 0.36, h * 0.15, 44 * s, 34 * s, 3.5 * s))
    p.end()
    return finish(img)


def grain_tile(size=256, seed=11):
    """Tesela de grano: píxeles blancos/negros casi transparentes que rompen las bandas de 8 bits."""
    tile = QImage(size, size, QImage.Format.Format_ARGB32)
    for y in range(size):
        for x in range(size):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            v = (seed >> 8) & 0xFF
            a = abs(v - 128) // 26  # 0..4
            tile.setPixelColor(x, y, QColor(255, 255, 255, a) if v > 127 else QColor(0, 0, 0, a))
    return tile


def finish(img):
    """Añade grano fino y pasa a 8 bits por canal."""
    p = QPainter(img)
    p.fillRect(img.rect(), QBrush(grain_tile()))
    p.end()
    return img.convertToFormat(QImage.Format.Format_RGB32)


def write_package(out, name, title, day, night):
    root = Path(out) / name
    (root / "contents" / "images").mkdir(parents=True, exist_ok=True)
    (root / "contents" / "images_dark").mkdir(parents=True, exist_ok=True)
    size = f"{day.width()}x{day.height()}"
    day.save(str(root / "contents" / "images" / f"{size}.jpg"), "JPG", 93)
    night.save(str(root / "contents" / "images_dark" / f"{size}.jpg"), "JPG", 93)
    day.scaled(800, 450, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation) \
        .save(str(root / "contents" / "screenshot.png"))
    metadata = {
        "KPlugin": {
            "Id": name,
            "Name": title,
            "Authors": [{"Name": "Luma OS"}],
            "License": "CC-BY-SA-4.0",
        }
    }
    (root / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    out = sys.argv[1]
    w, h = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (3840, 2160)
    app = QGuiApplication(sys.argv[:1])  # noqa: F841 (necesaria para QPainter)
    write_package(out, "Luma", "Luma · Destello", render(w, h, False), render(w, h, True))
    print(f"Fondos generados en {out}/Luma ({w}x{h})")


if __name__ == "__main__":
    main()
