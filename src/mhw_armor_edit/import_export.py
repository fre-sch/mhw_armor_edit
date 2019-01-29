# coding: utf-8
import json
import logging
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex, QObject
from PyQt5.QtWidgets import (QFileDialog, QApplication, QMainWindow,
                             QPushButton, QWidget, QVBoxLayout, QListWidgetItem,
                             QDialog, QMenu)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.ftypes.am_dat import AmDatEntry
from mhw_armor_edit.utils import create_action

log = logging.getLogger()
DialogWidget, DialogWidgetBase = \
    uic.loadUiType(Assets.load_asset_file("import_export.ui"))


class DialogHelper:

    def get_attrs(self):
        return self.attrs

    def dialog_helper_init(self):
        self.check_all_button.clicked.connect(self.handle_check_all_clicked)
        self.check_none_button.clicked.connect(self.handle_check_none_clicked)
        for attr in self.get_attrs():
            it = QListWidgetItem()
            it.setText(attr)
            it.setData(Qt.UserRole, attr)
            it.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            it.setCheckState(
                Qt.Checked if attr in self.default_attrs else Qt.Unchecked)
            self.attr_list.addItem(it)

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


class ImportDialog(DialogHelper, DialogWidgetBase, DialogWidget):
    import_accepted = pyqtSignal(object)

    def __init__(self, parent, data, attrs, default_attrs):
        super().__init__(parent)
        self.setupUi(self)
        self.data = data
        self.attrs = attrs
        self.default_attrs = default_attrs
        self.dialog_helper_init()
        self.dialog_button_box.accepted.connect(self.accept)
        self.dialog_button_box.rejected.connect(self.reject)
        self.finished.connect(self.handle_finished)

    def get_attrs(self):
        for attr in self.attrs:
            if attr in self.data:
                yield attr

    def handle_finished(self, result):
        log.debug("handle_finished")
        if result == QDialog.Accepted:
            import_data = {
                attr: self.data[attr]
                for attr in self.get_checked_attrs()
            }
            self.import_accepted.emit(import_data)

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


class ExportDialog(DialogHelper, DialogWidgetBase, DialogWidget):
    def __init__(self, parent, data, attrs, default_attrs):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Export data")
        self.data = data
        self.attrs = attrs
        self.default_attrs = default_attrs
        self.dialog_helper_init()
        self.dialog_button_box.accepted.connect(self.handle_accept_button_clicked)
        self.dialog_button_box.rejected.connect(self.reject)

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

    @classmethod
    def init(cls, parent, data, attrs, default_attrs):
        return cls(parent, data, attrs, default_attrs)


class ImportExportManager(QObject):
    import_finished = pyqtSignal(int)

    def __init__(self, target_widget):
        super().__init__(target_widget)
        self.target_widget = target_widget
        self.export_action = create_action(None, "Export ...",
                                           self.handle_export_action)
        self.import_action = create_action(None, "Import ...",
                                           self.handle_import_action)
        self.context_menu = QMenu()
        self.context_menu.addAction(self.export_action)
        self.context_menu.addAction(self.import_action)
        self.model_index = QModelIndex()

    def connect_custom_context_menu(self):
        self.target_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.target_widget.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, point):
        self.model_index = self.target_widget.indexAt(point)
        self.context_menu.exec(self.target_widget.mapToGlobal(point))

    def handle_export_action(self):
        if not self.model_index.isValid():
            return
        model = self.model_index.model()
        entry = model.data(self.model_index, Qt.UserRole)
        data = entry.as_dict()
        attrs = list(data.keys())
        dialog = ExportDialog.init(self.target_widget, data, attrs, attrs)
        dialog.open()

    def handle_import_action(self):
        if not self.model_index.isValid():
            return
        model = self.model_index.model()
        entry = model.data(self.model_index, Qt.UserRole)
        attrs = entry.fields()
        dialog = ImportDialog.init(self.target_widget, attrs, attrs)
        if dialog:
            dialog.import_accepted.connect(entry.update)
            dialog.finished.connect(self.import_finished.emit)
            dialog.open()


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
