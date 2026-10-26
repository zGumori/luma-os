import QtQuick
import QtQuick.Controls
import QtQuick.Effects
import QtQuick.Layouts

// Bienvenida a Luma — estilo Luma Glass (docs/DESIGN.md): ventana de cristal claro
// con bisel grueso, controles en píldora y píldoras vivas con brillo de color.
ApplicationWindow {
    id: win
    readonly property int shadowMargin: 40
    width: 940 + shadowMargin * 2
    height: 640 + shadowMargin * 2
    visible: true
    title: "Bienvenida a Luma"
    flags: Qt.Window | Qt.FramelessWindowHint
    color: "transparent"

    // ---------- Tokens ----------
    QtObject {
        id: t
        readonly property color ink: "#14161C"
        readonly property color ink2: "#6B7080"
        readonly property color ink3: "#A3A8B5"
        readonly property color paper: "#F7F8FB"
        readonly property color night: "#14171F"
        readonly property color liveGreen: "#21C07A"
        readonly property color liveAmber: "#F5A524"
        readonly property color liveBlue: "#1E5BFF"
        readonly property int radiusWindow: 28
        readonly property int radiusCard: 20
    }

    property int step: 0
    readonly property var steps: ["Bienvenida", "Tarjeta gráfica", "Apps", "Aspecto", "Listo"]
    readonly property var pages: [welcomePage, gpuPage, appsPage, lookPage, donePage]
    property bool darkMode: false
    property color accent: backend.accents[0]
    property bool showAgain: false

    function go(i) {
        if (i < 0 || i >= steps.length || i === step) return
        stack.forward = i > step
        step = i
        stack.replace(pages[i])
    }
    function icon(name, color) { return "image://icon/" + name + "/" + String(color).replace("#", "") }

    // ---------- Componentes ----------

    // Icono de trazo recoloreable
    component Icon: Image {
        property string name
        property color tint: t.ink
        property int size: 20
        source: name !== "" ? win.icon(name, tint) : ""
        sourceSize: Qt.size(size * 2, size * 2)
        width: size; height: size
        Layout.preferredWidth: size; Layout.preferredHeight: size
        smooth: true
    }

    // Píldora viva: base oscura con brillo de color desde abajo
    component LivePill: Rectangle {
        id: pill
        property color live: win.accent
        property string text
        property string iconName
        property bool interactive: false
        signal clicked()
        implicitHeight: 44
        implicitWidth: pillRow.implicitWidth + 36
        radius: height / 2
        border.width: 1
        border.color: Qt.rgba(live.r, live.g, live.b, 0.6)
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.tint(t.night, Qt.rgba(pill.live.r, pill.live.g, pill.live.b, 0.12)) }
            GradientStop { position: 1.0; color: Qt.tint(t.night, Qt.rgba(pill.live.r, pill.live.g, pill.live.b, 0.78)) }
        }
        scale: pillMouse.pressed ? 0.96 : (pillMouse.containsMouse && interactive ? 1.03 : 1)
        Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutBack } }
        Rectangle { // línea de luz superior
            anchors { left: parent.left; right: parent.right; top: parent.top; leftMargin: pill.radius; rightMargin: pill.radius; topMargin: 1 }
            height: 1; color: Qt.rgba(1, 1, 1, 0.22)
        }
        RowLayout {
            id: pillRow
            anchors.centerIn: parent
            spacing: 8
            Icon { visible: pill.iconName !== ""; name: pill.iconName; tint: "#FFFFFF"; size: 18 }
            Text { text: pill.text; color: "white"; font.pixelSize: 15; font.weight: Font.DemiBold }
        }
        MouseArea {
            id: pillMouse
            anchors.fill: parent
            enabled: pill.interactive
            hoverEnabled: true
            cursorShape: pill.interactive ? Qt.PointingHandCursor : Qt.ArrowCursor
            onClicked: pill.clicked()
        }
    }

    // Botón secundario: píldora blanca
    component SoftButton: Rectangle {
        id: soft
        property string text
        property string iconName
        property bool round: false
        signal clicked()
        implicitHeight: 44
        implicitWidth: round ? implicitHeight : softRow.implicitWidth + 36
        radius: height / 2
        color: softMouse.containsMouse ? "#FFFFFF" : Qt.rgba(1, 1, 1, 0.82)
        border.width: 1
        border.color: Qt.rgba(0, 0, 0, 0.08)
        scale: softMouse.pressed ? 0.95 : (softMouse.containsMouse ? 1.03 : 1)
        Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutBack } }
        Behavior on color { ColorAnimation { duration: 150 } }
        layer.enabled: true
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#260A0E1E"; shadowBlur: 0.5; shadowVerticalOffset: 3 }
        RowLayout {
            id: softRow
            anchors.centerIn: parent
            spacing: 8
            Icon { visible: soft.iconName !== ""; name: soft.iconName; size: 18 }
            Text { visible: soft.text !== ""; text: soft.text; color: t.ink; font.pixelSize: 15; font.weight: Font.DemiBold }
        }
        MouseArea { id: softMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: soft.clicked() }
    }

    // Tarjeta de cristal claro dentro de la ventana
    component Card: Rectangle {
        radius: t.radiusCard
        color: Qt.rgba(1, 1, 1, 0.62)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.9)
    }

    component Title: Text { color: t.ink; font.pixelSize: 30; font.weight: Font.Bold; font.letterSpacing: -0.4; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    component Body: Text { color: t.ink2; font.pixelSize: 16; lineHeight: 1.3; wrapMode: Text.WordWrap; Layout.fillWidth: true }

    // ---------- Ventana ----------

    // Sombra
    Rectangle {
        anchors.fill: body
        radius: t.radiusWindow
        color: "#FFFFFF"
        opacity: body.opacity
        scale: body.scale
        layer.enabled: true
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#590A0E1E"; shadowBlur: 1.0; shadowVerticalOffset: 18; shadowScale: 0.98 }
    }

    Item {
        id: body
        anchors.fill: parent
        anchors.margins: win.shadowMargin

        // Animación de apertura: escala + fundido
        opacity: 0
        scale: 0.92
        Component.onCompleted: { opacity = 1; scale = 1 }
        Behavior on opacity { NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }
        Behavior on scale { NumberAnimation { duration: 420; easing.type: Easing.OutBack; easing.overshoot: 0.8 } }

        // Cristal claro: base + tinte de color difuminado (simula el fondo que se ve a través)
        Rectangle { id: glassMask; anchors.fill: parent; radius: t.radiusWindow; visible: false; layer.enabled: true }
        Item {
            anchors.fill: parent
            layer.enabled: true
            layer.effect: MultiEffect { maskEnabled: true; maskSource: glassMask }
            Rectangle { anchors.fill: parent; color: t.paper }
            Item {
                anchors.fill: parent
                opacity: 0.55
                layer.enabled: true
                layer.effect: MultiEffect { blurEnabled: true; blur: 1.0; blurMax: 64 }
                component Blob: Rectangle {
                    id: blob
                    property real cx
                    property real cy
                    property int period: 16000
                    property real dx: 0
                    width: 380; height: width; radius: width / 2
                    x: cx * body.width - width / 2 + dx
                    y: cy * body.height - height / 2
                    SequentialAnimation on dx {
                        loops: Animation.Infinite
                        NumberAnimation { to: 70; duration: blob.period; easing.type: Easing.InOutSine }
                        NumberAnimation { to: -70; duration: blob.period; easing.type: Easing.InOutSine }
                    }
                }
                Blob { cx: 0.08; cy: 0.05; color: "#BFE3FF" }
                Blob { cx: 0.95; cy: 0.12; color: win.accent; opacity: 0.45; period: 19000; Behavior on color { ColorAnimation { duration: 500 } } }
                Blob { cx: 0.7; cy: 1.05; width: 460; color: "#E6D9FF"; period: 23000 }
            }
            Rectangle { anchors.fill: parent; color: Qt.rgba(1, 1, 1, 0.35) }
        }
        // Bisel grueso + filo exterior
        Rectangle { anchors.fill: parent; anchors.margins: -1; radius: t.radiusWindow + 1; color: "transparent"; border.width: 1; border.color: Qt.rgba(0, 0, 0, 0.12) }
        Rectangle { anchors.fill: parent; radius: t.radiusWindow; color: "transparent"; border.width: 5; border.color: Qt.rgba(1, 1, 1, 0.7) }

        // ---------- Barra de título ----------
        Item {
            id: titleBar
            anchors { left: parent.left; right: parent.right; top: parent.top; margins: 16 }
            height: 44
            MouseArea { anchors.fill: parent; onPressed: win.startSystemMove() }

            SoftButton {
                anchors.left: parent.left
                round: true
                iconName: "back"
                opacity: win.step > 0 ? 1 : 0
                visible: opacity > 0
                Behavior on opacity { NumberAnimation { duration: 200 } }
                onClicked: win.go(win.step - 1)
            }
            Text {
                anchors.centerIn: parent
                text: "Bienvenida a Luma"
                color: t.ink
                font.pixelSize: 17
                font.weight: Font.DemiBold
            }
            // Píldora de controles: minimizar · maximizar (no disponible) · cerrar
            Rectangle {
                anchors.right: parent.right
                width: controls.implicitWidth + 12
                height: 40
                radius: 20
                color: Qt.rgba(1, 1, 1, 0.9)
                border.width: 1
                border.color: Qt.rgba(0, 0, 0, 0.07)
                Row {
                    id: controls
                    anchors.centerIn: parent
                    spacing: 2
                    Repeater {
                        model: [
                            { icon: "minimize", enabled: true, action: "min" },
                            { icon: "maximize", enabled: false, action: "" },
                            { icon: "close", enabled: true, action: "close" }
                        ]
                        delegate: Rectangle {
                            required property var modelData
                            width: 34; height: 32; radius: 16
                            color: ctlMouse.containsMouse && modelData.enabled
                                   ? (modelData.action === "close" ? "#FFE3E4" : Qt.rgba(0, 0, 0, 0.06)) : "transparent"
                            Behavior on color { ColorAnimation { duration: 120 } }
                            Icon {
                                anchors.centerIn: parent
                                name: modelData.icon
                                size: 18
                                tint: ctlMouse.containsMouse && modelData.action === "close" ? "#E5323B" : t.ink
                                opacity: modelData.enabled ? 1 : 0.3
                            }
                            MouseArea {
                                id: ctlMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                enabled: modelData.enabled
                                onClicked: modelData.action === "min" ? win.showMinimized() : Qt.quit()
                            }
                        }
                    }
                }
            }
        }

        // ---------- Progreso por pasos ----------
        Row {
            id: progress
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: titleBar.bottom
            anchors.topMargin: 14
            spacing: 6
            Repeater {
                model: win.steps.length
                delegate: Rectangle {
                    required property int index
                    height: 8
                    width: index === win.step ? 34 : 8
                    radius: 4
                    color: index === win.step ? win.accent : (index < win.step ? Qt.rgba(win.accent.r, win.accent.g, win.accent.b, 0.4) : Qt.rgba(0, 0, 0, 0.12))
                    Behavior on width { NumberAnimation { duration: 320; easing.type: Easing.OutBack } }
                    Behavior on color { ColorAnimation { duration: 250 } }
                    MouseArea { anchors.fill: parent; anchors.margins: -6; onClicked: win.go(index) }
                }
            }
        }

        // ---------- Contenido ----------
        StackView {
            id: stack
            property bool forward: true
            anchors { left: parent.left; right: parent.right; top: progress.bottom; bottom: footer.top; leftMargin: 56; rightMargin: 56; topMargin: 18; bottomMargin: 12 }
            clip: true
            initialItem: welcomePage
            replaceEnter: Transition {
                ParallelAnimation {
                    NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 380; easing.type: Easing.OutCubic }
                    NumberAnimation { property: "x"; from: stack.forward ? 40 : -40; to: 0; duration: 420; easing.type: Easing.OutCubic }
                }
            }
            replaceExit: Transition {
                ParallelAnimation {
                    NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 200; easing.type: Easing.InCubic }
                    NumberAnimation { property: "x"; from: 0; to: stack.forward ? -30 : 30; duration: 200; easing.type: Easing.InCubic }
                }
            }
        }

        // ---------- Pie ----------
        Item {
            id: footer
            anchors { left: parent.left; right: parent.right; bottom: parent.bottom; leftMargin: 28; rightMargin: 28; bottomMargin: 24 }
            height: 48
            Text {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                text: (win.step + 1) + " de " + win.steps.length + " · " + win.steps[win.step]
                color: t.ink3
                font.pixelSize: 14
            }
            LivePill {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                height: 46
                interactive: true
                live: win.accent
                text: win.step === win.steps.length - 1 ? "Empezar" : "Siguiente"
                iconName: win.step === win.steps.length - 1 ? "sparkle" : "next"
                onClicked: win.step === win.steps.length - 1 ? backend.finish(win.showAgain) : win.go(win.step + 1)
            }
        }

        // ---------- Aviso ----------
        LivePill {
            id: toast
            live: "#E5323B"
            iconName: "alert"
            anchors.horizontalCenter: parent.horizontalCenter
            y: opacity > 0 ? parent.height - height - 90 : parent.height - height - 70
            opacity: 0
            Behavior on opacity { NumberAnimation { duration: 250 } }
            Behavior on y { NumberAnimation { duration: 320; easing.type: Easing.OutBack } }
            Timer { id: toastTimer; interval: 4500; onTriggered: toast.opacity = 0 }
        }
        Connections {
            target: backend
            function onMessage(text) { toast.text = text; toast.opacity = 1; toastTimer.restart() }
        }
    }

    // ---------- Páginas ----------

    Component {
        id: welcomePage
        ColumnLayout {
            spacing: 0
            Item { Layout.fillHeight: true }
            Item {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 168; Layout.preferredHeight: 168
                Image {
                    width: 168; height: 168
                    source: backend.logo
                    sourceSize: Qt.size(336, 336)
                    layer.enabled: true
                    layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#662F4BFF"; shadowBlur: 1.0; shadowVerticalOffset: 14 }
                    SequentialAnimation on y {
                        loops: Animation.Infinite
                        NumberAnimation { from: 0; to: -10; duration: 2800; easing.type: Easing.InOutSine }
                        NumberAnimation { from: -10; to: 0; duration: 2800; easing.type: Easing.InOutSine }
                    }
                }
            }
            Item { Layout.preferredHeight: 26 }
            Text { text: "luma os · " + backend.currentImage; color: t.ink3; font.pixelSize: 14; font.weight: Font.Medium; Layout.alignment: Qt.AlignHCenter }
            Item { Layout.preferredHeight: 6 }
            Title { text: "Te damos la bienvenida"; font.pixelSize: 40; horizontalAlignment: Text.AlignHCenter }
            Item { Layout.preferredHeight: 8 }
            Body {
                text: "Tu PC, listo para el día a día y para jugar.\nEn un par de minutos lo dejamos a tu gusto."
                horizontalAlignment: Text.AlignHCenter
            }
            Item { Layout.preferredHeight: 26 }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 12
                LivePill { live: t.liveBlue; iconName: "gamepad"; text: "Listo para jugar" }
                LivePill { live: t.liveGreen; iconName: "shield"; text: "Actualizaciones seguras" }
                LivePill { live: t.liveAmber; iconName: "sparkle"; text: "Diseño cuidado" }
            }
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: gpuPage
        ColumnLayout {
            spacing: 0
            Title { text: "Tu tarjeta gráfica" }
            Item { Layout.preferredHeight: 8 }
            Body { text: "Luma tiene una versión optimizada para cada tipo de gráfica, con los drivers más recientes." }
            Item { Layout.preferredHeight: 26 }
            Card {
                Layout.fillWidth: true
                Layout.preferredHeight: gpuList.implicitHeight + 40
                ColumnLayout {
                    id: gpuList
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 12
                    Repeater {
                        model: backend.gpus
                        delegate: RowLayout {
                            required property string modelData
                            spacing: 14
                            Rectangle {
                                Layout.preferredWidth: 44; Layout.preferredHeight: 44; radius: 12
                                color: t.night
                                Icon { anchors.centerIn: parent; name: "monitor"; tint: "#FFFFFF"; size: 22 }
                            }
                            Text { text: modelData; color: t.ink; font.pixelSize: 17; font.weight: Font.Medium; Layout.fillWidth: true; elide: Text.ElideRight }
                        }
                    }
                }
            }
            Item { Layout.preferredHeight: 16 }
            Card {
                Layout.fillWidth: true
                Layout.preferredHeight: 96
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16
                    LivePill {
                        live: backend.gpuMatches ? t.liveGreen : t.liveAmber
                        iconName: backend.gpuMatches ? "check" : "alert"
                        text: backend.gpuMatches ? "Todo en orden" : "Hay una versión mejor"
                    }
                    Text {
                        text: backend.gpuMatches ? "Estás usando <b>" + backend.currentImage + "</b>, la versión adecuada para tu equipo."
                                                 : "Ahora usas <b>" + backend.currentImage + "</b>.<br>Te recomendamos <b>" + backend.recommendedImage + "</b>."
                        textFormat: Text.StyledText
                        color: t.ink2; font.pixelSize: 15
                        wrapMode: Text.WordWrap; Layout.fillWidth: true
                    }
                    SoftButton { visible: !backend.gpuMatches; text: "Cambiar"; iconName: "download"; onClicked: backend.switchGpu() }
                }
            }
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: appsPage
        ColumnLayout {
            spacing: 0
            Title { text: "Añade tus apps favoritas" }
            Item { Layout.preferredHeight: 8 }
            Body { text: "Firefox, LibreOffice, Steam, Heroic y Bottles ya vienen incluidas. ¿Quieres algo más?" }
            Item { Layout.preferredHeight: 18 }
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                contentWidth: availableWidth
                GridLayout {
                    width: parent.width - 14
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 12
                    Repeater {
                        model: backend.apps
                        delegate: Card {
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.preferredHeight: 80
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 14
                                // Icono squircle con brillo
                                Rectangle {
                                    Layout.preferredWidth: 50; Layout.preferredHeight: 50; radius: 13
                                    gradient: Gradient {
                                        GradientStop { position: 0; color: Qt.lighter(modelData.color, 1.3) }
                                        GradientStop { position: 1; color: modelData.color }
                                    }
                                    Rectangle {
                                        anchors { left: parent.left; right: parent.right; top: parent.top; margins: 3 }
                                        height: parent.height * 0.45; radius: 10
                                        color: Qt.rgba(1, 1, 1, 0.18)
                                    }
                                    Text { anchors.centerIn: parent; text: modelData.name.charAt(0); color: "white"; font.pixelSize: 22; font.weight: Font.Bold }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2
                                    Text { text: modelData.name; color: t.ink; font.pixelSize: 16; font.weight: Font.DemiBold }
                                    Text { text: modelData.description; color: t.ink2; font.pixelSize: 13; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true }
                                }
                                Item {
                                    Layout.preferredWidth: 104; Layout.preferredHeight: 38
                                    SoftButton {
                                        anchors.fill: parent
                                        visible: !modelData.installed && !modelData.busy
                                        text: "Instalar"
                                        onClicked: backend.installApp(modelData.id)
                                    }
                                    // Progreso indeterminado tipo deslizador
                                    Rectangle {
                                        visible: modelData.busy
                                        anchors.centerIn: parent
                                        width: 84; height: 6; radius: 3
                                        color: "#C9CCD4"
                                        clip: true
                                        Rectangle {
                                            width: 30; height: parent.height; radius: 3
                                            color: win.accent
                                            SequentialAnimation on x {
                                                running: modelData.busy
                                                loops: Animation.Infinite
                                                NumberAnimation { from: -30; to: 84; duration: 1100; easing.type: Easing.InOutCubic }
                                            }
                                        }
                                    }
                                    RowLayout {
                                        visible: modelData.installed
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Icon { name: "check"; tint: t.liveGreen; size: 18 }
                                        Text { text: "Instalada"; color: t.liveGreen; font.pixelSize: 15; font.weight: Font.DemiBold }
                                    }
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
            spacing: 0
            Title { text: "Elige tu estilo" }
            Item { Layout.preferredHeight: 8 }
            Body { text: "Puedes cambiarlo cuando quieras desde la configuración del sistema." }
            Item { Layout.preferredHeight: 22 }
            RowLayout {
                Layout.fillWidth: true
                spacing: 22
                Repeater {
                    model: [ { dark: false, label: "Claro", icon: "sun" }, { dark: true, label: "Oscuro", icon: "moon" } ]
                    delegate: ColumnLayout {
                        required property var modelData
                        Layout.fillWidth: true
                        spacing: 12
                        // Miniatura de escritorio Luma: fondo, ventana de cristal y barra con píldoras
                        Rectangle {
                            id: preview
                            readonly property bool selected: win.darkMode === modelData.dark
                            readonly property bool isDark: modelData.dark
                            Layout.fillWidth: true
                            Layout.preferredHeight: 190
                            radius: 20
                            gradient: Gradient {
                                GradientStop { position: 0; color: preview.isDark ? "#1A2440" : "#CFE6FF" }
                                GradientStop { position: 1; color: preview.isDark ? "#3A1E4F" : "#8DB8FF" }
                            }
                            border.width: selected ? 3 : 0
                            border.color: win.accent
                            scale: selected ? 1 : (lookMouse.containsMouse ? 0.99 : 0.97)
                            Behavior on scale { NumberAnimation { duration: 220; easing.type: Easing.OutBack } }
                            // Ventana
                            Rectangle {
                                x: parent.width * 0.16; y: 22; width: parent.width * 0.68; height: 104; radius: 12
                                color: preview.isDark ? Qt.rgba(0.12, 0.13, 0.18, 0.92) : Qt.rgba(1, 1, 1, 0.9)
                                border.width: 2; border.color: preview.isDark ? Qt.rgba(1, 1, 1, 0.12) : Qt.rgba(1, 1, 1, 1)
                                Rectangle { anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 8; width: 34; height: 12; radius: 6; color: preview.isDark ? Qt.rgba(1, 1, 1, 0.14) : "#EDEFF4" }
                                Rectangle { anchors.horizontalCenter: parent.horizontalCenter; y: 26; width: 40; height: 40; radius: 10; color: win.accent }
                                Rectangle { anchors.horizontalCenter: parent.horizontalCenter; y: 74; width: parent.width * 0.5; height: 6; radius: 3; color: preview.isDark ? Qt.rgba(1, 1, 1, 0.3) : "#D5D8E2" }
                                Rectangle { anchors.horizontalCenter: parent.horizontalCenter; y: 86; width: parent.width * 0.3; height: 6; radius: 3; color: preview.isDark ? Qt.rgba(1, 1, 1, 0.18) : "#E4E6EE" }
                            }
                            // Barra Luma
                            Rectangle {
                                anchors { left: parent.left; right: parent.right; bottom: parent.bottom; margins: 10 }
                                height: 28; radius: 14
                                color: Qt.rgba(0.08, 0.09, 0.12, 0.82)
                                Row {
                                    anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter
                                    spacing: 6
                                    Image { source: backend.logoMark; sourceSize: Qt.size(28, 28); width: 14; height: 14 }
                                    Repeater { model: ["#3D8BFF", "#F0457A", "#21C07A"]; Rectangle { required property string modelData; width: 14; height: 14; radius: 4; color: modelData } }
                                }
                                Rectangle { anchors.centerIn: parent; width: 48; height: 16; radius: 8; color: Qt.tint(t.night, Qt.rgba(win.accent.r, win.accent.g, win.accent.b, 0.7)); border.width: 1; border.color: win.accent }
                                Rectangle { anchors.right: parent.right; anchors.rightMargin: 10; anchors.verticalCenter: parent.verticalCenter; width: 40; height: 16; radius: 8; color: "transparent"; border.width: 1; border.color: Qt.rgba(1, 1, 1, 0.3) }
                            }
                            MouseArea { id: lookMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: win.darkMode = modelData.dark }
                        }
                        RowLayout {
                            Layout.alignment: Qt.AlignHCenter
                            spacing: 8
                            Icon { name: modelData.icon; size: 18; tint: win.darkMode === modelData.dark ? t.ink : t.ink3 }
                            Text { text: modelData.label; color: win.darkMode === modelData.dark ? t.ink : t.ink2; font.pixelSize: 16; font.weight: Font.DemiBold }
                        }
                    }
                }
            }
            Item { Layout.preferredHeight: 20 }
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                Text { text: "Acento"; color: t.ink; font.pixelSize: 16; font.weight: Font.DemiBold; Layout.rightMargin: 6 }
                Repeater {
                    model: backend.accents
                    delegate: Rectangle {
                        required property string modelData
                        readonly property bool chosen: Qt.colorEqual(win.accent, modelData)
                        width: 34; height: 34; radius: 17
                        color: "white"
                        border.width: 1; border.color: Qt.rgba(0, 0, 0, 0.08)
                        Rectangle {
                            anchors.centerIn: parent
                            width: parent.chosen ? 24 : 30; height: width; radius: width / 2
                            color: modelData
                            Behavior on width { NumberAnimation { duration: 200; easing.type: Easing.OutBack } }
                        }
                        scale: chosen ? 1.12 : 1
                        Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutBack } }
                        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: win.accent = modelData }
                    }
                }
                Item { Layout.fillWidth: true }
                SoftButton { text: "Aplicar"; iconName: "check"; onClicked: backend.applyLook(win.darkMode, win.accent.toString()) }
            }
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: donePage
        ColumnLayout {
            spacing: 0
            Item { Layout.fillHeight: true }
            // Estrella con halo que respira
            Item {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 150; Layout.preferredHeight: 150
                Rectangle {
                    anchors.centerIn: parent
                    width: 150; height: 150; radius: 75
                    color: win.accent
                    opacity: 0.18
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        NumberAnimation { from: 0.85; to: 1.08; duration: 1800; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.08; to: 0.85; duration: 1800; easing.type: Easing.InOutSine }
                    }
                }
                Image { anchors.centerIn: parent; source: backend.logo; sourceSize: Qt.size(220, 220); width: 110; height: 110 }
            }
            Item { Layout.preferredHeight: 22 }
            Title { text: "¡Todo listo!"; font.pixelSize: 40; horizontalAlignment: Text.AlignHCenter }
            Item { Layout.preferredHeight: 8 }
            Body {
                text: "Luma se actualiza sola en segundo plano. Si algo falla,\npuedes volver a la versión anterior desde el menú de arranque."
                horizontalAlignment: Text.AlignHCenter
            }
            Item { Layout.preferredHeight: 24 }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 12
                SoftButton { text: "Abrir Steam"; iconName: "gamepad"; onClicked: backend.launch("steam") }
                SoftButton { text: "Tienda de apps"; iconName: "bag"; onClicked: backend.launch("plasma-discover") }
            }
            Item { Layout.preferredHeight: 24 }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 12
                Rectangle {
                    Layout.preferredWidth: 46; Layout.preferredHeight: 26; radius: 13
                    color: win.showAgain ? win.accent : "#D5D8E2"
                    Behavior on color { ColorAnimation { duration: 200 } }
                    Rectangle {
                        width: 20; height: 20; radius: 10; y: 3
                        x: win.showAgain ? parent.width - width - 3 : 3
                        color: "white"
                        Behavior on x { NumberAnimation { duration: 220; easing.type: Easing.OutBack } }
                    }
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: win.showAgain = !win.showAgain }
                }
                Text { text: "Mostrar esta bienvenida al iniciar sesión"; color: t.ink2; font.pixelSize: 14 }
            }
            Item { Layout.fillHeight: true }
        }
    }
}
