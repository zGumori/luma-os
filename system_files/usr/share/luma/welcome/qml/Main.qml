import QtQuick
import QtQuick.Controls
import QtQuick.Effects
import QtQuick.Layouts

ApplicationWindow {
    id: win
    width: 1000
    height: 660
    minimumWidth: 860
    minimumHeight: 600
    visible: true
    title: "Bienvenida a Luma"
    color: "#090B18"

    property int step: 0
    readonly property var steps: ["Bienvenida", "Tarjeta gráfica", "Apps", "Aspecto", "Listo"]
    property bool darkMode: true
    property string accent: backend.accents[0]

    function go(i) {
        if (i < 0 || i >= steps.length || i === step) return
        stack.forward = i > step
        step = i
        stack.replace(pages[i])
    }
    readonly property var pages: [welcomePage, gpuPage, appsPage, lookPage, donePage]

    // ---------- Fondo: manchas de color animadas y difuminadas ----------
    Item {
        id: blobs
        anchors.fill: parent
        layer.enabled: true
        layer.effect: MultiEffect { blurEnabled: true; blur: 1.0; blurMax: 64; saturation: 0.15 }

        component Blob: Rectangle {
            id: blob
            property real cx
            property real cy
            property real drift: 60
            property int period: 14000
            width: 420; height: width; radius: width / 2
            x: cx * win.width - width / 2 + dx
            y: cy * win.height - height / 2 + dy
            property real dx: 0
            property real dy: 0
            opacity: 0.55
            SequentialAnimation on dx {
                loops: Animation.Infinite
                NumberAnimation { to: blob.drift; duration: blob.period; easing.type: Easing.InOutSine }
                NumberAnimation { to: -blob.drift; duration: blob.period; easing.type: Easing.InOutSine }
            }
            SequentialAnimation on dy {
                loops: Animation.Infinite
                NumberAnimation { to: -blob.drift * 0.7; duration: blob.period * 1.3; easing.type: Easing.InOutSine }
                NumberAnimation { to: blob.drift * 0.7; duration: blob.period * 1.3; easing.type: Easing.InOutSine }
            }
        }
        Blob { cx: 0.12; cy: 0.18; color: "#3EC8F5"; period: 16000 }
        Blob { cx: 0.85; cy: 0.25; color: win.accent; width: 480; period: 19000; Behavior on color { ColorAnimation { duration: 600 } } }
        Blob { cx: 0.55; cy: 0.95; color: "#C45CFF"; width: 520; period: 22000 }
    }
    Rectangle { anchors.fill: parent; color: Qt.rgba(0.035, 0.04, 0.09, 0.45) }

    // ---------- Estructura: barra lateral + contenido ----------
    RowLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        GlassPanel {
            Layout.preferredWidth: 230
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 6

                RowLayout {
                    spacing: 12
                    Image { source: backend.logo; sourceSize: Qt.size(40, 40); Layout.preferredWidth: 40; Layout.preferredHeight: 40 }
                    Text { text: "Luma OS"; color: "white"; font.pixelSize: 21; font.weight: Font.Bold }
                }
                Item { Layout.preferredHeight: 22 }

                Repeater {
                    model: win.steps
                    delegate: Rectangle {
                        required property int index
                        required property string modelData
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        radius: 12
                        color: index === win.step ? Qt.rgba(1, 1, 1, 0.12)
                                                  : (stepMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.05) : "transparent")
                        Behavior on color { ColorAnimation { duration: 180 } }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            spacing: 12
                            Rectangle {
                                Layout.preferredWidth: 24; Layout.preferredHeight: 24; radius: 12
                                color: index < win.step ? "#2FD4A0" : (index === win.step ? win.accent : Qt.rgba(1, 1, 1, 0.1))
                                Behavior on color { ColorAnimation { duration: 250 } }
                                Text {
                                    anchors.centerIn: parent
                                    text: index < win.step ? "✓" : index + 1
                                    color: "white"; font.pixelSize: 12; font.weight: Font.Bold
                                }
                            }
                            Text {
                                Layout.fillWidth: true
                                text: modelData
                                color: index === win.step ? "white" : Qt.rgba(1, 1, 1, 0.65)
                                font.pixelSize: 15
                                font.weight: index === win.step ? Font.DemiBold : Font.Normal
                            }
                        }
                        MouseArea { id: stepMouse; anchors.fill: parent; hoverEnabled: true; onClicked: win.go(index) }
                    }
                }
                Item { Layout.fillHeight: true }
                Text {
                    text: "Variante: " + backend.currentImage
                    color: Qt.rgba(1, 1, 1, 0.4)
                    font.pixelSize: 12
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            GlassPanel {
                Layout.fillWidth: true
                Layout.fillHeight: true
                tint: 0.05
                clip: true

                StackView {
                    id: stack
                    property bool forward: true
                    anchors.fill: parent
                    anchors.margins: 36
                    initialItem: welcomePage

                    replaceEnter: Transition {
                        ParallelAnimation {
                            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 380; easing.type: Easing.OutCubic }
                            NumberAnimation { property: "x"; from: stack.forward ? 40 : -40; to: 0; duration: 420; easing.type: Easing.OutCubic }
                        }
                    }
                    replaceExit: Transition {
                        ParallelAnimation {
                            NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 220; easing.type: Easing.InCubic }
                            NumberAnimation { property: "x"; from: 0; to: stack.forward ? -30 : 30; duration: 220; easing.type: Easing.InCubic }
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                LumaButton { text: "Atrás"; primary: false; visible: win.step > 0; onClicked: win.go(win.step - 1) }
                Item { Layout.fillWidth: true }
                LumaButton {
                    text: win.step === win.steps.length - 1 ? "Empezar" : "Siguiente"
                    onClicked: win.step === win.steps.length - 1 ? backend.finish(showAgain.checked) : win.go(win.step + 1)
                }
            }
        }
    }

    // ---------- Aviso flotante ----------
    Rectangle {
        id: toast
        property alias text: toastText.text
        anchors.horizontalCenter: parent.horizontalCenter
        y: opacity > 0 ? parent.height - height - 90 : parent.height - height - 70
        width: toastText.implicitWidth + 40
        height: 44
        radius: 22
        color: "#E6222540"
        border.color: Qt.rgba(1, 1, 1, 0.18)
        opacity: 0
        Behavior on opacity { NumberAnimation { duration: 250 } }
        Behavior on y { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }
        Text { id: toastText; anchors.centerIn: parent; color: "white"; font.pixelSize: 14 }
        Timer { id: toastTimer; interval: 4500; onTriggered: toast.opacity = 0 }
    }
    Connections {
        target: backend
        function onMessage(text) { toast.text = text; toast.opacity = 1; toastTimer.restart() }
    }

    // ---------- Componentes reutilizables ----------
    component Title: Text { color: "white"; font.pixelSize: 30; font.weight: Font.Bold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    component Body: Text { color: Qt.rgba(1, 1, 1, 0.72); font.pixelSize: 16; lineHeight: 1.25; wrapMode: Text.WordWrap; Layout.fillWidth: true }

    // ---------- Páginas ----------
    Component {
        id: welcomePage
        ColumnLayout {
            spacing: 18
            Item { Layout.fillHeight: true }
            Item {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 150; Layout.preferredHeight: 150
                Image {
                    id: bigLogo
                    anchors.fill: parent
                    source: backend.logo
                    sourceSize: Qt.size(300, 300)
                    layer.enabled: true
                    layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#806A6CFF"; shadowBlur: 1.0; shadowVerticalOffset: 8 }
                    SequentialAnimation on y {
                        loops: Animation.Infinite
                        NumberAnimation { to: -8; duration: 2600; easing.type: Easing.InOutSine }
                        NumberAnimation { to: 0; duration: 2600; easing.type: Easing.InOutSine }
                    }
                }
            }
            Title { text: "Te damos la bienvenida a Luma OS"; horizontalAlignment: Text.AlignHCenter }
            Body {
                text: "Tu PC, listo para el día a día y para jugar. En un par de minutos lo dejamos a tu gusto."
                horizontalAlignment: Text.AlignHCenter
            }
            Item { Layout.preferredHeight: 10 }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 14
                Repeater {
                    model: [
                        { icon: "🎮", label: "Listo para jugar" },
                        { icon: "🛡️", label: "Actualizaciones seguras" },
                        { icon: "✨", label: "Diseñado con cariño" }
                    ]
                    delegate: GlassPanel {
                        required property var modelData
                        implicitWidth: chip.implicitWidth + 32
                        implicitHeight: 44
                        radius: 22
                        Row {
                            id: chip
                            anchors.centerIn: parent
                            spacing: 8
                            Text { text: modelData.icon; font.pixelSize: 16 }
                            Text { text: modelData.label; color: "white"; font.pixelSize: 14 }
                        }
                    }
                }
            }
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: gpuPage
        ColumnLayout {
            spacing: 16
            Title { text: "Tu tarjeta gráfica" }
            Body { text: "Luma tiene una versión optimizada para cada tipo de tarjeta gráfica, con los drivers más recientes." }
            Item { Layout.preferredHeight: 6 }
            GlassPanel {
                Layout.fillWidth: true
                Layout.preferredHeight: gpuCol.implicitHeight + 40
                ColumnLayout {
                    id: gpuCol
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 8
                    Repeater {
                        model: backend.gpus
                        delegate: RowLayout {
                            required property string modelData
                            spacing: 12
                            Text { text: "🖥️"; font.pixelSize: 20 }
                            Text { text: modelData; color: "white"; font.pixelSize: 16; Layout.fillWidth: true; elide: Text.ElideRight }
                        }
                    }
                }
            }
            GlassPanel {
                Layout.fillWidth: true
                Layout.preferredHeight: 92
                tint: 0.06
                border.color: backend.gpuMatches ? "#662FD4A0" : "#66FFB547"
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16
                    Rectangle {
                        Layout.preferredWidth: 44; Layout.preferredHeight: 44; radius: 22
                        color: backend.gpuMatches ? "#332FD4A0" : "#33FFB547"
                        Text { anchors.centerIn: parent; text: backend.gpuMatches ? "✓" : "!"; color: backend.gpuMatches ? "#2FD4A0" : "#FFB547"; font.pixelSize: 22; font.weight: Font.Bold }
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text {
                            text: backend.gpuMatches ? "Todo en orden" : "Hay una versión mejor para tu GPU"
                            color: "white"; font.pixelSize: 17; font.weight: Font.DemiBold
                        }
                        Text {
                            text: backend.gpuMatches ? "Estás usando " + backend.currentImage + ", la versión adecuada para tu equipo."
                                                     : "Ahora usas " + backend.currentImage + ". Te recomendamos " + backend.recommendedImage + "."
                            color: Qt.rgba(1, 1, 1, 0.7); font.pixelSize: 14
                            wrapMode: Text.WordWrap; Layout.fillWidth: true
                        }
                    }
                    LumaButton { visible: !backend.gpuMatches; text: "Cambiar"; onClicked: backend.switchGpu() }
                }
            }
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: appsPage
        ColumnLayout {
            spacing: 14
            Title { text: "Añade tus apps favoritas" }
            Body { text: "Firefox, LibreOffice, Steam, Heroic y Bottles ya vienen incluidas. ¿Quieres algo más?" }
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                contentWidth: availableWidth
                GridLayout {
                    width: parent.width - 16
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 12
                    Repeater {
                        model: backend.apps
                        delegate: GlassPanel {
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.preferredHeight: 84
                            radius: 16
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 12
                                Rectangle {
                                    Layout.preferredWidth: 46; Layout.preferredHeight: 46; radius: 13
                                    gradient: Gradient {
                                        GradientStop { position: 0; color: Qt.lighter(modelData.color, 1.25) }
                                        GradientStop { position: 1; color: modelData.color }
                                    }
                                    Text { anchors.centerIn: parent; text: modelData.name.charAt(0); color: "white"; font.pixelSize: 21; font.weight: Font.Bold }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 1
                                    Text { text: modelData.name; color: "white"; font.pixelSize: 15; font.weight: Font.DemiBold }
                                    Text { text: modelData.description; color: Qt.rgba(1, 1, 1, 0.6); font.pixelSize: 12; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true }
                                }
                                Item {
                                    Layout.preferredWidth: 96; Layout.preferredHeight: 34
                                    LumaButton {
                                        anchors.fill: parent
                                        visible: !modelData.installed && !modelData.busy
                                        text: "Instalar"; primary: false
                                        onClicked: backend.installApp(modelData.id)
                                    }
                                    BusyIndicator { anchors.centerIn: parent; visible: modelData.busy; running: visible; implicitWidth: 30; implicitHeight: 30 }
                                    Text { anchors.centerIn: parent; visible: modelData.installed; text: "✓ Instalada"; color: "#2FD4A0"; font.pixelSize: 14; font.weight: Font.DemiBold }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Component {
        id: lookPage
        ColumnLayout {
            spacing: 16
            Title { text: "Elige tu estilo" }
            Body { text: "Puedes cambiarlo cuando quieras desde la configuración del sistema." }
            RowLayout {
                Layout.fillWidth: true
                spacing: 18
                Repeater {
                    model: [ { dark: true, label: "Oscuro" }, { dark: false, label: "Claro" } ]
                    delegate: ColumnLayout {
                        required property var modelData
                        Layout.fillWidth: true
                        spacing: 10
                        Rectangle {
                            id: preview
                            readonly property bool selected: win.darkMode === modelData.dark
                            readonly property bool isDark: modelData.dark
                            Layout.fillWidth: true
                            Layout.preferredHeight: 170
                            radius: 18
                            color: modelData.dark ? "#141626" : "#EEF0F8"
                            border.width: selected ? 3 : 1
                            border.color: selected ? win.accent : Qt.rgba(1, 1, 1, 0.15)
                            scale: selected ? 1 : (lookMouse.containsMouse ? 0.99 : 0.97)
                            Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutBack } }
                            Behavior on border.color { ColorAnimation { duration: 200 } }
                            // Miniatura de una ventana con barra de título y "dock"
                            Rectangle {
                                x: 22; y: 22; width: parent.width * 0.62; height: 98; radius: 10
                                color: modelData.dark ? "#262A40" : "#FFFFFF"
                                Rectangle { x: 10; y: 10; width: 40; height: 8; radius: 4; color: win.accent }
                                Rectangle { x: 10; y: 28; width: parent.width - 20; height: 6; radius: 3; color: modelData.dark ? "#3A3F5C" : "#DADDEB" }
                                Rectangle { x: 10; y: 42; width: parent.width * 0.6; height: 6; radius: 3; color: modelData.dark ? "#3A3F5C" : "#DADDEB" }
                            }
                            Rectangle {
                                anchors.horizontalCenter: parent.horizontalCenter
                                anchors.bottom: parent.bottom; anchors.bottomMargin: 12
                                width: 120; height: 22; radius: 11
                                color: modelData.dark ? Qt.rgba(1, 1, 1, 0.12) : Qt.rgba(0, 0, 0, 0.08)
                                Row {
                                    anchors.centerIn: parent; spacing: 6
                                    Repeater { model: 5; Rectangle { required property int index; width: 12; height: 12; radius: 4; color: index === 0 ? win.accent : (preview.isDark ? "#4A5070" : "#C5C9DA") } }
                                }
                            }
                            MouseArea { id: lookMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: win.darkMode = modelData.dark }
                        }
                        Text { text: modelData.label; color: "white"; font.pixelSize: 15; Layout.alignment: Qt.AlignHCenter }
                    }
                }
            }
            Text { text: "Color de acento"; color: "white"; font.pixelSize: 16; font.weight: Font.DemiBold; Layout.topMargin: 6 }
            RowLayout {
                spacing: 12
                Repeater {
                    model: backend.accents
                    delegate: Rectangle {
                        required property string modelData
                        width: 34; height: 34; radius: 17
                        color: modelData
                        border.width: win.accent === modelData ? 3 : 0
                        border.color: "white"
                        scale: win.accent === modelData ? 1.12 : 1
                        Behavior on scale { NumberAnimation { duration: 180; easing.type: Easing.OutBack } }
                        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: win.accent = modelData }
                    }
                }
                Item { Layout.fillWidth: true }
                LumaButton { text: "Aplicar"; onClicked: backend.applyLook(win.darkMode, win.accent) }
            }
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: donePage
        ColumnLayout {
            spacing: 16
            Item { Layout.fillHeight: true }
            Text { text: "🎉"; font.pixelSize: 64; Layout.alignment: Qt.AlignHCenter }
            Title { text: "¡Todo listo!"; horizontalAlignment: Text.AlignHCenter }
            Body { text: "Luma seguirá actualizándose sola en segundo plano. Si algo falla, puedes volver a la versión anterior desde el menú de arranque."; horizontalAlignment: Text.AlignHCenter }
            Item { Layout.preferredHeight: 8 }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 12
                LumaButton { text: "Abrir Steam"; primary: false; onClicked: backend.launch("steam") }
                LumaButton { text: "Tienda de apps"; primary: false; onClicked: backend.launch("plasma-discover") }
            }
            Item { Layout.preferredHeight: 8 }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 12
                // Interruptor con el estilo de Luma
                Rectangle {
                    Layout.preferredWidth: 46; Layout.preferredHeight: 26; radius: 13
                    color: showAgain.checked ? win.accent : Qt.rgba(1, 1, 1, 0.14)
                    border.color: Qt.rgba(1, 1, 1, 0.2)
                    Behavior on color { ColorAnimation { duration: 200 } }
                    Rectangle {
                        width: 20; height: 20; radius: 10; y: 3
                        x: showAgain.checked ? parent.width - width - 3 : 3
                        color: "white"
                        Behavior on x { NumberAnimation { duration: 220; easing.type: Easing.OutBack } }
                    }
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: showAgain.checked = !showAgain.checked }
                }
                Text { text: "Mostrar esta bienvenida al iniciar sesión"; color: Qt.rgba(1, 1, 1, 0.75); font.pixelSize: 14 }
            }
            Item { Layout.fillHeight: true }
        }
    }
    // Estado del checkbox fuera de la página, para que lo lea el botón "Empezar"
    QtObject { id: showAgain; property bool checked: false }
}
