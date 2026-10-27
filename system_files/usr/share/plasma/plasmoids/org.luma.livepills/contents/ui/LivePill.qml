import QtQuick

// Píldora viva de Luma Glass (docs/DESIGN.md): base oscura con un brillo de color
// que sube desde el borde inferior. Solo usa QtQuick para poder probarla fuera de Plasma.
Rectangle {
    id: pill

    property bool shown: true
    property color live: "#2F7BFF"
    property string text
    property url iconSource
    property url artSource
    property bool interactive: false
    signal clicked()

    readonly property bool hasArt: artSource.toString() !== ""

    implicitHeight: 34
    implicitWidth: Math.min(row.implicitWidth + (hasArt ? 20 : 26), 280)
    radius: height / 2
    border.width: 1
    border.color: Qt.rgba(live.r, live.g, live.b, 0.6)
    gradient: Gradient {
        GradientStop { position: 0.0; color: Qt.tint("#14171F", Qt.rgba(pill.live.r, pill.live.g, pill.live.b, 0.12)) }
        GradientStop { position: 1.0; color: Qt.tint("#14171F", Qt.rgba(pill.live.r, pill.live.g, pill.live.b, 0.75)) }
    }
    clip: true

    // Aparece creciendo desde el centro con un rebote corto
    opacity: shown ? 1 : 0
    scale: shown ? (mouse.pressed ? 0.95 : (mouse.containsMouse && interactive ? 1.04 : 1)) : 0.6
    Behavior on opacity { NumberAnimation { duration: 220 } }
    Behavior on scale { NumberAnimation { duration: 320; easing.type: Easing.OutBack } }

    Rectangle { // línea de luz superior
        anchors { left: parent.left; right: parent.right; top: parent.top; leftMargin: pill.radius; rightMargin: pill.radius; topMargin: 1 }
        height: 1
        color: Qt.rgba(1, 1, 1, 0.22)
    }

    Row {
        id: row
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: pill.hasArt ? 6 : 13
        spacing: 8

        Rectangle { // carátula (música)
            visible: pill.hasArt
            width: pill.height - 12
            height: width
            radius: width * 0.36
            color: "#000000"
            clip: true
            Image { anchors.fill: parent; source: pill.artSource; fillMode: Image.PreserveAspectCrop; asynchronous: true }
        }
        Image {
            visible: pill.iconSource.toString() !== "" && !pill.hasArt
            anchors.verticalCenter: parent.verticalCenter
            source: pill.iconSource
            sourceSize: Qt.size(36, 36)
            width: 18
            height: 18
        }
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: pill.text
            color: "white"
            font.family: "DM Sans"
            font.pixelSize: 14
            font.weight: Font.DemiBold
            elide: Text.ElideRight
            width: Math.min(implicitWidth, 200)
        }
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        enabled: pill.interactive
        hoverEnabled: true
        cursorShape: pill.interactive ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: pill.clicked()
    }
}
