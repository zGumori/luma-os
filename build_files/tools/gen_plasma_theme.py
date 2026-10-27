#!/usr/bin/python3
"""Genera el estilo de Plasma "Luma" (cristal oscuro) en system_files.

Uso: python gen_plasma_theme.py   (desde la raíz del repo)

Plasma dibuja paneles y diálogos con SVG de 9 piezas (esquinas, bordes y centro).
Solo se generan las piezas que cambian; el resto cae en el tema Breeze por defecto.
Los SVG usan únicamente formas y opacidad (QtSvg no admite filtros ni clipPath).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / "system_files" / "usr" / "share" / "plasma" / "desktoptheme" / "luma"

NIGHT = "#14171F"
EDGE = 8  # tamaño de las piezas de borde y centro (se estiran)


def corner_paths(kind, r):
    """Relleno y borde de cada esquina, en coordenadas locales 0..r.

    El borde es un anillo relleno de 1 px (no un trazo): un trazo sobresale medio
    píxel de la pieza y Plasma deja de alinear esquinas y bordes, creando costuras.
    """
    q = r - 1
    return {
        "topleft": (f"M {r},0 A {r},{r} 0 0 0 0,{r} L {r},{r} Z",
                    f"M {r},0 A {r},{r} 0 0 0 0,{r} L 1,{r} A {q},{q} 0 0 1 {r},1 Z"),
        "topright": (f"M 0,0 A {r},{r} 0 0 1 {r},{r} L 0,{r} Z",
                     f"M 0,0 A {r},{r} 0 0 1 {r},{r} L {q},{r} A {q},{q} 0 0 0 0,1 Z"),
        "bottomleft": (f"M 0,0 A {r},{r} 0 0 0 {r},{r} L {r},0 Z",
                       f"M 0,0 A {r},{r} 0 0 0 {r},{r} L {r},{q} A {q},{q} 0 0 1 1,0 Z"),
        "bottomright": (f"M {r},0 A {r},{r} 0 0 1 0,{r} L 0,0 Z",
                        f"M {r},0 A {r},{r} 0 0 1 0,{r} L 0,{q} A {q},{q} 0 0 0 {q},0 Z"),
    }[kind]


def frame_svg(r, opacity, margins, prefixes=("",), border=0.10, highlight=0.18):
    """SVG de marco de 9 piezas, con versión de máscara (para el desenfoque de KWin)."""
    parts = []
    y = 0
    for prefix in list(prefixes) + ["mask-"]:
        is_mask = prefix == "mask-"
        fill = f'fill="{NIGHT if not is_mask else "#000000"}" fill-opacity="{1 if is_mask else opacity}"'
        cells = {
            "topleft": (0, 0, r, r), "top": (r + 2, 0, EDGE, r), "topright": (r + EDGE + 4, 0, r, r),
            "left": (0, r + 2, r, EDGE), "center": (r + 2, r + 2, EDGE, EDGE), "right": (r + EDGE + 4, r + 2, r, EDGE),
            "bottomleft": (0, r + EDGE + 4, r, r), "bottom": (r + 2, r + EDGE + 4, EDGE, r),
            "bottomright": (r + EDGE + 4, r + EDGE + 4, r, r),
        }
        for name, (cx, cy, w, h) in cells.items():
            ox, oy = cx, cy + y
            body = [f'<rect x="0" y="0" width="{w}" height="{h}" fill="none"/>']  # fija los límites de la pieza
            if name in ("topleft", "topright", "bottomleft", "bottomright"):
                fill_d, ring_d = corner_paths(name, r)
                body.append(f'<path d="{fill_d}" {fill}/>')
                if not is_mask:
                    alpha = highlight if name.startswith("top") else border
                    body.append(f'<path d="{ring_d}" fill="#FFFFFF" fill-opacity="{alpha}"/>')
            else:
                body.append(f'<rect x="0" y="0" width="{w}" height="{h}" {fill}/>')
                if not is_mask:
                    line = {
                        "top": (0, 0, w, 1, highlight), "bottom": (0, h - 1, w, 1, border),
                        "left": (0, 0, 1, h, border), "right": (w - 1, 0, 1, h, border),
                    }.get(name)
                    if line:
                        lx, ly, lw, lh, alpha = line
                        body.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="#FFFFFF" fill-opacity="{alpha}"/>')
            parts.append(f'  <g id="{prefix}{name}" transform="translate({ox},{oy})">' + "".join(body) + "</g>")
        y += 2 * r + EDGE + 8
    # Márgenes del contenido (independientes del radio de las esquinas)
    top, bottom, left, right = margins
    hints = [
        f'  <rect id="hint-top-margin" x="0" y="{y}" width="1" height="{top}" fill="none"/>',
        f'  <rect id="hint-bottom-margin" x="2" y="{y}" width="1" height="{bottom}" fill="none"/>',
        f'  <rect id="hint-left-margin" x="4" y="{y}" width="{left}" height="1" fill="none"/>',
        f'  <rect id="hint-right-margin" x="4" y="{y + 2}" width="{right}" height="1" fill="none"/>',
    ]
    width = 2 * r + EDGE + 8
    height = y + max(top, bottom) + 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
            + "\n".join(parts + hints) + "\n</svg>\n")


COLORS = """[Colors:Window]
BackgroundNormal=20,23,31
BackgroundAlternate=27,31,41
ForegroundNormal=240,242,247
ForegroundInactive=163,168,181
ForegroundActive=47,123,255
ForegroundLink=92,156,255
ForegroundVisited=167,139,250
ForegroundNegative=255,92,99
ForegroundNeutral=245,165,36
ForegroundPositive=52,211,140
DecorationFocus=47,123,255
DecorationHover=47,123,255

