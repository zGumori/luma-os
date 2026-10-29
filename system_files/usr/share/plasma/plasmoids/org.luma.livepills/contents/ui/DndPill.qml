import QtQuick
import org.kde.notificationmanager as NotificationManager

// «No molestar»: píldora roja mientras las notificaciones están silenciadas.
// Durante el Modo Juego ya lo indica la píldora «Jugando».
LivePill {
    GameModeState { id: gameMode }

    shown: NotificationManager.Server.inhibited && !gameMode.active
    live: "#E5323B"
    text: "No molestar"
    iconSource: Qt.resolvedUrl("../images/bell-off.svg")
}
