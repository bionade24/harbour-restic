import QtQuick 2.0
import Sailfish.Silica 1.0
import Nemo.Configuration 1.0
import io.thp.pyotherside 1.5
import "pages"

ApplicationWindow
{
    initialPage: Component { Main { } }
    cover: Qt.resolvedUrl("cover/CoverPage.qml")
    allowedOrientations: defaultAllowedOrientations

    Python {
        id: python

        property bool initialized;
        property var configQueue: [];

        Component.onCompleted: {
            addImportPath(Qt.resolvedUrl('../python'));
            importModule('main', function () {});
            importModule('sfsecret', function () {});
            //Use pyotherside.send to send progress e.g.
            setHandler('info', function(data) {
                 console.log(data)
            });
            setHandler('updated', function(data) {
                console.log(data)
            });

            setHandler('finished', function(data) {
                 console.log(JSON.stringify(data))
            });
            initialized = true;
            for (var i = 0; i < configQueue.length; i++) {
                console.log(configQueue[i].key, configQueue[i].value)
                setConfig(configQueue[i].key, configQueue[i].value)
            }
            configQueue = undefined
            //Another example, same as above
            //setHandler('finished', function(newvalue) {
            //    page.downloading = false;
            //    mainLabel.text = 'Color is ' + newvalue + '.';
            //});

        }

        function setConfig(key, value) {
            if(initialized) {
                call('main.set_config', [key, value]);
            } else {
                configQueue.push({key: key, value: value})
            }
        }

        onError: {
            // when an exception is raised, this error handler will be called
            console.log('python error: ' + traceback);
        }

        onReceived: {
            // asychronous messages from Python arrive here
            // in Python, this can be accomplished via pyotherside.send()
            console.log('got message from python: ' + data);
        }
    }

    ConfigurationGroup {
        id: config
        path: "/apps/harbour-restic"

        property bool repo_initialized;
        property string backup_destination;
        property string ssh_key;
        property string exclude_rules;
        property string env_vars;
        property ConfigurationValue backup_include_paths: ConfigurationValue {
            key: config.path + "/backup_include_paths"
            defaultValue: [ { "path": "/home"},
                            { "path": "/usr"},
                            { "path": "/etc"},
                            { "path": "/root"}
                          ]
            onValueChanged: {
                python.setConfig("backup_include_paths", value);
            }
        }

        onBackup_destinationChanged: {
                python.setConfig("backup_destination", backup_destination);
        }

        onSsh_keyChanged: {
                python.setConfig("ssh_key", ssh_key);
        }

        onExclude_rulesChanged: {
                python.setConfig("exclude_rules", exclude_rules);
        }

        onEnv_varsChanged: {
                python.setConfig("env_vars", env_vars);
        }
    }
}
