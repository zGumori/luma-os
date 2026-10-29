#!/usr/bin/python3
"""Genera el tema Kvantum «Luma» (cristal claro y oscuro en las ventanas) en system_files.

Uso: python gen_kvantum.py   (desde cualquier sitio)

Kvantum dibuja los controles de las apps Qt (botones, campos, listas, menús…) con
piezas de un SVG. Cada control se compone de 9 piezas (esquinas, bordes y centro)
por estado: normal, focused (hover), pressed y toggled. El grosor de cada marco
en el .kvconfig coincide con el tamaño de la pieza, así que las esquinas se ven
a 1:1. Si falta una pieza, Kvantum usa la de su tema por defecto (oscuro y gris),
por eso aquí se generan todas las que se usan, aunque sean transparentes.

Se crea un tema por color de acento (los mismos que ofrece la Bienvenida), cada
uno con su variante oscura dentro de la misma carpeta, como pide Kvantum:
/usr/share/Kvantum/Luma/Luma.kvconfig y .../Luma/LumaDark.kvconfig, etc.
Diseño: docs/DESIGN.md → «Cristal claro». Solo formas y opacidad (QtSvg).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "system_files" / "usr" / "share" / "Kvantum"

EDGE = 8  # tamaño de las piezas estirables (bordes y centro)

# Nombre del tema → acento (docs/DESIGN.md → Acentos seleccionables)
ACCENTS = {
    "Luma": "#2F7BFF",
    "LumaCian": "#14B8E6",
    "LumaVioleta": "#8B5CF6",
    "LumaRosa": "#F0457A",
    "LumaAmbar": "#F5A524",
    "LumaVerde": "#21C07A",
}

LIGHT = dict(
    dark=False,
    window="#F7F8FB", window_alpha=0.74, window_alpha_inactive=0.86,
    ink="#14161C", ink2="#6B7080", ink3="#A3A8B5", line="#000000",
    button="#FFFFFF", button_alpha=0.80, button_hover=0.98, button_line=0.11, button_line_hover=0.17,
    pressed="#E4E7EE", pressed_alpha=1.0,
    field="#FFFFFF", field_alpha=0.85, field_line=0.13,
    soft="#000000",  # rellenos suaves (hover de botones planos, pistas)
    menu="#FBFCFE", menu_alpha=0.84, menu_line=0.10,
    card="#FFFFFF", card_alpha=0.45, card_line=0.08,
    tab_on="#FFFFFF", tab_on_alpha=0.95,
    groove=0.13, scroll=0.28, scroll_hover=0.42, scroll_press=0.52,
    check="#FFFFFF", check_alpha=1.0, check_line=0.28,
    knob="#FFFFFF", knob_line=0.20,
    base="#FFFFFF", base_alpha="cc", alt_base="#F3F5F9",
)

DARK = dict(
    dark=True,
    window="#1A1E28", window_alpha=0.78, window_alpha_inactive=0.90,
    ink="#F0F2F7", ink2="#A3A8B5", ink3="#6B7080", line="#FFFFFF",
    button="#FFFFFF", button_alpha=0.08, button_hover=0.13, button_line=0.10, button_line_hover=0.16,
    pressed="#FFFFFF", pressed_alpha=0.04,
    field="#000000", field_alpha=0.26, field_line=0.12,
    soft="#FFFFFF",
    menu="#1E2230", menu_alpha=0.88, menu_line=0.10,
    card="#FFFFFF", card_alpha=0.05, card_line=0.08,
    tab_on="#FFFFFF", tab_on_alpha=0.13,
    groove=0.16, scroll=0.30, scroll_hover=0.44, scroll_press=0.54,
    check="#FFFFFF", check_alpha=0.06, check_line=0.32,
    knob="#F0F2F7", knob_line=0.0,
    base="#12151D", base_alpha="cc", alt_base="#181C26",
)

NIGHT = "#14171F"  # avisos (tooltips): siempre cristal oscuro, como el sistema


def shade(color, factor):
    """Oscurece (factor < 1) o aclara (factor > 1) un color #RRGGBB."""
    c = color.lstrip("#")
    rgb = [int(c[i:i + 2], 16) for i in (0, 2, 4)]
    if factor < 1:
        rgb = [round(v * factor) for v in rgb]
    else:
        rgb = [round(v + (255 - v) * (factor - 1)) for v in rgb]
    return "#" + "".join(f"{max(0, min(255, v)):02X}" for v in rgb)


