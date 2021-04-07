import QtQuick 2.0
import Sailfish.Silica 1.0
import Sailfish.Pickers 1.0
import "../components"

Page {
    id: configPage

    allowedOrientations: defaultAllowedOrientations

    property string backupDestination: config.value("backup_destination");
    property string sshKeyPath: config.value("ssh_key", "~/.ssh/id_rsa");

    Component.onDestruction: {
        config.setValue("backup_destination", configPage.backupDestination)
        config.setValue("ssh_key", configPage.sshKeyPath)
        config.setValue("exclude_rules", excludeRulesArea.text)
        config.setValue("env_vars", envVarsArea.text)
        console.log("Configuration written to disk.")
    }

    SilicaFlickable {
        anchors.fill: parent
        contentHeight: configColumn.height + Theme.paddingLarge

        VerticalScrollDecorator {}

        Column {
            id: configColumn
            width: parent.width

            PageHeader {
                title: "Restic configuration"
            }

            Button {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Restic online documentation"
                onClicked: Qt.openUrlExternally("https://restic.readthedocs.io/")
            }

            TextField {
                id: backupDestinationEntry
                label: "Backup destination"
                placeholderText: label + ": No path or URL set"
                width: parent.width
                text: configPage.backupDestination
                inputMethodHints: Qt.ImhUrlCharactersOnly | Qt.ImhNoAutoUppercase | Qt.ImhNoPredictiveText

                Binding { target: configPage; property: "backupDestination"; value: backupDestinationEntry.text }
            }

            ValueButton {
                label: "SSH key"
                value: configPage.sshKeyPath
                onClicked: pageStack.push(sshKeyPicker)
                visible: {
                    var patt = /^sftp:/;
                    return patt.test(configPage.backupDestination)
                }
            }

            PasswordField {
                id: pwField
                label: "Repo password"
                placeholderText: label

                property string prevPassword;

                Component.onCompleted: {
                    python.call('sfsecret.get_secret',
                        ["restic", "password"],
                        function callback(result) {
                            text = result
                            prevPassword = result
                        }
                    );
                }

                Component.onDestruction: {
                    if (text != prevPassword) {
                        console.log("PW change, store in SFSecret")
                        python.call('sfsecret.update_secret',
                            ["restic", "password", text]);
                    }
                }
            }

            ValueButton {
                id: backupIncludePathsButton
                label: "Paths to back up:"
                value: serializeBackupPaths()
                onClicked: pageStack.push(Qt.resolvedUrl("BackupIncludePathsPage.qml"))

                function serializeBackupPaths() {
                    var paths = "";
                    for (var i = 0; i < config.backup_include_paths.value.length; i++)
                    {
                        paths += (config.backup_include_paths.value[i].path + "\n")
                    }
                    return paths
                }
            }

            TextArea {
                id: excludeRulesArea
                width: parent.width
                label: "Exclude rules"
                text: config.value("exclude_rules", "/home/**/.cache")
                placeholderText: "Enter exclude rules here"
            }

            TextArea {
                id: envVarsArea
                width: parent.width
                label: "Enviroment variables"
                text: config.value("env_vars")
                placeholderText: "Enter env vars to be set during execution"
                inputMethodHints: Qt.ImhUppercaseOnly
                onFocusChanged: {
                    text = text.toUpperCase()
                }
            }
        }
    }

    Component {
        id: sshKeyPicker
        FilePickerPage {
            title: "Set path of SSH key"
            onSelectedContentPropertiesChanged: {
                configPage.sshKeyPath = selectedContentProperties.filePath
            }
        }
    }
}
