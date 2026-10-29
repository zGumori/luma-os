#!/usr/bin/python3
"""Genera el tema de cursor «Luma Pointer» (formato Xcursor) sin herramientas externas.

Uso: render_cursors.py <directorio de iconos>   → crea <dir>/LumaPointer

Diseño «Luma Glass» (docs/DESIGN.md): flecha estilizada de cristal oscuro con un filo
blanco nítido y lados ligeramente cóncavos, como las puntas de la estrella de Luma; sombra
suave dibujada a resolución completa. La espera es la estrella de Luma girando con el
degradado de la marca. Incluye flecha, mano, texto y espera/progreso animados; el resto
de cursores (redimensionar, etc.) se heredan de Breeze.
"""

import math
import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QTransform,
)

SIZES = (24, 32, 48, 64, 96)
FRAMES = 24
FRAME_DELAY = 40  # ms

# Material: cristal oscuro (tokens de docs/DESIGN.md)
GLASS_TOP = QColor("#2B3142")
GLASS_BOTTOM = QColor("#0C0E14")
RIM = QColor("#FFFFFF")
RIM_WIDTH = 1.7  # filo blanco, en la rejilla de 32
STAR_STOPS = [(0, "#5CA8FF"), (0.5, "#2F7BFF"), (1, "#8B5CF6")]


# ---------- Formas en una rejilla de 32×32 ----------

def arrow_path():
    """Flecha con lados cóncavos y puntas redondeadas."""
    p = QPainterPath(QPointF(6.0, 3.6))      # punta
    p.quadTo(7.0, 14.0, 7.6, 24.6)           # lado izquierdo, curvado hacia dentro
    p.quadTo(7.9, 25.9, 9.0, 25.0)           # punta inferior redondeada
    p.quadTo(11.0, 22.6, 13.0, 20.4)         # muesca
    p.quadTo(17.4, 19.6, 21.8, 19.6)         # ala derecha
    p.quadTo(23.2, 19.4, 22.2, 18.4)         # punta derecha redondeada
    p.quadTo(14.0, 11.0, 6.0, 3.6)           # lado derecho, curvado hacia dentro
    p.closeSubpath()
    return p


def hand_path():
    def rr(x1, y1, x2, y2, r):
        q = QPainterPath()
        q.addRoundedRect(QRectF(x1, y1, x2 - x1, y2 - y1), r, r)
        return q
    p = rr(11.6, 4.0, 15.0, 17.0, 1.7)               # índice
    p = p.united(rr(10.0, 13.6, 24.0, 27.0, 4.6))    # palma
    p = p.united(rr(15.2, 11.6, 18.6, 17.0, 1.7))    # corazón
    p = p.united(rr(18.8, 12.8, 22.2, 18.0, 1.7))    # anular
    thumb = rr(5.4, 16.2, 11.6, 19.6, 1.7)
    thumb = QTransform().translate(9, 17.9).rotate(38).translate(-9, -17.9).map(thumb)
    return p.united(thumb).simplified()


def beam_path():
    """Cursor de texto: barra con remates curvos, como un trazo de pluma."""
    p = QPainterPath(QPointF(12.2, 5.0))
    p.cubicTo(14.6, 5.0, 16.0, 6.0, 16.0, 8.2)
    p.lineTo(16.0, 23.8)
    p.cubicTo(16.0, 26.0, 14.6, 27.0, 12.2, 27.0)
    p.moveTo(19.8, 5.0)
    p.cubicTo(17.4, 5.0, 16.0, 6.0, 16.0, 8.2)
    p.moveTo(19.8, 27.0)
    p.cubicTo(17.4, 27.0, 16.0, 26.0, 16.0, 23.8)
    return p


def star_path(cx, cy, r, waist=0.22, angle=0.0):
    """Estrella de Luma de cuatro puntas con lados cóncavos."""
    tips = [QPointF(cx + r * math.cos(math.radians(angle + k * 90 - 90)),
                    cy + r * math.sin(math.radians(angle + k * 90 - 90))) for k in range(4)]
    w = r * waist
    p = QPainterPath(tips[0])
    for k in range(4):
        a = math.radians(angle + k * 90 - 45)
        p.quadTo(QPointF(cx + w * math.cos(a), cy + w * math.sin(a)), tips[(k + 1) % 4])
    p.closeSubpath()
    return p


# ---------- Dibujo ----------

def soft_shadow(p, path, s, dy=1.6, spread=2.6, alpha=0.30, layers=14):
    """Sombra suave a resolución completa: contornos cada vez más anchos y casi transparentes."""
    shape = QTransform().scale(s, s).translate(0, dy).map(path)
    p.save()
    p.setBrush(Qt.BrushStyle.NoBrush)
    for i in range(layers, 0, -1):
        t = i / layers
        pen = QPen(QColor(0, 0, 0, max(1, round(255 * alpha / layers))), 2 * spread * s * t ** 1.5)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.drawPath(shape)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(0, 0, 0, round(255 * alpha * 0.6)))
    p.drawPath(shape)
    p.restore()


def glass_shape(p, path, size, rim=RIM_WIDTH):
    """Filo blanco por fuera + cuerpo de cristal oscuro con reflejo superior."""
    s = size / 32
    soft_shadow(p, path, s)
    shape = QTransform().scale(s, s).map(path)
    bounds = shape.boundingRect()
    # Filo: el contorno ensanchado en blanco (uniones redondas = esquinas suaves)
    pen = QPen(RIM, 2 * rim * s)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(RIM)
    p.drawPath(shape)
    # Cuerpo de cristal
    body = QLinearGradient(bounds.topLeft(), bounds.bottomLeft())
    body.setColorAt(0, GLASS_TOP)
    body.setColorAt(1, GLASS_BOTTOM)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(body)
    p.drawPath(shape)
    # Reflejo: un velo blanco muy tenue en la mitad superior
    sheen = QLinearGradient(bounds.topLeft(), QPointF(bounds.left(), bounds.center().y()))
    sheen.setColorAt(0, QColor(255, 255, 255, 46))
    sheen.setColorAt(1, QColor(255, 255, 255, 0))
    p.setBrush(sheen)
    p.drawPath(shape)


