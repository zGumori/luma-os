#!/usr/bin/python3
"""Genera el tema de cursor «Luma Pointer» (formato Xcursor) sin herramientas externas.

Uso: render_cursors.py <directorio de iconos>   → crea <dir>/LumaPointer

Diseño (docs/DESIGN.md): flecha grande y redondeada, relleno blanco, contorno negro
grueso y sombra suave. Incluye flecha, mano, texto y espera/progreso animados; el
resto de cursores (redimensionar, etc.) se heredan de Breeze.
"""

import math
import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPainterPath, QPen, QTransform  # noqa: E402

SIZES = (24, 32, 48, 64, 96)
ACCENT = QColor("#2F7BFF")
FRAMES = 12
FRAME_DELAY = 55  # ms


# ---------- Formas en una rejilla de 32×32 ----------
# Estilo de la referencia: punta de flecha sin tallo, con muesca en la base, esquinas muy
# redondeadas, contorno negro grueso y relleno blanco. Cada forma se define por un «núcleo»
# más pequeño: el contorno y el redondeo salen de trazarlo con lápiz grueso y uniones redondas.

INK = QColor("#0E1014")
ROUND = 1.5    # radio de redondeo del relleno blanco
OUTLINE = 2.3  # grosor del contorno negro


def arrow_core():
    p = QPainterPath(QPointF(8.2, 7.4))           # punta
    for x, y in ((8.8, 23.6), (13.6, 19.2), (22.6, 18.4)):  # ala izq. · muesca · ala der.
        p.lineTo(x, y)
    p.closeSubpath()
    return p


def hand_core():
    def rr(x1, y1, x2, y2, r):
        q = QPainterPath()
        q.addRoundedRect(QRectF(x1, y1, x2 - x1, y2 - y1), r, r)
        return q
    p = rr(12.2, 5.6, 14.6, 17, 1.2)              # índice
    p = p.united(rr(10.4, 14.5, 23.2, 25.6, 3.4)) # palma
    p = p.united(rr(15.8, 13, 18.2, 17, 1.2))     # corazón
    p = p.united(rr(19.4, 14, 21.8, 18, 1.2))     # anular
    thumb = rr(6.2, 16.2, 11.2, 18.6, 1.2)
    thumb = QTransform().translate(9, 17.4).rotate(40).translate(-9, -17.4).map(thumb)
    return p.united(thumb).simplified()


def soft_shadow(p, path, size, s, dy=1.8, alpha=70):
    """Sombra difuminada de verdad: se dibuja a 1/4 de resolución y se amplía suavemente."""
    small = max(8, size // 4)
    k = small / size
    img = QImage(small, small, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    q = QPainter(img)
    q.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(0, 0, 0, alpha), 2 * (ROUND + OUTLINE + 0.6) * s * k)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    q.setPen(pen)
    q.setBrush(QColor(0, 0, 0, alpha))
    q.drawPath(QTransform().scale(s * k, s * k).translate(0, dy).map(path))
    q.end()
    p.drawImage(0, 0, img.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation))


def draw_shape(p, core, size, fill="#FFFFFF"):
    """Sombra + contorno negro grueso + relleno blanco, con esquinas redondeadas."""
    s = size / 32
    soft_shadow(p, core, size, s)
    scaled = QTransform().scale(s, s).map(core)
    for color, width in ((INK, ROUND + OUTLINE), (QColor(fill), ROUND)):
        pen = QPen(color, 2 * width * s)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(color)
        p.drawPath(scaled)


def spinner(p, cx, cy, r, s, frame, ring=OUTLINE):
    """Disco blanco de contorno grueso con un arco de acento que gira."""
    p.setPen(QPen(INK, ring * s))
    p.setBrush(QColor("#FFFFFF"))
    p.drawEllipse(QPointF(cx * s, cy * s), r * s, r * s)
    pen = QPen(ACCENT, max(2.0, r * 0.42) * s)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    rr = r * 0.52
    start = -int(frame * 360 / FRAMES * 16)
    p.drawArc(QRectF((cx - rr) * s, (cy - rr) * s, 2 * rr * s, 2 * rr * s), start, 110 * 16)


# ---------- Cursores ----------

def canvas(size):
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    return img, p


def cursor_arrow(size, frame=None):
    img, p = canvas(size)
    draw_shape(p, arrow_core(), size)
    if frame is not None:
        spinner(p, 23.5, 24, 5.6, size / 32, frame)
    p.end()
    return img


def cursor_hand(size, frame=None):
    img, p = canvas(size)
    draw_shape(p, hand_core(), size)
    p.end()
    return img


def cursor_text(size, frame=None):
    s = size / 32
    img, p = canvas(size)
    beam = QPainterPath(QPointF(12, 5))
    beam.cubicTo(14.5, 5, 16, 6, 16, 8)
    beam.lineTo(16, 24)
    beam.cubicTo(16, 26, 14.5, 27, 12, 27)
    beam.moveTo(20, 5)
    beam.cubicTo(17.5, 5, 16, 6, 16, 8)
    beam.moveTo(20, 27)
    beam.cubicTo(17.5, 27, 16, 26, 16, 24)
    beam.moveTo(13.5, 16)
    beam.lineTo(18.5, 16)
    t = QTransform().scale(s, s)
    for color, width in (("#FFFFFF", 7.0), ("#0E1014", 3.0)):
        pen = QPen(QColor(color), width * s)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.drawPath(t.map(beam))
    p.end()
    return img


def cursor_wait(size, frame=0):
    s = size / 32
    img, p = canvas(size)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QPointF(16.6 * s, 17.4 * s), 12 * s, 12 * s)
    spinner(p, 16, 16, 11, s, frame)
    p.end()
    return img


# nombre principal → (función, punto activo en la rejilla 32, animado, alias)
CURSORS = {
    "left_ptr": (cursor_arrow, (5.6, 4.4), False,
                 ["default", "arrow", "top_left_arrow", "left-arrow"]),
    "hand2": (cursor_hand, (13.4, 2.4), False,
              ["pointer", "hand1", "pointing_hand", "openhand", "9d800788f1b08800ae810202380a0822",
               "e29285e634086352946a0e7090d73106"]),
    "xterm": (cursor_text, (16, 16), False, ["text", "ibeam"]),
    "watch": (cursor_wait, (16, 16), True, ["wait"]),
    "left_ptr_watch": (cursor_arrow, (5.6, 4.4), True,
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
