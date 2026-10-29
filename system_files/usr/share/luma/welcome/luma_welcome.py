#!/usr/bin/python3
"""Bienvenida a Luma OS: asistente del primer inicio de sesión (PySide6 + QML)."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QProcess, QRectF, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QFont, QFontDatabase, QGuiApplication, QIcon, QImage, QPainter
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtSvg import QSvgRenderer

HERE = Path(__file__).resolve().parent
IMAGE_INFO = Path("/usr/share/ublue-os/image-info.json")
GPU_CHECK = "/usr/libexec/luma/luma-gpu-check"
SHARE = HERE.parent  # /usr/share/luma
FONTS = SHARE.parent / "fonts" / "luma"  # /usr/share/fonts/luma
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "luma"
DONE_FILE = CONFIG_DIR / "welcome-done"

# Apps opcionales que se ofrecen en la bienvenida (las básicas ya se instalan solas)
OPTIONAL_APPS = [
    ("com.discordapp.Discord", "Discord", "Chat de voz y texto para jugar con amigos", "#5865F2"),
    ("com.spotify.Client", "Spotify", "Música y podcasts", "#1DB954"),
    ("com.obsproject.Studio", "OBS Studio", "Graba y retransmite tus partidas", "#7B61FF"),
    ("com.google.Chrome", "Google Chrome", "Navegador web de Google", "#4285F4"),
    ("org.videolan.VLC", "VLC", "Reproduce cualquier vídeo", "#FF8800"),
    ("org.telegram.desktop", "Telegram", "Mensajería rápida y segura", "#2AABEE"),
    ("org.gimp.GIMP", "GIMP", "Edición de imágenes", "#9C7A4D"),
    ("org.prismlauncher.PrismLauncher", "Prism Launcher", "Minecraft con mods, sin complicaciones", "#4DB36A"),
    ("org.libretro.RetroArch", "RetroArch", "Emuladores de consolas clásicas", "#E04E5C"),
    ("com.visualstudio.code", "VS Code", "Editor de código", "#2F9BEF"),
]

# Acentos de Luma Glass (docs/DESIGN.md)
ACCENTS = ["#2F7BFF", "#14B8E6", "#8B5CF6", "#F0457A", "#F5A524", "#21C07A"]
# Tema Kvantum de cada acento (build_files/tools/gen_kvantum.py)
KVANTUM_THEMES = dict(zip(ACCENTS, ["Luma", "LumaCian", "LumaVioleta", "LumaRosa", "LumaAmbar", "LumaVerde"]))


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None


def flatpak_installed(app_id):
    result = run(["flatpak", "info", app_id])
    return bool(result and result.returncode == 0)


def gpu_names():
    names = []
    for cls in ("::0300", "::0302"):
        result = run(["lspci", "-mm", "-d", cls])
        if not result:
            continue
        for line in result.stdout.splitlines():
            # Formato: slot "clase" "fabricante" "dispositivo" ...
            fields = line.split('"')
            if len(fields) >= 6:
                names.append(f"{fields[3]} {fields[5]}".strip())
    return names


def image_info():
    try:
        return json.loads(IMAGE_INFO.read_text())
    except (OSError, ValueError):
        return {}


class IconProvider(QQuickImageProvider):
    """Iconos de trazo recoloreados: image://icon/<nombre>/<color sin #>."""

    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image)

    def requestImage(self, icon_id, size, requested):
        name, _, color = icon_id.partition("/")
        svg = (HERE / "icons" / f"{name}.svg").read_text().replace("#14161C", f"#{color or '14161C'}")
        side = max(requested.width(), requested.height(), 24)
        image = QImage(side, side, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        QSvgRenderer(svg.encode()).render(painter, QRectF(0, 0, side, side))
        painter.end()
        if size is not None:
            size.setWidth(side)
            size.setHeight(side)
        return image


class Backend(QObject):
    appsChanged = Signal()
    message = Signal(str)

    def __init__(self):
        super().__init__()
        self._apps = [
            {"id": a, "name": n, "description": d, "color": c,
             "installed": flatpak_installed(a), "busy": False}
            for a, n, d, c in OPTIONAL_APPS
        ]
        self._gpus = gpu_names() or ["No se ha podido detectar la tarjeta gráfica"]
        self._current = image_info().get("image-name", "luma")
        result = run([GPU_CHECK, "--recommend"])
        self._recommended = result.stdout.strip() if result and result.returncode == 0 else self._current
        self._processes = {}

    # --- Sistema -----------------------------------------------------------

    @Property(str, constant=True)
    def logo(self):
        return QUrl.fromLocalFile(str(SHARE / "logo.svg")).toString()

    @Property(str, constant=True)
    def logoMark(self):
        return QUrl.fromLocalFile(str(SHARE / "logo-mark.svg")).toString()

    @Property("QStringList", constant=True)
    def gpus(self):
        return self._gpus

    @Property(str, constant=True)
    def currentImage(self):
        return self._current

    @Property(str, constant=True)
    def recommendedImage(self):
        return self._recommended

    @Property(bool, constant=True)
    def gpuMatches(self):
        return self._current == self._recommended

    @Slot()
    def switchGpu(self):
        for term, args in (("ptyxis", ["--"]), ("konsole", ["-e"])):
            if shutil.which(term):
                QProcess.startDetached(term, args + [GPU_CHECK, "--switch"])
                return
        self.message.emit("No se ha encontrado una terminal para cambiar de variante.")

    # --- Apps --------------------------------------------------------------

    @Property("QVariantList", notify=appsChanged)
    def apps(self):
        return self._apps

    def _set_app(self, app_id, **changes):
        for app in self._apps:
            if app["id"] == app_id:
                app.update(changes)
        self.appsChanged.emit()

    @Slot(str)
    def installApp(self, app_id):
        if app_id in self._processes:
            return
        proc = QProcess(self)
        proc.setProgram("flatpak")
        proc.setArguments(["install", "--system", "--noninteractive", "--assumeyes", "flathub", app_id])
        proc.finished.connect(lambda code, _status, a=app_id: self._install_finished(a, code))
        proc.errorOccurred.connect(lambda _err, a=app_id: self._install_finished(a, -1))
        self._processes[app_id] = proc
        self._set_app(app_id, busy=True)
        proc.start()

    def _install_finished(self, app_id, code):
        if self._processes.pop(app_id, None) is None:
            return
        ok = code == 0 and flatpak_installed(app_id)
        self._set_app(app_id, busy=False, installed=ok)
        if not ok:
            name = next(a["name"] for a in self._apps if a["id"] == app_id)
            self.message.emit(f"No se pudo instalar {name}. Comprueba la conexión a internet.")

    # --- Aspecto -----------------------------------------------------------

    @Property("QStringList", constant=True)
    def accents(self):
        return ACCENTS

    @Slot(bool, str)
    def applyLook(self, dark, accent):
        scheme = "LumaDark" if dark else "LumaLight"
        args = [scheme]
        if accent:
            args = ["--accent-color", accent, scheme]
        if not QProcess.startDetached("plasma-apply-colorscheme", args)[0]:
            self.message.emit("No se pudo aplicar el aspecto (solo funciona en KDE Plasma).")
            return
        # Decoración de ventana a juego (Luma / LumaDark) y aviso a KWin para recargarla
        theme = "__aurorae__svg__LumaDark" if dark else "__aurorae__svg__Luma"
        run(["kwriteconfig6", "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "theme", theme])
        run(["dbus-send", "--session", "--type=method_call", "--dest=org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure"])
        # Cristal dentro de las ventanas: tema Kvantum del acento elegido, claro u oscuro
        kvantum = KVANTUM_THEMES.get((accent or ACCENTS[0]).upper(), "Luma")
        run(["kwriteconfig6", "--file", str(Path.home() / ".config/Kvantum/kvantum.kvconfig"),
             "--group", "General", "--key", "theme", kvantum])
        run(["kwriteconfig6", "--file", "kdeglobals", "--group", "KDE", "--key", "widgetStyle",
             "kvantum-dark" if dark else "kvantum"])
        # Aviso de cambio de estilo (KGlobalSettings::StyleChanged = 2) para las apps abiertas
        run(["dbus-send", "--session", "--type=signal", "/KGlobalSettings", "org.kde.KGlobalSettings.notifyChange",
             "int32:2", "int32:0"])

    # --- Otros -------------------------------------------------------------

    @Slot(str)
    def launch(self, command):
        if not QProcess.startDetached(command, [])[0]:
            self.message.emit(f"No se pudo abrir {command}.")

    @Slot(str)
    def openUrl(self, url):
        QDesktopServices.openUrl(QUrl(url))

    @Slot(bool)
    def finish(self, show_again):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if show_again:
            DONE_FILE.unlink(missing_ok=True)
        else:
            DONE_FILE.touch()
        QGuiApplication.quit()


def main():
    if "--autostart" in sys.argv and DONE_FILE.exists():
        return 0

    # Estilo "Basic": la app dibuja su propio aspecto, igual en cualquier escritorio
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(sys.argv)
    for font in FONTS.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont("DM Sans", 11))
    app.setApplicationName("Bienvenida a Luma")
    app.setDesktopFileName("org.luma.Welcome")
    app.setWindowIcon(QIcon.fromTheme("luma-logo"))

    backend = Backend()
    engine = QQmlApplicationEngine()
    engine.addImageProvider("icon", IconProvider())
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(QUrl.fromLocalFile(str(HERE / "qml" / "Main.qml")))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
