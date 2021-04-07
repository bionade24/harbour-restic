# NOTICE:
#
# Application name defined in TARGET has a corresponding QML filename.
# If name defined in TARGET is changed, the following needs to be done
# to match new name:
#   - corresponding QML filename must be changed
#   - desktop icon filename must be changed
#   - desktop filename must be changed
#   - icon definition filename in desktop file must be changed
#   - translation filenames have to be changed

# The name of your application
TARGET = harbour-restic

CONFIG += sailfishapp_qml

DEPLOY_PATH = /usr/share/$${TARGET}

python.files = python/
python.files += python/restic
python.path = $${DEPLOY_PATH}/

INSTALLS += python

DISTFILES += qml/harbour-restic.qml \
    qml/cover/CoverPage.qml \
    qml/components/BackupPathItem.qml \
    qml/pages/BackupIncludePathsPage.qml \
    qml/pages/ConfigPage.qml \
    qml/pages/Main.qml \
    qml/pages/TextDialog.qml \
    rpm/harbour-restic.changes.in \
    rpm/harbour-restic.changes.run.in \
    rpm/harbour-restic.spec \
    rpm/harbour-restic.yaml \
    translations/*.ts \
    harbour-restic.desktop

SAILFISHAPP_ICONS = 86x86 108x108 128x128 172x172

# to disable building translations every time, comment out the
# following CONFIG line
CONFIG += sailfishapp_i18n

# German translation is enabled as an example. If you aren't
# planning to localize your app, remember to comment out the
# following TRANSLATIONS line. And also do not forget to
# modify the localized app name in the the .desktop file.
TRANSLATIONS += translations/harbour-restic-de.ts