class Sheet:
    """Coloca grupos en filas dentro del SVG; cada grupo fija sus límites con un rect invisible."""

    def __init__(self):
        self.parts = []
        self.x = self.y = self.row_h = 0
        self.width = 640

    def group(self, gid, w, h, body):
        if self.x + w > self.width:
            self.x, self.y, self.row_h = 0, self.y + self.row_h + 4, 0
        self.parts.append(f'<g id="{gid}" transform="translate({self.x},{self.y})">'
                          f'<rect x="0" y="0" width="{w}" height="{h}" fill="none"/>{body}</g>')
        self.x += w + 4
        self.row_h = max(self.row_h, h)

    def svg(self):
        height = self.y + self.row_h + 4
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height}" '
                f'viewBox="0 0 {self.width} {height}">\n' + "\n".join(self.parts) + "\n</svg>\n")


def paint(color, alpha):
    return f'fill="{color}" fill-opacity="{alpha:g}"'


def corner(f, m, r, b, fill, line):
    """Esquina superior izquierda de f×f: forma desde (m,m) con radio r y filo de b px."""
    body = ""
    if fill:
        body += f'<path d="M {m},{f} L {m},{m + r} A {r},{r} 0 0 1 {m + r},{m} L {f},{m} L {f},{f} Z" {fill}/>'
    if line and b:
        ri = max(r - b, 0)
        body += (f'<path fill-rule="evenodd" d="M {m},{f} L {m},{m + r} A {r},{r} 0 0 1 {m + r},{m} L {f},{m} '
                 f'L {f},{f} Z M {m + b},{f} L {m + b},{m + b + ri} A {ri},{ri} 0 0 1 {m + b + ri},{m + b} '
                 f'L {f},{m + b} L {f},{f} Z" {line}/>')
    return body


def box(sheet, base, f, style, m=0, r=None):
    """Marco de 9 piezas: {base}-top…{base}-bottomright y el interior {base}.

    style = (relleno, alfa, color del filo, alfa del filo, grosor del filo).
    m deja un margen transparente alrededor (la forma queda separada del borde).
    """
    fill_c, fill_a, line_c, line_a, b = style
    r = f - m if r is None else r
    fill = paint(fill_c, fill_a) if fill_a else ""
    line = paint(line_c, line_a) if line_a and b else ""
    tl = corner(f, m, r, b, fill, line)
    mirror = {"topleft": "", "topright": f"translate({f},0) scale(-1,1)",
              "bottomleft": f"translate(0,{f}) scale(1,-1)", "bottomright": f"translate({f},{f}) scale(-1,-1)"}
    for pos, tf in mirror.items():
        sheet.group(f"{base}-{pos}", f, f, f'<g transform="{tf}">{tl}</g>' if tf else tl)
    # Bordes: banda de relleno desde el margen y línea del filo pegada a él
    edges = {
        "top": (EDGE, f, (0, m, EDGE, f - m), (0, m, EDGE, b)),
        "bottom": (EDGE, f, (0, 0, EDGE, f - m), (0, f - m - b, EDGE, b)),
        "left": (f, EDGE, (m, 0, f - m, EDGE), (m, 0, b, EDGE)),
        "right": (f, EDGE, (0, 0, f - m, EDGE), (f - m - b, 0, b, EDGE)),
    }
    for pos, (w, h, frect, lrect) in edges.items():
        body = ""
        if fill:
            body += '<rect x="{}" y="{}" width="{}" height="{}" '.format(*frect) + fill + "/>"
        if line:
            body += '<rect x="{}" y="{}" width="{}" height="{}" '.format(*lrect) + line + "/>"
        sheet.group(f"{base}-{pos}", w, h, body)
    sheet.group(base, EDGE, EDGE, f'<rect x="0" y="0" width="{EDGE}" height="{EDGE}" {fill}/>' if fill else "")


