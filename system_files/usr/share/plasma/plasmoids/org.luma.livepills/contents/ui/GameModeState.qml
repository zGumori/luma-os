import QtQuick
import org.kde.plasma.workspace.dbus as DBus

// Estado del servicio de Modo Juego de Luma (org.luma.GameMode, luma-gamemode).
// Las propiedades se actualizan solas con la señal PropertiesChanged del servicio.
Item {
    id: gameModeState

    readonly property bool available: watcher.registered
    readonly property bool active: available && props.properties.Active === true
    readonly property string title: available && props.properties.Title ? String(props.properties.Title) : ""
    readonly property bool recording: available && props.properties.Recording === true
    readonly property real recordingSince: available ? Number(props.properties.RecordingSince || 0) : 0

    function toggleRecording() {
        DBus.SessionBus.asyncCall({
            "service": "org.luma.GameMode",
            "path": "/org/luma/GameMode",
            "iface": "org.luma.GameMode",
            "member": "ToggleRecording",
            "arguments": [],
            "signature": ""
        });
    }

    DBus.Properties {
        id: props
        busType: DBus.BusType.Session
        service: "org.luma.GameMode"
        path: "/org/luma/GameMode"
        iface: "org.luma.GameMode"
    }

    // Si el servicio arranca (o se reinicia) después que la barra, se vuelven a leer
    DBus.DBusServiceWatcher {
        id: watcher
        busType: DBus.BusType.Session
        watchedService: "org.luma.GameMode"
        onRegisteredChanged: if (registered) props.updateAll()
    }
}
