import QtQuick

// Pantalla de carga al iniciar sesión (KSplash): la estrella de Luma sobre la noche,
// con un brillo que respira y una píldora de progreso que avanza con cada etapa.
Rectangle {
    id: root
    color: "#07080D"

    property int stage

    onStageChanged: {
        if (stage === 2) {
            intro.running = true;
        }
    }

    Item {
        id: content
        anchors.centerIn: parent
        width: 220
        height: 220
        opacity: 0

        Image {
            id: halo
            anchors.centerIn: star
            source: "images/halo.svg"
            sourceSize: Qt.size(440, 440)
            width: 260
            height: 260
            SequentialAnimation on opacity {
                loops: Animation.Infinite
                NumberAnimation { from: 0.45; to: 0.9; duration: 1400; easing.type: Easing.InOutSine }
                NumberAnimation { from: 0.9; to: 0.45; duration: 1400; easing.type: Easing.InOutSine }
            }
        }

        Image {
            id: star
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 30
            source: "file:///usr/share/luma/logo-mark.svg"
            sourceSize: Qt.size(192, 192)
            width: 96
            height: 96
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: star.bottom
            anchors.topMargin: 22
            text: "luma"
            color: "white"
            font.family: "DM Sans"
            font.pixelSize: 30
            font.weight: Font.Bold
            font.letterSpacing: 1
        }
    }

    Rectangle { // píldora de progreso
        id: track
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: root.height * 0.16
        width: 160
        height: 4
        radius: 2
        color: Qt.rgba(1, 1, 1, 0.12)
        opacity: content.opacity

        Rectangle {
            height: parent.height
            radius: 2
            width: parent.width * Math.min(1, Math.max(0.08, (root.stage - 1) / 5))
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "#FF7A45" }
                GradientStop { position: 1.0; color: "#E8366F" }
            }
            Behavior on width { NumberAnimation { duration: 500; easing.type: Easing.OutCubic } }
        }
    }

    ParallelAnimation {
        id: intro
        NumberAnimation { target: content; property: "opacity"; from: 0; to: 1; duration: 600; easing.type: Easing.OutCubic }
        NumberAnimation { target: content; property: "scale"; from: 0.92; to: 1; duration: 700; easing.type: Easing.OutBack }
    }
}
