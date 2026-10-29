import QtQuick

// «Grabando»: una partida se está grabando (Meta+Alt+R). Clic = detener y guardar.
LivePill {
    id: pill

    property real now: Date.now()

    GameModeState { id: gameMode }

    Timer {
        interval: 1000
        repeat: true
        running: gameMode.recording
        triggeredOnStart: true
        onTriggered: pill.now = Date.now()
    }

    function elapsed() {
        const total = Math.max(0, Math.floor((now - gameMode.recordingSince) / 1000));
        const minutes = Math.floor(total / 60);
        const seconds = total % 60;
        return minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
    }

    shown: gameMode.recording
    live: "#E5323B"
    text: "Grabando " + elapsed()
    iconSource: Qt.resolvedUrl("../images/record.svg")
    interactive: true
    onClicked: gameMode.toggleRecording()
}
