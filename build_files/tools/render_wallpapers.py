#!/usr/bin/python3
"""Genera los fondos de pantalla de Luma OS como paquetes de Plasma.

Uso: render_wallpapers.py <directorio de salida> [ancho alto]

Crea <salida>/Luma con la versión clara (contents/images) y oscura
(contents/images_dark): Plasma cambia entre ellas según el esquema de color.
Los fondos son propios de Luma: formas luminosas suaves (esfera, cintas de luz,
destello de estrella) siguiendo docs/DESIGN.md.
"""

import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient,
)


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


def glow(p, cx, cy, radius, hex_value, alpha):
    g = QRadialGradient(cx, cy, radius)
    g.setColorAt(0, color(hex_value, alpha))
    g.setColorAt(1, color(hex_value, 0))
    p.setBrush(QBrush(g))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx, cy), radius, radius)


def ribbon(p, path, hex_value, width, strength=1.0):
    """Cinta de luz: muchas pasadas de trazo con anchura y opacidad graduales simulan el resplandor."""
    steps = 24
    for i in range(steps):
        t = i / (steps - 1)  # 0 = halo exterior, 1 = núcleo
        w = width * (0.4 + 7.0 * (1 - t) ** 2)
        a = 4 + 26 * t ** 3
        pen = QPen(color(hex_value, int(a * strength)), w)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)


def render_day(w, h):
    img = QImage(w, h, QImage.Format.Format_RGBX64)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    s = h / 2160

    sky = QLinearGradient(0, 0, w * 0.4, h)
    sky.setColorAt(0, QColor("#F2F8FF"))
    sky.setColorAt(0.55, QColor("#CFE4FF"))
    sky.setColorAt(1, QColor("#A9CBFF"))
    p.fillRect(img.rect(), sky)

    glow(p, w * 0.18, h * 0.12, 900 * s, "#FFFFFF", 200)

    # Esfera de cristal azul, parcialmente fuera de la pantalla
    cx, cy, r = w * 0.80, h * 0.58, 820 * s
    glow(p, cx, cy, r * 1.35, "#3D8BFF", 70)
    body = QRadialGradient(cx - r * 0.35, cy - r * 0.45, r * 1.6)
    body.setColorAt(0.0, QColor("#B9DCFF"))
    body.setColorAt(0.25, QColor("#5AA2FF"))
    body.setColorAt(0.6, QColor("#1E5BFF"))
    body.setColorAt(1.0, QColor("#0A2A8C"))
    p.setBrush(QBrush(body))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx, cy), r, r)
    # Brillo especular y borde iluminado
    spec = QRadialGradient(cx - r * 0.38, cy - r * 0.5, r * 0.55)
    spec.setColorAt(0, color("#FFFFFF", 150))
    spec.setColorAt(1, color("#FFFFFF", 0))
    p.setBrush(QBrush(spec))
    p.drawEllipse(QPointF(cx, cy), r, r)
    rim = QPen(color("#FFFFFF", 90), 6 * s)
    p.setPen(rim)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(QRectF(cx - r, cy - r, 2 * r, 2 * r), 95 * 16, 110 * 16)

    # Arcos finos de luz que cruzan la pantalla
    for i, (alpha, off) in enumerate([(150, 0), (90, 140), (55, 290)]):
        arc = QPainterPath(QPointF(-200 * s, h * (0.98 - i * 0.03)))
        arc.cubicTo(w * 0.25, h * (0.55 - i * 0.05) + off * s * 0.2, w * 0.55, h * 0.25 + off * s, w + 200 * s, h * (0.08 + i * 0.06))
        pen = QPen(color("#FFFFFF", alpha), (3.2 - i) * s)
        p.setPen(pen)
        p.drawPath(arc)

    # Destello de estrella sutil
    p.setPen(Qt.PenStyle.NoPen)
    glow(p, w * 0.14, h * 0.2, 120 * s, "#FFFFFF", 160)
    p.setBrush(color("#FFFFFF", 235))
    p.drawPath(star_path(w * 0.14, h * 0.2, 70 * s, 50 * s, 6 * s))
    p.end()
    return finish(img)


def render_night(w, h):
    img = QImage(w, h, QImage.Format.Format_RGBX64)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    s = h / 2160

    sky = QLinearGradient(0, 0, w * 0.3, h)
    sky.setColorAt(0, QColor("#05070F"))
    sky.setColorAt(0.6, QColor("#0B1024"))
    sky.setColorAt(1, QColor("#1A0F2E"))
    p.fillRect(img.rect(), sky)

    glow(p, w * 0.75, h * 0.95, 1300 * s, "#8B5CF6", 60)
    glow(p, w * 0.2, h * 0.9, 900 * s, "#F5A524", 28)

    # Cintas de luz que entran desde la izquierda y se curvan
    def band(y0, y1, y2, y3, x2f, x3f):
        path = QPainterPath(QPointF(-300 * s, h * y0))
        path.cubicTo(w * 0.35, h * y1, w * x2f, h * y2, w * x3f, h * y3)
        return path

    ribbon(p, band(0.36, 0.30, 0.58, 0.62, 0.62, 1.05), "#FF8A1F", 26 * s, 1.0)
    ribbon(p, band(0.52, 0.45, 0.80, 0.86, 0.70, 1.08), "#F5A524", 14 * s, 0.75)
    ribbon(p, band(0.22, 0.20, 0.42, 0.40, 0.55, 1.06), "#FF5A3C", 10 * s, 0.55)
    ribbon(p, band(0.70, 0.66, 0.95, 1.05, 0.52, 0.95), "#8B5CF6", 18 * s, 0.6)

    # Estrellas lejanas
    p.setPen(Qt.PenStyle.NoPen)
    seed = 7
    for _ in range(140):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = (seed % 10000) / 10000 * w
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        y = (seed % 10000) / 10000 * h * 0.7
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        r = (0.6 + (seed % 100) / 100 * 1.8) * s
        p.setBrush(color("#FFFFFF", 70 + seed % 120))
        p.drawEllipse(QPointF(x, y), r, r)

    # Destello de Luma
    glow(p, w * 0.82, h * 0.18, 260 * s, "#9DB8FF", 120)
    p.setBrush(color("#FFFFFF", 245))
    p.drawPath(star_path(w * 0.82, h * 0.18, 110 * s, 80 * s, 9 * s))
    p.setBrush(color("#FFFFFF", 200))
    p.drawPath(star_path(w * 0.82 + 120 * s, h * 0.18 - 95 * s, 34 * s, 26 * s, 3 * s))
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
    (root / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")


def main():
    out = sys.argv[1]
    w, h = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (3840, 2160)
    app = QGuiApplication(sys.argv[:1])  # noqa: F841 (necesaria para QPainter)
    write_package(out, "Luma", "Luma", render_day(w, h), render_night(w, h))
    print(f"Fondos generados en {out}/Luma ({w}x{h})")


if __name__ == "__main__":
    main()
