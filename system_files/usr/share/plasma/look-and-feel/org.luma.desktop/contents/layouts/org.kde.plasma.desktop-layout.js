// Disposición inicial de Luma OS: la Barra Luma (docs/DESIGN.md).
// Barra de cristal oscuro de lado a lado, pegada al borde inferior:
// lanzador con la estrella · apps centradas · píldoras vivas, bandeja y reloj a la derecha.
// Si cambias el orden, actualiza también updates/luma-full-bar.js.

var panel = new Panel;
panel.location = "bottom";
panel.height = 2 * Math.ceil(gridUnit * 2.6 / 2);
panel.floating = false;
panel.hiding = "none";

var launcher = panel.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "luma-logo-mark");

// Dos espaciadores flexibles iguales: Plasma centra las apps respecto a la pantalla
panel.addWidget("org.kde.plasma.panelspacer");

var tasks = panel.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("fill", false);
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:steam.desktop",
    "applications:org.kde.discover.desktop"
]);

panel.addWidget("org.kde.plasma.panelspacer");

// Derecha: píldoras vivas (música, juego, grabación, «No molestar»), bandeja y reloj
panel.addWidget("org.luma.livepills");
panel.addWidget("org.kde.plasma.systemtray");

var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateFormat", "custom");
clock.writeConfig("customDateFormat", "ddd d");
clock.writeConfig("dateDisplayFormat", "BesideTime");

// Fondo de Luma (versión clara u oscura según el esquema de color)
var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {
    var desktop = allDesktops[i];
    desktop.wallpaperPlugin = "org.kde.image";
    desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktop.writeConfig("Image", "file:///usr/share/wallpapers/Luma/");
}
