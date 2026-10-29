import QtQuick

// «Jugando»: el Modo Juego está activo (rendimiento al máximo, notificaciones en silencio).
LivePill {
    GameModeState { id: gameMode }

    shown: gameMode.active
    live: "#8B5CF6"
    text: gameMode.title !== "" ? "Jugando · " + gameMode.title : "Jugando"
    iconSource: Qt.resolvedUrl("../images/gamepad.svg")
}
