import QtQuick

// Panel de cristal: relleno translúcido, degradado sutil y borde iluminado arriba
Rectangle {
    id: root
    property real tint: 0.07
    radius: 20
    color: Qt.rgba(1, 1, 1, tint)
    border.width: 1
    border.color: Qt.rgba(1, 1, 1, 0.14)

    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.07) }
            GradientStop { position: 0.45; color: Qt.rgba(1, 1, 1, 0.0) }
        }
    }
}
