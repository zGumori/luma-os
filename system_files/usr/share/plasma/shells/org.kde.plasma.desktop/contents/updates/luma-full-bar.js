// Luma OS: pasa la Barra Luma flotante de antes a la barra de lado a lado, con las apps
// centradas y las píldoras vivas a la derecha. Se ejecuta una sola vez por usuario y solo
// toca paneles que siguen exactamente como los dejó Luma (sin widgets añadidos ni quitados).
// Las apps ancladas se conservan.
const oldLayout = [
    "org.kde.plasma.kickoff", "org.kde.plasma.marginsseparator", "org.kde.plasma.icontasks",
    "org.kde.plasma.panelspacer", "org.luma.livepills", "org.kde.plasma.panelspacer",
    "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock"
];
const allPanels = panels();

for (let i = 0; i < allPanels.length; ++i) {
    const old = allPanels[i];
    const widgets = old.widgets();
    const types = [];
    for (let j = 0; j < widgets.length; ++j) {
        types.push(widgets[j].type);
    }
    if (old.location !== "bottom" || types.join(",") !== oldLayout.join(",")) {
        continue;
    }

    const oldTasks = widgets[2];
    oldTasks.currentConfigGroup = ["General"];
    const launchers = oldTasks.readConfig("launchers", "");
    widgets[0].currentConfigGroup = ["General"];
    const launcherIcon = String(widgets[0].readConfig("icon", "luma-logo-mark"));
    const screen = old.screen;
    const height = old.height;
    old.remove();

    // Igual que layouts/org.kde.plasma.desktop-layout.js del tema global
    const panel = new Panel;
    panel.screen = screen;
    panel.location = "bottom";
    panel.height = height;
    panel.floating = false;
    panel.hiding = "none";

    const launcher = panel.addWidget("org.kde.plasma.kickoff");
    launcher.currentConfigGroup = ["General"];
    launcher.writeConfig("icon", launcherIcon);

    panel.addWidget("org.kde.plasma.panelspacer");
    const tasks = panel.addWidget("org.kde.plasma.icontasks");
    tasks.currentConfigGroup = ["General"];
    tasks.writeConfig("fill", false);
    if (launchers !== "" && launchers.length !== 0) {
        tasks.writeConfig("launchers", launchers);
    }
    panel.addWidget("org.kde.plasma.panelspacer");

    panel.addWidget("org.luma.livepills");
    panel.addWidget("org.kde.plasma.systemtray");
    const clock = panel.addWidget("org.kde.plasma.digitalclock");
    clock.currentConfigGroup = ["Appearance"];
    clock.writeConfig("showDate", true);
    clock.writeConfig("dateFormat", "custom");
    clock.writeConfig("customDateFormat", "ddd d");
    clock.writeConfig("dateDisplayFormat", "BesideTime");
}
