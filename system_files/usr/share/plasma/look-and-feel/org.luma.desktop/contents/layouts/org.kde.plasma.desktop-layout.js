// Disposición inicial de Luma OS: la Barra Luma (docs/DESIGN.md).
// Lanzador con la estrella · apps ancladas · espacio central · bandeja · reloj.

var panel = new Panel;
panel.location = "bottom";
panel.height = 2 * Math.ceil(gridUnit * 2.6 / 2);
panel.floating = true;
panel.hiding = "none";

var launcher = panel.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "luma-logo-mark");

panel.addWidget("org.kde.plasma.marginsseparator");

var tasks = panel.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:steam.desktop",
    "applications:org.kde.discover.desktop"
]);

// Espacio central: aquí irán las píldoras vivas
panel.addWidget("org.kde.plasma.panelspacer");
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
