# coding: utf-8
import json
import logging
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QFileDialog, QApplication, QMainWindow,
                             QPushButton, QWidget, QVBoxLayout, QListWidgetItem,
                             QDialog)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.ftypes.am_dat import AmDatEntry

log = logging.getLogger()
DialogWidget, DialogWidgetBase = \
    uic.loadUiType(Assets.load_asset_file("import_export.ui"))


class ImportDialog(DialogWidgetBase, DialogWidget):
    """
    Example:
    ```
    def handle_import_accepted(import_data):
        log.debug("import_accepted: %s", import_data)

    def handle_clicked():
        dialog = ImportDialog.start(window, AmDatEntry.fields(), AmDatEntry.fields())
        dialog.import_accepted.connect(handle_import_accepted)
        dialog.open()
    ```
    """
    import_accepted = pyqtSignal(object)

    def __init__(self, parent, data, attrs, default_attrs):
        super().__init__(parent)
        self.setupUi(self)
        self.data = data
        self.attrs = attrs
        self.default_attrs = default_attrs
        for attr in self.attrs:
            if attr not in self.data:
                continue
            it = QListWidgetItem()
            it.setText(attr)
            it.setData(Qt.UserRole, attr)
            it.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
            it.setCheckState(Qt.Checked if attr in self.default_attrs else Qt.Unchecked)
            self.attr_list.addItem(it)
        self.dialog_button_box.accepted.connect(self.accept)
        self.dialog_button_box.rejected.connect(self.reject)
        self.check_all_button.clicked.connect(self.handle_check_all_clicked)
        self.check_none_button.clicked.connect(self.handle_check_none_clicked)
        self.finished.connect(self.handle_finished)

    def handle_finished(self, result):
        log.debug("handle_finished")
        if result == QDialog.Accepted:
            import_data = {
                attr: self.data[attr]
                for attr in self.get_checked_attrs()
            }
            self.import_accepted.emit(import_data)

    def handle_check_all_clicked(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            it.setCheckState(Qt.Checked)

    def handle_check_none_clicked(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            it.setCheckState(Qt.Unchecked)

    def get_checked_attrs(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            if it.checkState() == Qt.Checked:
                yield it.data(Qt.UserRole)

    @classmethod
    def init(cls, parent, attrs, default_attrs):
        file_path, _ = QFileDialog.getOpenFileName(
            parent, "Import data file",
            filter="Data *.json;;All *.*", initialFilter="*.json")
        if not file_path:
            return None
        with open(file_path, "r", encoding="UTF-8") as fp:
            data = json.load(fp)
        return cls(parent, data, attrs, default_attrs)


class ExportDialog(DialogWidgetBase, DialogWidget):
    def __init__(self, parent, data, attrs, default_attrs):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Export data")
        self.data = data
        self.attrs = attrs
        self.default_attrs = default_attrs
        for attr in self.attrs:
            it = QListWidgetItem()
            it.setText(attr)
            it.setData(Qt.UserRole, attr)
            it.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            it.setCheckState(
                Qt.Checked if attr in self.default_attrs else Qt.Unchecked)
            self.attr_list.addItem(it)
        self.dialog_button_box.accepted.connect(self.handle_accept_button_clicked)
        self.dialog_button_box.rejected.connect(self.reject)
        self.check_all_button.clicked.connect(self.handle_check_all_clicked)
        self.check_none_button.clicked.connect(self.handle_check_none_clicked)

    def handle_accept_button_clicked(self):
        log.debug("handle_accept_button_clicked")

        export_path, _ = QFileDialog.getSaveFileName(
            self, "Export data file",
            filter="Data *.json", initialFilter="*.json")
        if not export_path:
            return self.reject()

        export_data = {
            attr: self.data[attr]
            for attr in self.get_checked_attrs()
            if attr in self.data
        }
        with open(export_path, "w", encoding="UTF-8") as fp:
            json.dump(export_data, fp, indent=2)
        self.accept()

    def handle_check_all_clicked(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            it.setCheckState(Qt.Checked)

    def handle_check_none_clicked(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            it.setCheckState(Qt.Unchecked)

    def get_checked_attrs(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            if it.checkState() == Qt.Checked:
                yield it.data(Qt.UserRole)

    @classmethod
    def init(cls, parent, data, attrs, default_attrs):
        return cls(parent, data, attrs, default_attrs)


class Foo:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Dialog test")

    def handle_import_accepted(import_data):
        log.debug("handle_import_accepted: %s", import_data)

    def handle_import_clicked():
        dialog = ImportDialog.init(window,
                                   AmDatEntry.fields(),
                                   AmDatEntry.fields())
        dialog.import_accepted.connect(handle_import_accepted)
        dialog.show()

    def handle_export_clicked():
        export_data = Foo(
            id=1,
            num_gem_slots=3,
            gem_slot1_lvl=3,
            gem_slot2_lvl=2,
            gem_slot3_lvl=1)
        dialog = ExportDialog.init(window,
                                   export_data,
                                   AmDatEntry.fields(),
                                   AmDatEntry.fields())
        dialog.open()

    import_button = QPushButton("Import data ...")
    import_button.clicked.connect(handle_import_clicked)

    export_button = QPushButton("Export data ...")
    export_button.clicked.connect(handle_export_clicked)

    box = QWidget()
    box.setLayout(QVBoxLayout())
    box.layout().addWidget(import_button)
    box.layout().addWidget(export_button)
    window.setCentralWidget(box)
    window.show()
    sys.exit(app.exec_())
