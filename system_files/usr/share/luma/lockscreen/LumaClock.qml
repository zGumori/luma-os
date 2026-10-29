import QtQuick
import QtQuick.Layouts
import org.kde.plasma.clock as PlasmaClock

// Reloj de la pantalla de bloqueo de Luma: sustituye al «Clock» de Breeze con la misma
// interfaz (un Item cuya opacidad y posición controla LockScreenUi.qml). Estilo del
// inicio de sesión de Luma: fecha arriba, hora grande y fina en DM Sans.
ColumnLayout {
    id: root

    readonly property bool softwareRendering: GraphicsInfo.api === GraphicsInfo.Software
    spacing: -8

    Text {
        // Solo la primera letra en mayúscula: «Jueves, 29 de octubre»
        readonly property string date: timeSource.dateTime.toLocaleDateString(Qt.locale(), "dddd, d 'de' MMMM")
        text: date.charAt(0).toUpperCase() + date.slice(1)
        textFormat: Text.PlainText
        color: Qt.rgba(1, 1, 1, 0.8)
        style: root.softwareRendering ? Text.Outline : Text.Normal
        styleColor: "#000000"
        font.family: "DM Sans"
        font.pixelSize: 26
        font.weight: Font.Medium
        Layout.alignment: Qt.AlignHCenter
    }
    Text {
        text: timeSource.dateTime.toLocaleTimeString(Qt.locale(), "HH:mm")
        textFormat: Text.PlainText
        color: "#FFFFFF"
        style: root.softwareRendering ? Text.Outline : Text.Normal
        styleColor: "#000000"
        font.family: "DM Sans"
        font.pixelSize: 132
        font.weight: Font.Light
        font.letterSpacing: -3
        Layout.alignment: Qt.AlignHCenter
    }

    PlasmaClock.Clock {
        id: timeSource
        trackSeconds: false
    }
}
