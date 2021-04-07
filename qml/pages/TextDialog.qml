import QtQuick 2.0
import Sailfish.Silica 1.0

Dialog {
    id: dialogPage

    property alias text: textField.text;

    onStatusChanged: {
        if (status === PageStatus.Active) {
            textField.focus = true
        } else if (status === PageStatus.Deactivating) {
            textField.focus = false
        }
    }

    SilicaFlickable {
        anchors.fill: parent
        contentHeight: column.height

        VerticalScrollDecorator {}

        Column {
            id: column
            width: parent.width

            DialogHeader { title: "Set path" }

            TextField {
                id: textField
                placeholderText: "Please specify path"
                placeholderColor: Theme.errorColor
                width: parent.width
            }
        }

    }
}

