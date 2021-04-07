import QtQuick 2.0
import Sailfish.Silica 1.0

Page {
    id: page

    // The effective value will be restricted by ApplicationWindow.allowedOrientations
    allowedOrientations: defaultAllowedOrientations

    // To enable PullDownMenu, place our content in a SilicaFlickable
    SilicaFlickable {
        anchors.fill: parent

        // PullDownMenu and PushUpMenu must be declared in SilicaFlickable, SilicaListView or SilicaGridView
        PullDownMenu {
            MenuItem {
                text: qsTr("Backup Configuration")
                onClicked: pageStack.push(Qt.resolvedUrl("ConfigPage.qml"))
            }
        }

        // Tell SilicaFlickable the height of its content.
        contentHeight: column.height

        // Place our content in a Column.  The PageHeader is always placed at the top
        // of the page, followed by our content.
        Column {
            id: column

            width: page.width
            spacing: Theme.paddingLarge
            PageHeader {
                title: qsTr("Restic")
            }

            Button {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Init repository"
                visible: !config.value("repo_initialized")
                onClicked: {
                    python.call('main.init_repo', function callback(result) {
                    config.setValue("repo_initialized", true)
                    })
                }
            }
        }
    }

    onStatusChanged: {
        if (status === PageStatus.Active) {
            if (config.value("backup_destination").length === 0)
                pageStack.push(Qt.resolvedUrl("ConfigPage.qml"))
        }
    }
}
