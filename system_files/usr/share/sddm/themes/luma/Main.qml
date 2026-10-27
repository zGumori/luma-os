import QtQuick
import QtQuick.Effects

// Inicio de sesión de Luma OS (SDDM, Qt 6) — pantalla de bloqueo de docs/DESIGN.md:
// reloj grande y fino, avatar, nombre y contraseña en una píldora de cristal oscuro.
// Usa las propiedades que SDDM expone al tema: sddm, userModel, sessionModel, keyboard, config.
Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#05070F"

    readonly property color accent: config.accent ? config.accent : "#2F7BFF"
    readonly property color night: "#14171F"
    property int userIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property bool failed: false

    function login() {
        if (!root.currentUser) return
        failed = false
        sddm.login(root.currentUser.userName, password.text, sessionIndex)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.failed = true
            password.text = ""
            password.forceActiveFocus()
            shake.restart()
        }
    }

    // Repeaters invisibles: dan acceso a los datos del usuario y la sesión seleccionados
    // (un Repeater crea siempre todos sus elementos; un ListView oculto podría no hacerlo)
    readonly property Item currentUser: users.count > 0 ? users.itemAt(Math.min(userIndex, users.count - 1)) : null
    readonly property Item currentSession: sessions.count > 0 ? sessions.itemAt(Math.min(sessionIndex, sessions.count - 1)) : null

    Repeater {
        id: users
        model: userModel
        delegate: Item {
            required property string name
            required property string realName
            required property string icon
            readonly property string userName: name
            readonly property string displayName: realName !== "" ? realName : name
            readonly property string avatar: icon
        }
    }
    Repeater {
        id: sessions
        model: sessionModel
        delegate: Item {
            required property string name
            readonly property string sessionName: name
        }
    }

    // ---------- Fondo ----------
    Image {
        id: wallpaper
        anchors.fill: parent
        source: config.background ? config.background : ""
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        // Entrada suave del fondo
        opacity: status === Image.Ready ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 600 } }
    }
    Rectangle { anchors.fill: parent; color: Qt.rgba(0.02, 0.03, 0.06, 0.25) }

    // ---------- Reloj ----------
    Column {
        id: clock
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: root.width * 0.06
        anchors.topMargin: root.height * 0.08
        spacing: -8
        property date now: new Date()
        Timer { interval: 1000; running: true; repeat: true; onTriggered: clock.now = new Date() }

        Text {
            // Solo la primera letra en mayúscula: «Martes, 27 de octubre»
            readonly property string date: clock.now.toLocaleDateString(Qt.locale(), "dddd, d 'de' MMMM")
            text: date.charAt(0).toUpperCase() + date.slice(1)
            color: Qt.rgba(1, 1, 1, 0.75)
            font.family: "DM Sans"
            font.pixelSize: Math.round(root.height * 0.028)
            font.weight: Font.Medium
        }
        Text {
            text: clock.now.toLocaleTimeString(Qt.locale(), "HH:mm")
            color: "white"
            font.family: "DM Sans"
            font.pixelSize: Math.round(root.height * 0.13)
            font.weight: Font.Light
            font.letterSpacing: -2
        }
        layer.enabled: true
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#80000000"; shadowBlur: 0.6 }
    }

    // ---------- Usuario y contraseña ----------
    Column {
        id: loginBox
        anchors.centerIn: parent
        anchors.verticalCenterOffset: root.height * 0.04
        spacing: 18

        // Aparición: sube y se funde
        opacity: 0
        transform: Translate { id: rise; y: 24 }
        Component.onCompleted: { opacity = 1; rise.y = 0 }
        Behavior on opacity { NumberAnimation { duration: 500; easing.type: Easing.OutCubic } }

        // Avatar
        Item {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 112; height: 112
            Rectangle {
                id: avatarCircle
                anchors.fill: parent
                radius: width / 2
                color: Qt.tint(root.night, Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.55))
                border.width: 3
                border.color: Qt.rgba(1, 1, 1, 0.85)
                Text {
                    anchors.centerIn: parent
                    visible: avatarImage.status !== Image.Ready
                    text: root.currentUser ? root.currentUser.displayName.charAt(0).toUpperCase() : ""
                    color: "white"
                    font.family: "DM Sans"
                    font.pixelSize: 46
                    font.weight: Font.DemiBold
                }
            }
            Image {
                id: avatarImage
                anchors.fill: parent
                anchors.margins: 3
                source: root.currentUser && root.currentUser.avatar ? "file://" + root.currentUser.avatar : ""
                fillMode: Image.PreserveAspectCrop
                visible: false
            }
            MultiEffect {
                anchors.fill: avatarImage
                source: avatarImage
                visible: avatarImage.status === Image.Ready
                maskEnabled: true
                maskSource: avatarMask
            }
            Rectangle { id: avatarMask; anchors.fill: avatarImage; radius: width / 2; visible: false; layer.enabled: true }

            // Flechas para cambiar de usuario si hay varios
            Repeater {
                model: userModel.count > 1 ? [-1, 1] : []
                delegate: Rectangle {
                    required property int modelData
                    x: modelData < 0 ? -56 : parent.width + 18
                    anchors.verticalCenter: parent.verticalCenter
                    width: 38; height: 38; radius: 19
                    color: Qt.rgba(1, 1, 1, userArrow.containsMouse ? 0.22 : 0.12)
                    Image { anchors.centerIn: parent; source: modelData < 0 ? "icons/back.svg" : "icons/next.svg"; sourceSize: Qt.size(40, 40); width: 20; height: 20 }
                    MouseArea {
                        id: userArrow
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: root.userIndex = (root.userIndex + modelData + userModel.count) % userModel.count
                    }
                }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.currentUser ? root.currentUser.displayName : ""
            color: "white"
            font.family: "DM Sans"
            font.pixelSize: 28
            font.weight: Font.DemiBold
            layer.enabled: true
            layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#80000000"; shadowBlur: 0.5 }
        }

        // Píldora de contraseña (cristal oscuro)
        Rectangle {
            id: pill
            anchors.horizontalCenter: parent.horizontalCenter
            width: 360; height: 54
            radius: height / 2
            color: Qt.rgba(0.08, 0.09, 0.12, 0.62)
            border.width: 1
            border.color: root.failed ? "#E5323B" : (password.activeFocus ? Qt.rgba(1, 1, 1, 0.35) : Qt.rgba(1, 1, 1, 0.14))
            Behavior on border.color { ColorAnimation { duration: 200 } }

            SequentialAnimation {
                id: shake
                NumberAnimation { target: pillShift; property: "x"; to: -12; duration: 50 }
                NumberAnimation { target: pillShift; property: "x"; to: 12; duration: 70 }
                NumberAnimation { target: pillShift; property: "x"; to: -8; duration: 60 }
                NumberAnimation { target: pillShift; property: "x"; to: 0; duration: 60 }
            }
            transform: Translate { id: pillShift }

            TextInput {
                id: password
                anchors.left: parent.left
                anchors.right: eye.left
                anchors.leftMargin: 24
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                echoMode: showPassword ? TextInput.Normal : TextInput.Password
                passwordCharacter: "●"
                property bool showPassword: false
                color: "white"
                selectionColor: root.accent
                font.family: "DM Sans"
                font.pixelSize: showPassword ? 18 : 20
                font.letterSpacing: showPassword ? 0 : 4
                focus: true
                clip: true
                onAccepted: root.login()
                onTextChanged: if (text.length > 0) root.failed = false

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    visible: password.text.length === 0
                    text: keyboard.capsLock ? "Mayúsculas activadas" : "Contraseña"
                    color: keyboard.capsLock ? "#F5A524" : Qt.rgba(1, 1, 1, 0.45)
                    font.family: "DM Sans"
                    font.pixelSize: 17
                }
            }
            Rectangle {
                id: eye
                anchors.right: go.left
                anchors.rightMargin: 4
                anchors.verticalCenter: parent.verticalCenter
                width: 40; height: 40; radius: 20
                color: eyeMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.12) : "transparent"
                Image {
                    anchors.centerIn: parent
                    source: password.showPassword ? "icons/eye-off.svg" : "icons/eye.svg"
                    sourceSize: Qt.size(44, 44); width: 22; height: 22
                    opacity: 0.85
                }
                MouseArea { id: eyeMouse; anchors.fill: parent; hoverEnabled: true; onClicked: password.showPassword = !password.showPassword }
            }
            // Botón de entrar: píldora viva con el color de acento
            Rectangle {
                id: go
                anchors.right: parent.right
                anchors.rightMargin: 6
                anchors.verticalCenter: parent.verticalCenter
                width: 42; height: 42; radius: 21
                border.width: 1
                border.color: Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.7)
                gradient: Gradient {
                    GradientStop { position: 0; color: Qt.tint(root.night, Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.25)) }
                    GradientStop { position: 1; color: Qt.tint(root.night, Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.9)) }
                }
                scale: goMouse.pressed ? 0.92 : (goMouse.containsMouse ? 1.06 : 1)
                Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutBack } }
                Image { anchors.centerIn: parent; source: "icons/next.svg"; sourceSize: Qt.size(44, 44); width: 22; height: 22 }
                MouseArea { id: goMouse; anchors.fill: parent; hoverEnabled: true; onClicked: root.login() }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Contraseña incorrecta. Inténtalo de nuevo."
            color: "#FF8A8F"
            font.family: "DM Sans"
            font.pixelSize: 15
            opacity: root.failed ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 200 } }
        }
    }

    // ---------- Pie: marca, sesión y energía ----------
    Row {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 32
        spacing: 12
        Image { source: "icons/logo-mark.svg"; sourceSize: Qt.size(64, 64); width: 30; height: 30; anchors.verticalCenter: parent.verticalCenter }
        Text { text: "luma"; color: "white"; font.family: "DM Sans"; font.pixelSize: 22; font.weight: Font.Bold; anchors.verticalCenter: parent.verticalCenter }
    }

    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 28
        spacing: 10

        // Sesión (clic para cambiar)
        Rectangle {
            visible: sessionModel.count > 1
            height: 44
            width: sessionRow.implicitWidth + 32
            radius: 22
            color: Qt.rgba(0.08, 0.09, 0.12, sessionMouse.containsMouse ? 0.75 : 0.55)
            border.color: Qt.rgba(1, 1, 1, 0.14)
            Row {
                id: sessionRow
                anchors.centerIn: parent
                spacing: 8
                Image { source: "icons/session.svg"; sourceSize: Qt.size(40, 40); width: 18; height: 18; anchors.verticalCenter: parent.verticalCenter }
                Text { text: root.currentSession ? root.currentSession.sessionName : ""; color: "white"; font.family: "DM Sans"; font.pixelSize: 15; anchors.verticalCenter: parent.verticalCenter }
            }
            MouseArea { id: sessionMouse; anchors.fill: parent; hoverEnabled: true; onClicked: root.sessionIndex = (root.sessionIndex + 1) % sessionModel.count }
        }

        // Energía: suspender · reiniciar · apagar, agrupados en una píldora
        Rectangle {
            height: 44
            width: powerRow.implicitWidth + 12
            radius: 22
            color: Qt.rgba(0.08, 0.09, 0.12, 0.55)
            border.color: Qt.rgba(1, 1, 1, 0.14)
            Row {
                id: powerRow
                anchors.centerIn: parent
                spacing: 2
                Repeater {
                    model: [
                        { icon: "sleep", enabled: sddm.canSuspend, action: "suspend" },
                        { icon: "restart", enabled: sddm.canReboot, action: "reboot" },
                        { icon: "power", enabled: sddm.canPowerOff, action: "poweroff" }
                    ]
                    delegate: Rectangle {
                        required property var modelData
                        visible: modelData.enabled
                        width: 40; height: 36; radius: 18
                        color: powerMouse.containsMouse ? (modelData.action === "poweroff" ? "#66E5323B" : Qt.rgba(1, 1, 1, 0.14)) : "transparent"
                        Behavior on color { ColorAnimation { duration: 120 } }
                        Image { anchors.centerIn: parent; source: "icons/" + modelData.icon + ".svg"; sourceSize: Qt.size(40, 40); width: 20; height: 20 }
                        MouseArea {
                            id: powerMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: modelData.action === "suspend" ? sddm.suspend()
                                     : modelData.action === "reboot" ? sddm.reboot() : sddm.powerOff()
                        }
                    }
                }
            }
        }
    }
}
