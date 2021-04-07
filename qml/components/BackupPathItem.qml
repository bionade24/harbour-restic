import QtQuick 2.0
import Sailfish.Silica 1.0

Item {
    property string path;
    TextArea {
        id: backupPaths
        label: "Path to backup"
        text: path
        placeholderText: ": No path to back up specified."
        width: parent.width
        inputMethodHints: Qt.ImhUrlCharactersOnly | Qt.ImhNoAutoUppercase | Qt.ImhNoPredictiveText
    }
}