[Colors:Button]
BackgroundNormal=34,38,50
BackgroundAlternate=27,31,41
ForegroundNormal=240,242,247
ForegroundInactive=163,168,181
ForegroundActive=47,123,255
DecorationFocus=47,123,255
DecorationHover=47,123,255

[Colors:View]
BackgroundNormal=15,17,24
BackgroundAlternate=22,25,33
ForegroundNormal=240,242,247
ForegroundInactive=163,168,181
ForegroundActive=47,123,255
DecorationFocus=47,123,255
DecorationHover=47,123,255

[Colors:Selection]
BackgroundNormal=47,123,255
ForegroundNormal=255,255,255

[Colors:Tooltip]
BackgroundNormal=20,23,31
ForegroundNormal=240,242,247

[Colors:Complementary]
BackgroundNormal=20,23,31
ForegroundNormal=240,242,247
"""

PLASMARC = """# Efectos de KWin detrás de los paneles y diálogos del tema
[ContrastEffect]
enabled=true
contrast=0.25
intensity=0.9
saturation=1.8

[AdaptiveTransparency]
enabled=false
"""


def main():
    (THEME / "widgets").mkdir(parents=True, exist_ok=True)
    (THEME / "dialogs").mkdir(parents=True, exist_ok=True)
    (THEME / "widgets" / "panel-background.svg").write_text(frame_svg(16, 0.62, (5, 5, 10, 10)), encoding="utf-8", newline="\n")
    (THEME / "dialogs" / "background.svg").write_text(frame_svg(18, 0.80, (12, 12, 12, 12)), encoding="utf-8", newline="\n")
    (THEME / "widgets" / "tooltip.svg").write_text(frame_svg(12, 0.86, (8, 8, 10, 10)), encoding="utf-8", newline="\n")
    (THEME / "colors").write_text(COLORS, encoding="utf-8", newline="\n")
    (THEME / "plasmarc").write_text(PLASMARC, encoding="utf-8", newline="\n")
    metadata = {
        "KPlugin": {
            "Id": "luma",
            "Name": "Luma",
            "Description": "Cristal oscuro de Luma OS",
            "Authors": [{"Name": "Luma OS"}],
            "License": "GPL-2.0-or-later",
            "Version": "0.1",
            "Website": "https://github.com/zGumori/luma-os",
        },
        "X-Plasma-API-Minimum-Version": "6.0",
    }
    (THEME / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Tema generado en {THEME}")


if __name__ == "__main__":
    main()