def states(sheet, name, f, table, m=0, r=None):
    """Un box() por estado: table = {estado: estilo}."""
    for state, style in table.items():
        box(sheet, f"{name}-{state}", f, style, m, r)


NONE = (None, 0, None, 0, 0)

# ---------- Indicadores (iconos de 16×16, trazos redondeados) ----------

CHEVRON = {
    "down": "M4.5 6.5 L8 10 L11.5 6.5",
    "up": "M4.5 9.5 L8 6 L11.5 9.5",
    "left": "M9.5 4.5 L6 8 L9.5 11.5",
    "right": "M6.5 4.5 L10 8 L6.5 11.5",
    "plus": "M4.5 8 H11.5 M8 4.5 V11.5",
    "minus": "M4.5 8 H11.5",
}


def icon(sheet, gid, d, color, alpha, width=1.6, size=16):
    sheet.group(gid, size, size,
                f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{alpha:g}" stroke-width="{width}" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')


def indicators(sheet, t, accent):
    ink, ink2 = t["ink"], t["ink2"]
    look = {"normal": (ink2, 1), "focused": (ink, 1), "pressed": (ink, 1),
            "toggled": ("#FFFFFF", 1), "disabled": (ink2, 0.4)}
    for direction in ("up", "down", "left", "right"):
        for state, (color, alpha) in look.items():
            icon(sheet, f"arrow-{direction}-{state}", CHEVRON[direction], color, alpha)
    for state, (color, alpha) in look.items():
        icon(sheet, f"carrow-{state}", CHEVRON["down"], color, alpha)
        for kind in ("up", "down", "plus", "minus"):
            icon(sheet, f"spin-{kind}-{state}", CHEVRON[kind], color, alpha)
    # Ramas de los árboles: cerrada → flecha a la derecha, abierta → hacia abajo
    for state, (color, alpha) in look.items():
        if state == "toggled":
            continue
        icon(sheet, f"tree-plus-{state}", CHEVRON["right"], color, alpha)
        icon(sheet, f"tree-minus-{state}", CHEVRON["down"], color, alpha)
    # Cerrar pestaña: aspa con círculo suave al pasar por encima
    x = "M5.5 5.5 L10.5 10.5 M10.5 5.5 L5.5 10.5"
    for state, (bg, color, alpha) in {"normal": (0, ink2, 1), "focused": (0.10, ink, 1),
                                      "pressed": (0.16, ink, 1), "disabled": (0, ink2, 0.4)}.items():
        circle = f'<circle cx="8" cy="8" r="7.5" {paint(t["soft"], bg)}/>' if bg else ""
        sheet.group(f"tab-close-{state}", 16, 16, circle +
                    f'<path d="{x}" fill="none" stroke="{color}" stroke-opacity="{alpha:g}" stroke-width="1.5" '
                    f'stroke-linecap="round"/>')
    # Ventanas MDI y paneles acoplables (poco comunes): mismos iconos que los botones de ventana
    mdi = {"close": x, "maximize": "M5 5.5 h6 v5 h-6 Z", "minimize": "M5 10.5 H11",
           "restore": "M6 6.5 h4.5 v4.5 h-4.5 Z M7.5 5 H12 V9.5", "shade": "M5 6.5 H11", "menu": "M5 6 H11 M5 8 H11 M5 10 H11"}
    for name, d in mdi.items():
        for state, (color, alpha) in look.items():
            if state == "toggled" or (name == "menu" and state != "normal"):
                continue
            icon(sheet, f"mdi-{name}-{state}", d, color, alpha, 1.4)
    icon(sheet, "dock-close", mdi["close"], ink2, 1, 1.4)
    icon(sheet, "dock-restore", mdi["restore"], ink2, 1, 1.4)
    # Agarre de redimensionar: tres puntos en diagonal
    for state, alpha in (("normal", 0.35), ("focused", 0.6)):
        dots = "".join(f'<circle cx="{cx}" cy="{cy}" r="1.1" {paint(ink, alpha)}/>'
                       for cx, cy in ((10, 10), (6, 10), (10, 6)))
        sheet.group(f"resize-grip-{state}", 13, 13, dots)
    # Elementos que existen en el tema por defecto y que Luma no quiere ver
    for gid in ("grip-normal", "grip-focused", "grip-pressed", "button-default-indicator",
                "splitter-grip-normal", "splitter-grip-focused", "splitter-grip-pressed", "dial-notches"):
        sheet.group(gid, 4, 4, "")
    # Separadores: línea fina centrada
    sheet.group("menuitem-separator", 16, 9, f'<rect x="0" y="4" width="16" height="1" {paint(t["line"], 0.10)}/>')
    sheet.group("toolbar-separator", 9, 16, f'<rect x="4" y="2" width="1" height="12" {paint(t["line"], 0.14)}/>')
    sheet.group("toolbar-handle", 8, 16, "".join(
        f'<circle cx="4" cy="{cy}" r="1" {paint(ink, 0.3)}/>' for cy in (4, 8, 12)))
    sheet.group("header-separator", 1, 16, f'<rect x="0" y="3" width="1" height="10" {paint(t["line"], 0.10)}/>')
    # Rueda (QDial)
    sheet.group("dial", 32, 32, f'<circle cx="16" cy="16" r="15" {paint(t["field"], t["field_alpha"])} '
                f'stroke="{t["line"]}" stroke-opacity="{t["field_line"]:g}"/>')
    sheet.group("dial-handle", 8, 8, f'<circle cx="4" cy="4" r="3.5" fill="{accent}"/>')


def checks(sheet, t, accent):
    """Casillas y botones de opción de 18 px: vacíos en blanco, marcados en el acento."""
    S = 18
    tick = "M5 9.4 L7.8 12 L13 6.4"
    off = {"normal": t["check_line"], "focused": None, "pressed": None, "disabled": t["check_line"] * 0.5}
    for kind in ("checkbox", "radio"):
        def shape(fill_attr, line_attr, inset=0.75):
            if kind == "checkbox":
                return (f'<rect x="{inset}" y="{inset}" width="{S - 2 * inset}" height="{S - 2 * inset}" rx="5" '
                        f'{fill_attr} {line_attr}/>')
            return f'<circle cx="9" cy="9" r="{9 - inset}" {fill_attr} {line_attr}/>'
        for state, line_a in off.items():
            stroke = (f'stroke="{accent}" stroke-width="1.5"' if line_a is None
                      else f'stroke="{t["line"]}" stroke-opacity="{line_a:g}" stroke-width="1.5"')
            sheet.group(f"{kind}-{state}", S, S, shape(paint(t["check"], t["check_alpha"]), stroke))
        for state in ("normal", "focused", "pressed", "disabled"):
            color = shade(accent, 0.86) if state == "pressed" else (shade(accent, 1.12) if state == "focused" else accent)
            alpha = 0.45 if state == "disabled" else 1
            on = shape(paint(color, alpha), 'stroke="none"', 0)
            if kind == "checkbox":
                mark = (f'<path d="{tick}" fill="none" stroke="#FFFFFF" stroke-width="2" '
                        f'stroke-linecap="round" stroke-linejoin="round"/>')
                tri = '<path d="M5.5 9 H12.5" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>'
                sheet.group(f"checkbox-checked-{state}", S, S, on + mark)
                sheet.group(f"checkbox-tristate-{state}", S, S, on + tri)
            else:
                sheet.group(f"radio-checked-{state}", S, S, on + '<circle cx="9" cy="9" r="3.6" fill="#FFFFFF"/>')
    # Tirador de los deslizadores: círculo blanco con filo y sombra suave
    for state in ("normal", "focused", "pressed", "disabled"):
        ring = (f'stroke="{accent}" stroke-width="1.5"' if state in ("focused", "pressed")
                else f'stroke="{t["line"]}" stroke-opacity="{t["knob_line"]:g}"')
        alpha = 0.5 if state == "disabled" else 1
        sheet.group(f"slidercursor-{state}", 18, 18,
                    f'<circle cx="9" cy="10" r="8" {paint("#000000", 0.10)}/>'
                    f'<circle cx="9" cy="9" r="8" {paint(t["knob"], alpha)} {ring}/>')


def svg(t, accent):
    s = Sheet()
    a_dark = shade(accent, 0.86)
    line, soft = t["line"], t["soft"]
    # Botones: cristal blanco con filo; activados en el color de acento
    states(s, "button", 8, {
        "normal": (t["button"], t["button_alpha"], line, t["button_line"], 1),
        "focused": (t["button"], t["button_hover"], line, t["button_line_hover"], 1),
        "pressed": (t["pressed"], t["pressed_alpha"], line, t["button_line"], 1),
        "toggled": (accent, 1, a_dark, 1, 1),
    })
    # Botones de barra de herramientas: planos hasta pasar por encima
    states(s, "tbutton", 8, {
        "normal": NONE,
        "focused": (soft, 0.06, None, 0, 0),
        "pressed": (soft, 0.11, None, 0, 0),
        "toggled": (accent, 0.16, accent, 0.35, 1),
    })
    # Campos de texto: blancos; con el foco, filo de 2 px en el acento
    states(s, "lineedit", 8, {
        "normal": (t["field"], t["field_alpha"], line, t["field_line"], 1),
        "focused": (t["field"], min(1, t["field_alpha"] + 0.12), accent, 1, 2),
    })
    # Menús emergentes: cristal un poco más opaco que la ventana
    box(s, "menu-normal", 8, (t["menu"], t["menu_alpha"], line, t["menu_line"], 1))
    # Elementos de menú y de lista: píldora en el acento (como la referencia)
    states(s, "menuitem", 6, {
        "normal": NONE,
        "focused": (accent, 1, None, 0, 0),
        "pressed": (a_dark, 1, None, 0, 0),
        "toggled": (accent, 1, None, 0, 0),
    })
    states(s, "menubaritem", 6, {
        "normal": NONE,
        "focused": (soft, 0.07, None, 0, 0),
        "pressed": (soft, 0.11, None, 0, 0),
        "toggled": (soft, 0.11, None, 0, 0),
    })
    states(s, "itemview", 6, {
        "normal": NONE,
        "focused": (accent, 0.12, None, 0, 0),
        "pressed": (a_dark, 1, None, 0, 0),
        "toggled": (accent, 1, None, 0, 0),
        "toggled-inactive": (accent, 0.55, None, 0, 0),
    })
    # Pestañas: control segmentado; la activa es una píldora blanca
    states(s, "tab", 7, {
        "normal": NONE,
        "focused": (soft, 0.05, None, 0, 0),
        "pressed": (soft, 0.09, None, 0, 0),
        "toggled": (t["tab_on"], t["tab_on_alpha"], line, 0.10, 1),
    })
    box(s, "tabframe-normal", 10, (t["card"], t["card_alpha"], line, t["card_line"], 1))
    box(s, "group-normal", 10, (t["card"], t["card_alpha"] * 0.9, line, t["card_line"], 1))
    box(s, "common-normal", 6, (None, 0, line, 0.10, 1))
    states(s, "header", 2, {
        "normal": NONE,
        "focused": (soft, 0.04, None, 0, 0),
        "pressed": (soft, 0.08, None, 0, 0),
    })
    # Avisos emergentes: cristal oscuro del sistema
    box(s, "tooltip-normal", 8, (NIGHT, 0.92, "#FFFFFF", 0.10, 1))
    # Pistas: deslizador, barra de progreso y barra de desplazamiento (píldoras)
    states(s, "slider", 3, {
        "normal": (soft, t["groove"], None, 0, 0),
        "toggled": (accent, 1, None, 0, 0),
    })
    box(s, "progress-normal", 3, (soft, t["groove"] * 0.8, None, 0, 0))
    box(s, "progress-pattern-normal", 3, (accent, 1, None, 0, 0))
    states(s, "scrollbarslider", 5, {
        "normal": (soft, t["scroll"], None, 0, 0),
        "focused": (soft, t["scroll_hover"], None, 0, 0),
        "pressed": (soft, t["scroll_press"], None, 0, 0),
    }, m=2, r=3)
    # Marco de foco de teclado (sin estado)
    box(s, "focus", 2, (None, 0, accent, 0.6, 1.5))
    # Fondo de las ventanas y diálogos: el cristal (Kvantum pide desenfoque a KWin detrás)
    for el in ("window", "dialog"):
        s.group(f"{el}-normal", EDGE, EDGE,
                f'<rect x="0" y="0" width="{EDGE}" height="{EDGE}" {paint(t["window"], t["window_alpha"])}/>')
        s.group(f"{el}-normal-inactive", EDGE, EDGE,
                f'<rect x="0" y="0" width="{EDGE}" height="{EDGE}" {paint(t["window"], t["window_alpha_inactive"])}/>')
    indicators(s, t, accent)
    checks(s, t, accent)
    return s.svg()


# ---------- Configuración ----------

def kvconfig(name, t, accent):
    ink, ink2, ink3 = t["ink"], t["ink2"], t["ink3"]
    variant = "oscuro" if t["dark"] else "claro"
    return f"""# Generado por build_files/tools/gen_kvantum.py: no editar a mano.
[%General]
author=Luma OS
comment=Cristal {variant} de Luma OS
x11drag=menubar_and_primary_toolbar
alt_mnemonic=true
left_tabs=false
attach_active_tab=false
embedded_tabs=false
mirror_doc_tabs=false
group_toolbar_buttons=false
joined_inactive_tabs=false
spread_progressbar=true
spread_menuitems=false
composite=true
translucent_windows=true
blurring=true
popup_blurring=true
menu_blur_radius=8
tooltip_blur_radius=8
menu_shadow_depth=0
tooltip_shadow_depth=0
shadowless_popup=false
reduce_window_opacity=0
reduce_menu_opacity=0
contrast=1.00
intensity=1.00
saturation=1.15
scroll_width=10
scroll_arrows=false
scroll_min_extent=40
transient_scrollbar=true
transient_groove=true
scrollbar_in_view=true
slider_width=6
slider_handle_width=18
slider_handle_length=18
tickless_slider_handle_size=18
check_size=18
progressbar_thickness=6
textless_progressbar=false
center_toolbar_handle=true
toolbar_separator_thickness=9
menu_separator_height=9
submenu_overlap=0
submenu_delay=250
tooltip_delay=-1
combo_as_lineedit=true
combo_menu=true
combo_focus_rect=false
hide_combo_checkboxes=true
inline_spin_indicators=true
inline_spin_separator=false
vertical_spin_indicators=false
spin_button_width=18
groupbox_top_label=true
remove_extra_frames=true
fill_rubberband=false
animate_states=true
no_inactiveness=false
no_window_pattern=true
tree_branch_line=false
layout_spacing=6
layout_margin=9
respect_DE=true
opaque=kaffeine,kmplayer,subtitlecomposer,kdenlive,vlc,smplayer,smplayer2,avidemux,avidemux3_qt5,avidemux3_qt6,kamoso,QtCreator,VirtualBox,VirtualBoxVM,dragon,digikam,lyx,obs,mpv,haruna,krita,blender

[GeneralColors]
window.color={t["window"]}
inactive.window.color={t["window"]}
base.color={t["base"]}{t["base_alpha"]}
inactive.base.color={t["base"]}{t["base_alpha"]}
alt.base.color={t["alt_base"]}
button.color={t["window"]}
light.color={"#2A2F3D" if t["dark"] else "#FFFFFF"}
mid.light.color={"#232836" if t["dark"] else "#EEF0F5"}
dark.color={"#0B0D12" if t["dark"] else "#B9BEC9"}
mid.color={"#181C26" if t["dark"] else "#D9DDE6"}
highlight.color={accent}
inactive.highlight.color={accent}
tooltip.base.color={NIGHT}
text.color={ink}
window.text.color={ink}
button.text.color={ink}
disabled.text.color={ink3}
tooltip.text.color=#F0F2F7
highlight.text.color=#FFFFFF
link.color={accent}
link.visited.color=#8B5CF6
progress.indicator.text.color={ink}

[Hacks]
transparent_dolphin_view=true
transparent_ktitle_label=true
transparent_menutitle=true
transparent_arrow_button=true
transparent_pcmanfm_sidepane=true
transparent_pcmanfm_view=true
blur_translucent=true
respect_darkness=true
no_selection_tint=true
kcapacitybar_as_progressbar=true
force_size_grip=false
iconless_pushbutton=false
iconless_menu=false
normal_default_pushbutton=true
single_top_toolbar=false
middle_click_scroll=false
tint_on_mouseover=0
disabled_icon_opacity=50

[PanelButtonCommand]
frame=true
frame.element=button
frame.top=8
frame.bottom=8
frame.left=8
frame.right=8
interior=true
interior.element=button
indicator.element=arrow
indicator.size=16
text.margin.top=0
text.margin.bottom=0
text.margin.left=6
text.margin.right=6
text.iconspacing=6
text.normal.color={ink}
text.focus.color={ink}
text.press.color={ink}
text.toggle.color=#FFFFFF
text.shadow=false
min_width=+0.5font
min_height=+0font

[PanelButtonTool]
inherits=PanelButtonCommand
frame.element=tbutton
interior.element=tbutton
text.margin.left=4
text.margin.right=4
text.toggle.color={shade(accent, 0.8) if not t["dark"] else shade(accent, 1.3)}

[ToolbarButton]
frame.element=tbutton
interior.element=tbutton
indicator.element=arrow
text.normal.color={ink}
text.focus.color={ink}
text.press.color={ink}
text.toggle.color={shade(accent, 0.8) if not t["dark"] else shade(accent, 1.3)}

[Dock]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=dock

[DockTitle]
inherits=PanelButtonCommand
frame=false
interior=false
text.normal.color={ink2}
text.focus.color={ink}
text.bold=true

[IndicatorSpinBox]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=spin
indicator.size=16

[RadioButton]
inherits=PanelButtonCommand
frame=false
interior.element=radio
text.margin.left=4
text.margin.right=4
text.normal.color={ink}
text.focus.color={ink}
text.press.color={ink}
text.toggle.color={ink}

[CheckBox]
inherits=PanelButtonCommand
frame=false
interior.element=checkbox
text.margin.left=4
text.margin.right=4
text.normal.color={ink}
text.focus.color={ink}
text.press.color={ink}
text.toggle.color={ink}

[Focus]
inherits=PanelButtonCommand
frame=true
frame.element=focus
interior=false
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2

[GenericFrame]
inherits=PanelButtonCommand
frame=true
interior=false
frame.element=common
interior.element=common
frame.top=6
frame.bottom=6
frame.left=6
frame.right=6

[LineEdit]
inherits=PanelButtonCommand
frame.element=lineedit
interior.element=lineedit
indicator.element=carrow
text.margin.left=4
text.margin.right=4

[ToolbarLineEdit]
frame.element=lineedit
interior.element=lineedit

[DropDownButton]
inherits=PanelButtonCommand
indicator.element=arrow-down

[IndicatorArrow]
indicator.element=arrow
indicator.size=16

[ToolboxTab]
inherits=PanelButtonCommand
frame.element=tab
interior.element=tab
text.toggle.color={ink}

[Tab]
inherits=PanelButtonCommand
frame.element=tab
interior.element=tab
indicator.element=tab
indicator.size=16
frame.top=7
frame.bottom=7
frame.left=7
frame.right=7
text.margin.left=8
text.margin.right=8
text.normal.color={ink2}
text.focus.color={ink}
text.press.color={ink}
text.toggle.color={ink}
min_width=+1font

[TabFrame]
inherits=PanelButtonCommand
frame=true
frame.element=tabframe
interior=true
interior.element=tabframe
frame.top=10
frame.bottom=10
frame.left=10
frame.right=10

[TabBarFrame]
inherits=GenericFrame
frame=false
interior=false

[TreeExpander]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=tree
indicator.size=16

[HeaderSection]
inherits=PanelButtonCommand
frame.element=header
interior.element=header
indicator.element=arrow
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
text.margin.left=4
text.margin.right=4
text.normal.color={ink2}
text.focus.color={ink}
text.press.color={ink}
text.toggle.color={ink}
text.bold=false

[SizeGrip]
indicator.element=resize-grip

[Toolbar]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=toolbar
indicator.size=8
text.normal.color={ink}
text.focus.color={ink}

[Slider]
inherits=PanelButtonCommand
frame.element=slider
interior.element=slider
frame.top=3
frame.bottom=3
frame.left=3
frame.right=3
focusFrame=false

[SliderCursor]
inherits=PanelButtonCommand
frame=false
interior.element=slidercursor

[Progressbar]
inherits=PanelButtonCommand
frame.element=progress
interior.element=progress
frame.top=3
frame.bottom=3
frame.left=3
frame.right=3
text.margin=0
text.normal.color={ink}
text.focus.color={ink}
text.press.color={ink}
text.toggle.color={ink}
text.bold=false

[ProgressbarContents]
inherits=PanelButtonCommand
frame=true
frame.element=progress-pattern
interior.element=progress-pattern
frame.top=3
frame.bottom=3
frame.left=3
frame.right=3

[ItemView]
inherits=PanelButtonCommand
frame.element=itemview
interior.element=itemview
frame.top=6
frame.bottom=6
frame.left=6
frame.right=6
text.margin.top=0
text.margin.bottom=0
text.margin.left=2
text.margin.right=2
text.normal.color={ink}
text.focus.color={ink}
text.press.color=#FFFFFF
text.toggle.color=#FFFFFF
text.toggle.inactive.color=#FFFFFF

[Splitter]
frame=false
interior=false
indicator.element=splitter-grip
indicator.size=16

[Scrollbar]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=arrow
indicator.size=12

[ScrollbarSlider]
inherits=PanelButtonCommand
frame.element=scrollbarslider
interior=false
indicator.element=grip
frame.top=5
frame.bottom=5
frame.left=5
frame.right=5

[ScrollbarGroove]
inherits=PanelButtonCommand
frame=false
interior=false

[MenuItem]
inherits=PanelButtonCommand
frame=true
frame.element=menuitem
interior.element=menuitem
indicator.element=menuitem
frame.top=6
frame.bottom=6
frame.left=6
frame.right=6
text.margin.top=0
text.margin.bottom=0
text.margin.left=4
text.margin.right=4
text.normal.color={ink}
text.focus.color=#FFFFFF
text.press.color=#FFFFFF
text.toggle.color=#FFFFFF
min_height=+0font

[MenuBar]
inherits=PanelButtonCommand
frame=false
interior=false

[MenuBarItem]
inherits=PanelButtonCommand
frame=true
frame.element=menubaritem
interior.element=menubaritem
frame.top=6
frame.bottom=6
frame.left=6
frame.right=6
text.margin.top=0
text.margin.bottom=0
text.margin.left=4
text.margin.right=4
text.normal.color={ink}
text.focus.color={ink}
text.press.color={ink}
text.toggle.color={ink}

[TitleBar]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=mdi
indicator.size=16
text.normal.color={ink2}
text.focus.color={ink}
text.bold=true

[ComboBox]
inherits=PanelButtonCommand
indicator.element=carrow
text.toggle.color={ink}

[Menu]
inherits=PanelButtonCommand
frame=true
frame.element=menu
interior=true
interior.element=menu
frame.top=8
frame.bottom=8
frame.left=8
frame.right=8
text.normal.color={ink}

[GroupBox]
inherits=GenericFrame
frame=true
frame.element=group
interior=true
interior.element=group
frame.top=10
frame.bottom=10
frame.left=10
frame.right=10
text.normal.color={ink}
text.focus.color={ink}
text.press.color={ink}
text.bold=true

[ToolTip]
inherits=GenericFrame
frame=true
frame.element=tooltip
interior=true
interior.element=tooltip
frame.top=8
frame.bottom=8
frame.left=8
frame.right=8
text.normal.color=#F0F2F7
text.focus.color=#F0F2F7

[StatusBar]
inherits=GenericFrame
frame=false
interior=false

[Window]
interior=true
interior.element=window

[Dialog]
interior=true
interior.element=dialog
"""


def main():
    for name, accent in ACCENTS.items():
        folder = OUT / name
        folder.mkdir(parents=True, exist_ok=True)
        for theme, t in ((name, LIGHT), (f"{name}Dark", DARK)):
            (folder / f"{theme}.svg").write_text(svg(t, accent), encoding="utf-8", newline="\n")
            (folder / f"{theme}.kvconfig").write_text(kvconfig(theme, t, accent), encoding="utf-8", newline="\n")
    print(f"Temas Kvantum generados en {OUT}")


if __name__ == "__main__":
    main()
