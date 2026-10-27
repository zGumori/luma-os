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

def arrow_path():
    p = QPainterPath(QPointF(4, 2.5))
    for x, y in ((4, 24.5), (9.3, 19.6), (13.2, 28), (16.8, 26.4), (12.9, 18.2), (20.2, 18.2)):
        p.lineTo(x, y)
    p.closeSubpath()
    return p


def hand_path():
    def rr(x1, y1, x2, y2, r):
        q = QPainterPath()
        q.addRoundedRect(QRectF(x1, y1, x2 - x1, y2 - y1), r, r)
        return q
    p = rr(11, 2.5, 15.6, 18, 2.3)              # índice
    p = p.united(rr(8.5, 13.5, 25, 29, 5))      # palma
    p = p.united(rr(15.2, 11, 19.4, 18, 2.1))   # corazón
    p = p.united(rr(19, 12.5, 23.2, 19.5, 2.1)) # anular
    p = p.united(rr(22.4, 14.5, 25.6, 21, 1.6)) # meñique
    thumb = rr(4, 15, 10.5, 19.6, 2.3)
    thumb = QTransform().translate(7, 17).rotate(38).translate(-7, -17).map(thumb)
    return p.united(thumb).simplified()


def draw_shape(p, path, s, fill="#FFFFFF", outline=2.2):
    """Sombra suave + relleno + contorno negro redondeado, escalados por s."""
    t = QTransform().scale(s, s)
    scaled = t.map(path)
    for i, a in enumerate((18, 26, 40)):
        pen = QPen(QColor(0, 0, 0, a), (outline + 3.2 - i) * s)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(QColor(0, 0, 0, a))
        p.drawPath(QTransform().translate(0.6 * s, 1.4 * s).map(scaled))
    pen = QPen(QColor("#111318"), outline * s)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(QColor(fill))
    p.drawPath(scaled)


def spinner(p, cx, cy, r, s, frame, ring=2.0):
    """Disco blanco con un arco de acento que gira."""
    p.setPen(QPen(QColor("#111318"), ring * s))
    p.setBrush(QColor("#FFFFFF"))
    p.drawEllipse(QPointF(cx * s, cy * s), r * s, r * s)
    pen = QPen(ACCENT, max(2.0, r * 0.42) * s)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    rr = r * 0.55
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
    s = size / 32
    img, p = canvas(size)
    draw_shape(p, arrow_path(), s)
    if frame is not None:
        spinner(p, 23, 23, 6.2, s, frame, ring=1.6)
    p.end()
    return img


def cursor_hand(size, frame=None):
    s = size / 32
    img, p = canvas(size)
    draw_shape(p, hand_path(), s, outline=2.0)
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
    for color, width in (("#FFFFFF", 5.2), ("#111318", 2.2)):
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
    spinner(p, 16, 16, 11, s, frame, ring=2.2)
    p.end()
    return img


# nombre principal → (función, punto activo en la rejilla 32, animado, alias)
CURSORS = {
    "left_ptr": (cursor_arrow, (4, 2.5), False,
                 ["default", "arrow", "top_left_arrow", "left-arrow"]),
    "hand2": (cursor_hand, (13.3, 3), False,
              ["pointer", "hand1", "pointing_hand", "openhand", "9d800788f1b08800ae810202380a0822",
               "e29285e634086352946a0e7090d73106"]),
    "xterm": (cursor_text, (16, 16), False, ["text", "ibeam"]),
    "watch": (cursor_wait, (16, 16), True, ["wait"]),
    "left_ptr_watch": (cursor_arrow, (4, 2.5), True,
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
