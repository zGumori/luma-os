import QtQuick
import org.kde.notificationmanager as NotificationManager

// «No molestar»: píldora roja mientras las notificaciones están silenciadas.
LivePill {
    shown: NotificationManager.Server.inhibited
    live: "#E5323B"
    text: "No molestar"
    iconSource: Qt.resolvedUrl("../images/bell-off.svg")
}
