// Luma: Modo Juego — avisa al servicio luma-gamemode (org.luma.GameMode) de la ventana
// activa. El servicio decide si es un juego; este script solo informa.

function report(window) {
    if (!window) {
        return;
    }
    // Todo como texto salvo la pantalla completa: los números de JS llegan a D-Bus como double
    callDBus("org.luma.GameMode", "/org/luma/GameMode", "org.luma.GameMode", "WindowActivated",
             String(window.resourceClass || ""), String(window.resourceName || ""),
             String(window.caption || ""), Boolean(window.fullScreen), String(window.pid || 0));
}

function watch(window) {
    window.fullScreenChanged.connect(function () {
        if (workspace.activeWindow === window) {
            report(window);
        }
    });
}

workspace.windowActivated.connect(report);
workspace.windowAdded.connect(watch);
workspace.windowList().forEach(watch);
report(workspace.activeWindow);
