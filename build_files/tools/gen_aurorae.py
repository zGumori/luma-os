#!/usr/bin/python3
"""Genera la decoración de ventana de Luma (temas Aurorae de KWin) en system_files.

Uso: python gen_aurorae.py   (desde cualquier sitio)

Crea dos temas: «Luma» (claro) y «LumaDark» (oscuro). Cada uno tiene:
- decoration.svg: marco de 9 piezas con sombra, bisel y esquinas redondeadas
  (variantes activa, inactiva y maximizada).
- minimize/maximize/restore/close.svg: segmentos de una misma píldora; con
  ButtonSpacing=0 se ven como un único control agrupado (docs/DESIGN.md).
Solo formas, degradados y opacidad: KWin dibuja estos SVG con QtSvg.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "system_files" / "usr" / "share" / "aurorae" / "themes"

PAD = 24          # espacio para la sombra alrededor de la ventana
R_TOP = 14        # radio de las esquinas superiores
R_BOTTOM = 7      # radio de las esquinas inferiores (el bisel es fino abajo)
BORDER = 5        # bisel lateral e inferior
EDGE = 8          # piezas estirables
BTN_W, BTN_H = 38, 30

THEMES = {
    "Luma": dict(
        title="Luma", fill="#F7F8FB", fill_inactive="#F1F2F6", line="#000000", line_alpha=0.13,
        highlight_alpha=0.9, shadow_alpha=0.24, shadow_inactive=0.12,
        text="20,22,28", text_inactive="140,145,160",
        pill="#FFFFFF", pill_line_alpha=0.10, hover="#ECEEF3", pressed="#E0E3EA",
        icon="#14161C", icon_inactive_alpha=0.45, close_hover="#FFE3E4", close_icon_hover="#E5323B",
    ),
    "LumaDark": dict(
        title="Luma Oscuro", fill="#1B1F2A", fill_inactive="#171A23", line="#FFFFFF", line_alpha=0.10,
        highlight_alpha=0.16, shadow_alpha=0.45, shadow_inactive=0.25,
        text="240,242,247", text_inactive="140,146,162",
        pill="#2A2F3D", pill_line_alpha=0.10, hover="#353B4C", pressed="#404759",
        icon="#F0F2F7", icon_inactive_alpha=0.45, close_hover="#4A2328", close_icon_hover="#FF6B72",
    ),
}


# ---------- Marco de la ventana ----------

def shadow_corner(cx, cy, r, alpha, gid):
    """Degradado radial de sombra centrado en el centro del arco de la esquina."""
    stop = r / (r + PAD)
    return (f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r + PAD}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#0A0E1E" stop-opacity="{alpha}"/>'
            f'<stop offset="{stop:.3f}" stop-color="#0A0E1E" stop-opacity="{alpha}"/>'
            f'<stop offset="1" stop-color="#0A0E1E" stop-opacity="0"/></radialGradient>')


def frame(prefix, t, active, maximized, oy):
    """Devuelve (defs, piezas) de un marco completo colocado a partir de y=oy."""
    defs, parts = [], []
    fill = t["fill"] if active else t["fill_inactive"]
    salpha = t["shadow_alpha"] if active else t["shadow_inactive"]
    line = f'fill="{t["line"]}" fill-opacity="{t["line_alpha"]}"'
    hl = f'fill="#FFFFFF" fill-opacity="{t["highlight_alpha"]}"'

    if maximized:
        # Sin sombra, sin bisel ni esquinas: un rectángulo plano
        for i, name in enumerate(["topleft", "top", "topright", "left", "center", "right",
                                  "bottomleft", "bottom", "bottomright"]):
            x = (i % 3) * (EDGE + 2)
            y = oy + (i // 3) * (EDGE + 2)
            parts.append(f'<rect id="{prefix}{name}" x="{x}" y="{y}" width="{EDGE}" height="{EDGE}" fill="{fill}"/>')
        return defs, parts, 3 * (EDGE + 2)

    # Columnas y filas de ancho uniforme: Plasma estira cada esquina al tamaño de su borde,
    # así que esquinas y bordes deben medir lo mismo. Lo que sobra queda bajo la ventana.
    W = PAD + R_TOP      # ancho de las columnas izquierda/derecha
    HT = PAD + R_TOP     # alto de la fila superior
    HB = PAD + R_BOTTOM  # alto de la fila inferior
    rt, rb = R_TOP, R_BOTTOM
    cols = [0, W + 2, W + EDGE + 4]
    rows = [oy, oy + HT + 2, oy + HT + EDGE + 4]
    uid = prefix.strip("-").replace("-", "_")

    def group(name, x, y, w, h, body):
        parts.append(f'<g id="{prefix}{name}" transform="translate({x},{y})">'
                     f'<rect x="0" y="0" width="{w}" height="{h}" fill="none"/>{body}</g>')

    def lin(gid, x1, y1, x2, y2):
        """Sombra lineal: opaca en (x2,y2), transparente en (x1,y1)."""
        defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" gradientUnits="userSpaceOnUse">'
                    f'<stop offset="0" stop-color="#0A0E1E" stop-opacity="0"/>'
                    f'<stop offset="1" stop-color="#0A0E1E" stop-opacity="{salpha}"/></linearGradient>')
        return f"url(#{gid})"

    def rad(gid, cx, cy, r):
        defs.append(shadow_corner(cx, cy, r, salpha, gid))
        return f"url(#{gid})"

    # Esquinas superiores (radio grande)
    group("topleft", cols[0], rows[0], W, HT,
          f'<rect x="0" y="0" width="{W}" height="{HT}" fill="{rad(f"sh_{uid}_tl", W, HT, rt)}"/>'
          f'<path d="M {PAD},{HT} A {rt},{rt} 0 0 1 {W},{PAD} L {W},{HT} Z" fill="{fill}"/>'
          f'<path d="M {PAD},{HT} A {rt},{rt} 0 0 1 {W},{PAD} L {W},{PAD + 1} A {rt - 1},{rt - 1} 0 0 0 {PAD + 1},{HT} Z" {hl}/>')
    group("topright", cols[2], rows[0], W, HT,
          f'<rect x="0" y="0" width="{W}" height="{HT}" fill="{rad(f"sh_{uid}_tr", 0, HT, rt)}"/>'
          f'<path d="M 0,{PAD} A {rt},{rt} 0 0 1 {rt},{HT} L 0,{HT} Z" fill="{fill}"/>'
          f'<path d="M 0,{PAD} A {rt},{rt} 0 0 1 {rt},{HT} L {rt - 1},{HT} A {rt - 1},{rt - 1} 0 0 0 0,{PAD + 1} Z" {hl}/>')

    # Esquinas inferiores (radio pequeño, dentro de una pieza tan ancha como la columna)
    cxl = PAD + rb       # centro del arco inferior izquierdo
    cxr = W - PAD - rb   # centro del arco inferior derecho
    group("bottomleft", cols[0], rows[2], W, HB,
          f'<rect x="0" y="0" width="{cxl}" height="{HB}" fill="{rad(f"sh_{uid}_bl", cxl, 0, rb)}"/>'
          f'<rect x="{cxl}" y="{rb}" width="{W - cxl}" height="{PAD}" fill="{lin(f"sh_{uid}_blv", 0, HB, 0, rb)}"/>'
          f'<rect x="{cxl}" y="0" width="{W - cxl}" height="{rb}" fill="{fill}"/>'
          f'<path d="M {PAD},0 A {rb},{rb} 0 0 0 {cxl},{rb} L {cxl},0 Z" fill="{fill}"/>'
          f'<path d="M {PAD},0 A {rb},{rb} 0 0 0 {cxl},{rb} L {cxl},{rb - 1} A {rb - 1},{rb - 1} 0 0 1 {PAD + 1},0 Z" {line}/>'
          f'<rect x="{cxl}" y="{rb - 1}" width="{W - cxl}" height="1" {line}/>')
    group("bottomright", cols[2], rows[2], W, HB,
          f'<rect x="{cxr}" y="0" width="{W - cxr}" height="{HB}" fill="{rad(f"sh_{uid}_br", cxr, 0, rb)}"/>'
          f'<rect x="0" y="{rb}" width="{cxr}" height="{PAD}" fill="{lin(f"sh_{uid}_brv", 0, HB, 0, rb)}"/>'
          f'<rect x="0" y="0" width="{cxr}" height="{rb}" fill="{fill}"/>'
          f'<path d="M {W - PAD},0 A {rb},{rb} 0 0 1 {cxr},{rb} L {cxr},0 Z" fill="{fill}"/>'
          f'<path d="M {W - PAD},0 A {rb},{rb} 0 0 1 {cxr},{rb} L {cxr},{rb - 1} A {rb - 1},{rb - 1} 0 0 0 {W - PAD - 1},0 Z" {line}/>'
          f'<rect x="0" y="{rb - 1}" width="{cxr}" height="1" {line}/>')

    # Bordes
    group("top", cols[1], rows[0], EDGE, HT,
          f'<rect x="0" y="0" width="{EDGE}" height="{PAD}" fill="{lin(f"sh_{uid}_t", 0, 0, 0, PAD)}"/>'
          f'<rect x="0" y="{PAD}" width="{EDGE}" height="{rt}" fill="{fill}"/>'
          f'<rect x="0" y="{PAD}" width="{EDGE}" height="1" {hl}/>')
    group("bottom", cols[1], rows[2], EDGE, HB,
          f'<rect x="0" y="0" width="{EDGE}" height="{rb}" fill="{fill}"/>'
          f'<rect x="0" y="{rb - 1}" width="{EDGE}" height="1" {line}/>'
          f'<rect x="0" y="{rb}" width="{EDGE}" height="{PAD}" fill="{lin(f"sh_{uid}_b", 0, HB, 0, rb)}"/>')
    group("left", cols[0], rows[1], W, EDGE,
          f'<rect x="0" y="0" width="{PAD}" height="{EDGE}" fill="{lin(f"sh_{uid}_l", 0, 0, PAD, 0)}"/>'
          f'<rect x="{PAD}" y="0" width="{rt}" height="{EDGE}" fill="{fill}"/>'
          f'<rect x="{PAD}" y="0" width="1" height="{EDGE}" {line}/>')
    group("right", cols[2], rows[1], W, EDGE,
          f'<rect x="0" y="0" width="{rt}" height="{EDGE}" fill="{fill}"/>'
          f'<rect x="{rt - 1}" y="0" width="1" height="{EDGE}" {line}/>'
          f'<rect x="{rt}" y="0" width="{PAD}" height="{EDGE}" fill="{lin(f"sh_{uid}_r", W, 0, rt, 0)}"/>')
    group("center", cols[1], rows[1], EDGE, EDGE, f'<rect x="0" y="0" width="{EDGE}" height="{EDGE}" fill="{fill}"/>')
    return defs, parts, rows[2] - oy + HB

def decoration_svg(t):
    defs, parts, y = [], [], 0
    for prefix, active, maximized in (("decoration-", True, False), ("decoration-inactive-", False, False),
                                      ("decoration-maximized-", True, True), ("decoration-maximized-inactive-", False, True)):
        d, p, h = frame(prefix, t, active, maximized, y)
        defs += d
        parts += p
        y += h + 8
    width = (PAD + R_TOP) * 2 + EDGE + 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}" viewBox="0 0 {width} {y}">\n'
            f'<defs>{"".join(defs)}</defs>\n' + "\n".join(parts) + "\n</svg>\n")


# ---------- Botones: segmentos de una píldora ----------

ICONS = {
    "minimize": '<path d="M13 15h12"/>',
    "maximize": '<rect x="13.5" y="9.5" width="11" height="11" rx="2.5"/>',
    "restore": '<rect x="12.5" y="11.5" width="9" height="9" rx="2"/><path d="M15.5 9.5h6a2 2 0 0 1 2 2v6"/>',
    "close": '<path d="M14 10l10 10M24 10L14 20"/>',
}
SEGMENT = {"minimize": "left", "maximize": "middle", "restore": "middle", "close": "right"}


def segment_path(kind, w, h):
    r = h / 2
    if kind == "left":
        return f"M {r},0 H {w} V {h} H {r} A {r},{r} 0 0 1 {r},0 Z"
    if kind == "right":
        return f"M 0,0 H {w - r} A {r},{r} 0 0 1 {w - r},{h} H 0 Z"
    return f"M 0,0 H {w} V {h} H 0 Z"


def outline(kind, w, h, attrs):
    """Filo exterior de la píldora (1 px) sin líneas entre segmentos."""
    r = h / 2
    if kind == "left":
        return (f'<path d="M {r},0 H {w} V 1 H {r} A {r - 1},{r - 1} 0 0 0 {r},{h - 1} H {w} V {h} H {r} '
                f'A {r},{r} 0 0 1 {r},0 Z" {attrs}/>')
    if kind == "right":
        return (f'<path d="M 0,0 H {w - r} A {r},{r} 0 0 1 {w - r},{h} H 0 V {h - 1} H {w - r} '
                f'A {r - 1},{r - 1} 0 0 0 {w - r},1 H 0 Z" {attrs}/>')
    return f'<rect x="0" y="0" width="{w}" height="1" {attrs}/><rect x="0" y="{h - 1}" width="{w}" height="1" {attrs}/>'


def button_svg(name, t):
    kind = SEGMENT[name]
    states = {
        "active": (t["pill"], t["icon"], 1.0),
        "hover": (t["close_hover"] if name == "close" else t["hover"],
                  t["close_icon_hover"] if name == "close" else t["icon"], 1.0),
        "pressed": (t["pressed"], t["close_icon_hover"] if name == "close" else t["icon"], 1.0),
        "inactive": (t["pill"], t["icon"], t["icon_inactive_alpha"]),
        "deactivated": (t["pill"], t["icon"], 0.3),
    }
    parts = []
    for i, (state, (bg, icon, alpha)) in enumerate(states.items()):
        y = i * (BTN_H + 4)
        line_attrs = f'fill="{t["line"]}" fill-opacity="{t["pill_line_alpha"]}"'
        parts.append(
            f'<g id="{state}-center" transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="{BTN_W}" height="{BTN_H}" fill="none"/>'
            f'<path d="{segment_path(kind, BTN_W, BTN_H)}" fill="{bg}"/>'
            f'{outline(kind, BTN_W, BTN_H, line_attrs)}'
            f'<g fill="none" stroke="{icon}" stroke-opacity="{alpha}" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g></g>')
    height = len(states) * (BTN_H + 4)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{BTN_W}" height="{height}" viewBox="0 0 {BTN_W} {height}">\n'
            + "\n".join(parts) + "\n</svg>\n")


def themerc(t):
    return f"""[General]
