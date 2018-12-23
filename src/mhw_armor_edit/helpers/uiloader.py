# coding: utf-8
import logging
import sys

from PyQt5 import uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyle

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor.kire_widget import KireGaugeModel
from mhw_armor_edit.utils import create_action


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UI Loader Helper")
        self.setGeometry(300, 300, 600, 800)
        self.reload_ui_action = create_action(
            self.get_icon(QStyle.SP_BrowserReload),
            "Reload UI",
            self.handle_reload_ui,
            None)
        self.kire_gauge_model = KireGaugeModel()
        self.init_toolbar()

    def init_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setFloatable(False)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.insertAction(None, self.reload_ui_action)

    def get_icon(self, name):
        return self.style().standardIcon(name)

    def handle_reload_ui(self):
        widget = uic.loadUi(Assets.load_asset_file("weapon_editor.ui"))
        widget.kire_widget.set_model(self.kire_gauge_model)
        self.setCentralWidget(widget)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s %(message)s")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
