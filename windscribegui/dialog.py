# Built-in modules
import logging
from os.path import dirname

# Third-party modules
import windscribe
from qtpy.QtCore import QSettings
from qtpy.QtGui import QIcon, QStandardItem, QStandardItemModel
from qtpy.QtWidgets import QDialog, QMenu, QSystemTrayIcon, QTreeView
from qtpy.uic import loadUi


class Dialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        logging.info("Setting up Dialog UI")
        self.ui = loadUi(dirname(__file__) + "/dialog.ui", self)

        logging.info("Initializing QSettings")
        self.settings = QSettings("ShayBox", "WindscribeGUI")

        logging.info("Setting window icon")
        self.set_window_icon()

        logging.info("Populating locations")
        self.populate_locations()

        # logging.debug("Resizing widgets and window to minimum size")
        # self.adjustSize()
        # self.resize(self.minimumSize())

        logging.info("Initializing QSystemTrayIcon")
        self.init_tray()

        logging.info("Showing QSystemTrayIcon")
        self.tray.show()

    def set_window_icon(self) -> None:
        icon = self.settings.value("icon", "windscribe")
        icon = QIcon(icon) if isinstance(icon, QIcon) else QIcon.fromTheme(icon)
        if icon:
            self.setWindowIcon(icon)

    def populate_locations(self):
        # Populate locations from windscribe
        self.locationsModel = QStandardItemModel()
        for location in windscribe.locations():
            logging.info(f"Adding location {location}")
            label_item = QStandardItem(location.label)
            city_item = QStandardItem(location.city)
            geo_item = QStandardItem(location.geo)
            self.locationsModel.appendRow([label_item, city_item, geo_item])

        self.locationsView = QTreeView()
        self.locationsView.header().hide()
        self.locationsView.setRootIsDecorated(False)

        self.locationsBox.setView(self.locationsView)
        self.locationsBox.setModel(self.locationsModel)

        # Select the previously selected location
        location = self.settings.value("location", "")
        self.locationsBox.setCurrentText(location)

    def init_tray(self) -> None:
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        self.menu = QMenu()
        self.tray.activated.connect(self.show)
        self.menu.addAction("Show", self.show)
        self.menu.addSeparator()
        self.menu.addSection("Locations")

        def connect(location: str) -> None:
            self.locationsBox.setCurrentText(location)
            self.action_connect()

        for location in windscribe.locations():
            self.menu.addAction(location.label, lambda: connect(location.label))

        self.menu.addSeparator()
        self.menu.addAction("Quit", self.close)
        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip("WindscribeGUI")

    def closeEvent(self, event) -> None:
        event.ignore()
        self.reject()
        self.hide()

    def connect_buttons(self) -> None:
        self.connectButton.clicked.connect(self.action_connect)
        self.disconnectButton.clicked.connect(self.action_disconnect)

    def action_connect(self) -> None:
        logging.info(f"Connecting to {self.locationsBox.currentText()}")
        windscribe.connect(self.locationsBox.currentText())
        self.accept()

    def action_disconnect(self) -> None:
        logging.info("Disconnecting")
        windscribe.disconnect()
        self.accept()

    def accept(self) -> None:
        logging.info(f"Saving {self.locationsBox.currentText()}")
        self.settings.setValue("location", self.locationsBox.currentText())
        self.settings.sync()
        self.hide()

    def reject(self) -> None:
        self.hide()
