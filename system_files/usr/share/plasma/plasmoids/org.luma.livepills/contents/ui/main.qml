import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

// Píldoras vivas de la Barra Luma. Cada píldora vive en su propio archivo y se carga
// con un Loader: si una API de Plasma cambia, falla esa píldora y no el widget entero.
PlasmoidItem {
    id: root

    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation

    fullRepresentation: Item {
        id: rep
        readonly property real pillHeight: Math.max(24, Math.min(height - 10, 36))

        Layout.minimumWidth: row.implicitWidth
        Layout.preferredWidth: row.implicitWidth
        Layout.fillHeight: true

        RowLayout {
            id: row
            anchors.centerIn: parent
            spacing: 8

            Repeater {
                model: ["MediaPill.qml", "DndPill.qml"]
                delegate: Loader {
                    required property string modelData
                    source: modelData
                    visible: status === Loader.Ready && item.shown
                    // Con el alto fijado, el Loader redimensiona la píldora
                    Layout.preferredHeight: rep.pillHeight
                }
            }
        }
    }
}
