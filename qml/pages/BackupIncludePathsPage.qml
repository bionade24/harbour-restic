import QtQuick 2.0
import Sailfish.Silica 1.0
import "."

Page {
    id: backupIncludePathsPage
    property ListModel backupIncludePaths: ListModel {}

    Component.onCompleted: {
        backupIncludePaths.append(config.backup_include_paths.value)
    }

    Component.onDestruction: {
        var array = []
        for (var i = 0; i < backupIncludePaths.rowCount(); i++) {
            array.push( { "path": backupIncludePaths.get(i).path } )
        }
        config.backup_include_paths.value = array
    }

    SilicaListView {
        id: listView
        anchors.fill: parent
        contentHeight: Theme.paddingLarge
        model: backupIncludePaths
        delegate: ListItem {
            Label {
                text: path
                font.pixelSize: Theme.fontSizeMedium
                anchors.centerIn: parent.Center
                padding: Theme.paddingMedium
            }
            menu: ContextMenu {
                MenuItem {
                    text: "Remove"
                    onClicked: remorseAction("Removing", function() { backupIncludePaths.remove(index) })
                }
            }
            onClicked: pageStack.push(changeDialog)
            Component {
                id: changeDialog
                TextDialog {
                    id: dialogPage
                    text: path
                    onAccepted: {
                        path = text
                    }
                }
            }
        }

        VerticalScrollDecorator {}

        header: PageHeader {
            title: "Select paths to backup"
        }

        PullDownMenu {
            MenuItem {
                id: addPathItem
                text: qsTr("Add path")
                onClicked: {
                    pageStack.push(addDialog)
                }
                Component {
                    id: addDialog
                    TextDialog {
                        id: dialogPage
                        text: ""
                        onAccepted: {
                            backupIncludePaths.append( { "path": text } )
                        }
                    }
                }
            }
        }
    }
}