ActiveTextColor={t["text"]}
InactiveTextColor={t["text_inactive"]}
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=150
Shadow=false

[Layout]
BorderLeft={BORDER}
BorderRight={BORDER}
BorderBottom={BORDER}
TitleEdgeTop=8
TitleEdgeBottom=8
TitleEdgeLeft=12
TitleEdgeRight=12
TitleEdgeTopMaximized=4
TitleEdgeBottomMaximized=4
TitleEdgeLeftMaximized=8
TitleEdgeRightMaximized=8
TitleBorderLeft=10
TitleBorderRight=10
TitleHeight={BTN_H}
ButtonWidth={BTN_W}
ButtonHeight={BTN_H}
ButtonSpacing=0
ButtonMarginTop=0
ExplicitButtonSpacer=10
PaddingTop={PAD}
PaddingBottom={PAD}
PaddingLeft={PAD}
PaddingRight={PAD}
"""


def main():
    for key, t in THEMES.items():
        d = OUT / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "decoration.svg").write_text(decoration_svg(t), encoding="utf-8", newline="\n")
        for name in ICONS:
            (d / f"{name}.svg").write_text(button_svg(name, t), encoding="utf-8", newline="\n")
        (d / f"{key}rc").write_text(themerc(t), encoding="utf-8", newline="\n")
        (d / "metadata.desktop").write_text(
            f"[Desktop Entry]\nName={t['title']}\nComment=Decoración de ventana de Luma OS\n"
            f"X-KDE-PluginInfo-Author=Luma OS\nX-KDE-PluginInfo-Name={key}\nX-KDE-PluginInfo-Version=0.1\n"
            f"X-KDE-PluginInfo-License=GPL-2.0-or-later\nX-KDE-PluginInfo-Website=https://github.com/zGumori/luma-os\n",
            encoding="utf-8", newline="\n")
        (d / "metadata.json").write_text(json.dumps({"KPlugin": {
            "Id": key, "Name": t["title"], "Description": "Decoración de ventana de Luma OS",
            "Authors": [{"Name": "Luma OS"}], "License": "GPL-2.0-or-later", "Version": "0.1"}},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"Tema Aurorae generado: {d}")


if __name__ == "__main__":
    main()
