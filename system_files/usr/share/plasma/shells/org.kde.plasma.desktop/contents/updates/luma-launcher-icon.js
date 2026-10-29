// Luma OS: pone la estrella de Luma en el botón del lanzador de aplicaciones de los paneles
// existentes. Se ejecuta una sola vez por usuario. No toca un icono elegido a mano.
const launchers = ["org.kde.plasma.kickoff", "org.kde.plasma.kicker", "org.kde.plasma.kickerdash"];
const allPanels = panels();

for (let i = 0; i < allPanels.length; ++i) {
    const widgets = allPanels[i].widgets();
    for (let j = 0; j < widgets.length; ++j) {
        const widget = widgets[j];
        if (launchers.indexOf(widget.type) === -1) {
            continue;
        }
        widget.currentConfigGroup = ["General"];
        const icon = String(widget.readConfig("icon", ""));
        if (icon === "" || /start-here|bazzite|fedora|distributor|steamdeck/i.test(icon)) {
            widget.writeConfig("icon", "luma-logo-mark");
            widget.reloadConfig();
        }
    }
}
