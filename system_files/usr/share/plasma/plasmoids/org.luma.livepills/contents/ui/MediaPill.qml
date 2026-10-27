import QtQuick
import org.kde.plasma.private.mpris as Mpris

// Música: carátula y título de lo que suena. Clic = reproducir/pausar.
LivePill {
    id: pill

    readonly property var player: mpris2Model.currentPlayer
    readonly property bool playing: player !== null && player.playbackStatus === Mpris.PlaybackStatus.Playing

    shown: player !== null && player.playbackStatus !== Mpris.PlaybackStatus.Stopped && player.track !== ""
    live: playing ? "#F5A524" : "#6B7080"
    text: player ? player.track : ""
    artSource: player && player.artUrl ? player.artUrl : ""
    iconSource: Qt.resolvedUrl("../images/play.svg")
    interactive: true
    onClicked: if (player) player.PlayPause()

    Mpris.Mpris2Model { id: mpris2Model }
}
