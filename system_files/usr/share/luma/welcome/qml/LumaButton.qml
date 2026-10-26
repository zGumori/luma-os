import QtQuick

// Botón con degradado (primario) o de cristal (secundario), con animación al pulsar
Item {
    id: root
    property string text
    property bool primary: true
    property bool enabledState: true
    signal clicked()

    implicitWidth: Math.max(120, label.implicitWidth + 44)
    implicitHeight: 42
    opacity: enabledState ? 1 : 0.45
    scale: mouse.pressed ? 0.96 : (mouse.containsMouse ? 1.02 : 1)
    Behavior on scale { NumberAnimation { duration: 160; easing.type: Easing.OutBack } }

    Rectangle {
        anchors.fill: parent
        radius: height / 2
        visible: root.primary
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0; color: "#5E8BFF" }
            GradientStop { position: 1; color: "#B45CFF" }
        }
    }
    Rectangle {
        anchors.fill: parent
        radius: height / 2
        color: root.primary ? Qt.rgba(1, 1, 1, mouse.containsMouse ? 0.12 : 0)
                            : Qt.rgba(1, 1, 1, mouse.containsMouse ? 0.16 : 0.09)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, root.primary ? 0.25 : 0.16)
        Behavior on color { ColorAnimation { duration: 150 } }
    }
    Text {
        id: label
        anchors.centerIn: parent
        text: root.text
        color: "white"
        font.pixelSize: 15
        font.weight: Font.DemiBold
    }
    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        enabled: root.enabledState
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