def brand_star(p, cx, cy, r, s, angle):
    """Estrella de Luma con el degradado de la marca y filo blanco."""
    path = star_path(cx * s, cy * s, r * s, 0.22, angle)
    pen = QPen(RIM, 2 * 1.3 * s)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(RIM)
    p.drawPath(path)
    grad = QLinearGradient(QPointF((cx - r) * s, (cy - r) * s), QPointF((cx + r) * s, (cy + r) * s))
    for t, col in STAR_STOPS:
        grad.setColorAt(t, QColor(col))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(grad)
    p.drawPath(path)


def spin_angle(frame):
    """Un cuarto de vuelta por ciclo (la estrella es simétrica), lento al empezar y al acabar."""
    t = frame / FRAMES
    return 90 * (t - math.sin(2 * math.pi * t) / (2 * math.pi))


# ---------- Cursores ----------

def canvas(size):
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    return img, p


def cursor_arrow(size, frame=None):
    img, p = canvas(size)
    glass_shape(p, arrow_path(), size)
    if frame is not None:
        s = size / 32
        soft_shadow(p, star_path(24, 24.5, 6.6), s, dy=1.0, spread=1.6, alpha=0.25, layers=8)
        brand_star(p, 24, 24.5, 6.6, s, spin_angle(frame))
    p.end()
    return img


def cursor_hand(size, frame=None):
    img, p = canvas(size)
    glass_shape(p, hand_path(), size)
    p.end()
    return img


def cursor_text(size, frame=None):
    s = size / 32
    img, p = canvas(size)
    beam = beam_path()
    layers = ((QColor(0, 0, 0, 60), 7.6, 0.8), (RIM, 6.0, 0), (GLASS_BOTTOM, 2.6, 0))
    for color, width, dy in layers:
        pen = QPen(color, width * s)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.drawPath(QTransform().scale(s, s).translate(0, dy).map(beam))
    p.end()
    return img


def cursor_wait(size, frame=0):
    s = size / 32
    img, p = canvas(size)
    soft_shadow(p, star_path(16, 16, 12), s, dy=1.4, spread=2.0, alpha=0.28, layers=10)
    brand_star(p, 16, 16, 12, s, spin_angle(frame))
    p.end()
    return img


# nombre principal → (función, punto activo en la rejilla 32, animado, alias)
CURSORS = {
    "left_ptr": (cursor_arrow, (5.5, 2.4), False,
                 ["default", "arrow", "top_left_arrow", "left-arrow"]),
    "hand2": (cursor_hand, (13.3, 2.6), False,
              ["pointer", "hand1", "pointing_hand", "openhand", "9d800788f1b08800ae810202380a0822",
               "e29285e634086352946a0e7090d73106"]),
    "xterm": (cursor_text, (16, 16), False, ["text", "ibeam"]),
    "watch": (cursor_wait, (16, 16), True, ["wait"]),
    "left_ptr_watch": (cursor_arrow, (5.5, 2.4), True,
                       ["progress", "half-busy", "00000000000000020006000e7e9ffc3f",
                        "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"]),
}


# ---------- Escritura en formato Xcursor ----------

def xcursor(entries):
    """entries: lista de (tamaño nominal, QImage, xhot, yhot, delay). Devuelve los bytes del archivo."""
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, len(entries))
    toc_size = 12 * len(entries)
    pos = len(header) + toc_size
    toc, chunks = b"", b""
    for nominal, img, xh, yh, delay in entries:
        w, h = img.width(), img.height()
        pixels = bytes(img.constBits())[: w * h * 4]  # ARGB premultiplicado, little-endian
        chunk = struct.pack("<IIIIIIIII", 36, 0xFFFD0002, nominal, 1, w, h, xh, yh, delay) + pixels
        toc += struct.pack("<III", 0xFFFD0002, nominal, pos)
        pos += len(chunk)
        chunks += chunk
    return header + toc + chunks


def main():
    out = Path(sys.argv[1]) / "LumaPointer"
    cursors = out / "cursors"
    cursors.mkdir(parents=True, exist_ok=True)
    app = QGuiApplication(sys.argv[:1])  # noqa: F841 (necesaria para QPainter)
    for name, (fn, (hx, hy), animated, aliases) in CURSORS.items():
        entries = []
        for size in SIZES:
            s = size / 32
            frames = range(FRAMES) if animated else [None]
            for f in frames:
                img = fn(size, f) if f is not None else fn(size)
                entries.append((size, img, round(hx * s), round(hy * s), FRAME_DELAY if animated else 0))
        (cursors / name).write_bytes(xcursor(entries))
        for alias in aliases:
            link = cursors / alias
            if link.exists() or link.is_symlink():
                link.unlink()
            try:
                link.symlink_to(name)
            except OSError:  # Windows sin permisos de enlace: copia
                link.write_bytes((cursors / name).read_bytes())
    (out / "index.theme").write_text(
        "[Icon Theme]\nName=Luma Pointer\nComment=Cursor de Luma OS\nInherits=breeze_cursors\n",
        encoding="utf-8", newline="\n")
    (out / "cursor.theme").write_text("[Icon Theme]\nInherits=LumaPointer\n", encoding="utf-8", newline="\n")
    print(f"Cursor generado en {out}")


if __name__ == "__main__":
    main()
