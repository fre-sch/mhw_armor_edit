# coding: utf-8
import csv
import json
import logging

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex, QObject, pyqtSlot
from PyQt5.QtWidgets import (QFileDialog, QListWidgetItem,
                             QDialog, QMenu)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.utils import create_action, is_sequence, yield_to_list

log = logging.getLogger()
DialogWidget, DialogWidgetBase = \
    uic.loadUiType(Assets.load_asset_file("import_export.ui"))


def sanitize(item, attrs):
    return {
        attr: item[attr]
        for attr in attrs
        if attr in item
    }


class CsvFilter:
    Label = "CSV *.csv"

    def import_data(self, fp, fields, as_list=False):
        reader = csv.DictReader(fp, fields)
        if as_list:
            return list(reader)
        # just the first one
        for row in reader:
            return row

    def export_data(self, fp, export_data, fields):
        if is_sequence(export_data):
            export_data = [sanitize(it, fields) for it in export_data]
        else:
            export_data = [sanitize(export_data, fields)]
        writer = csv.DictWriter(fp, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(export_data)


class JsonFilter:
    Label = "JSON *.json"

    def import_data(self, fp, fields, as_list=False):
        return json.load(fp)

    def export_data(self, fp, export_data, fields):
        if is_sequence(export_data):
            export_data = [sanitize(it, fields) for it in export_data]
        else:
            export_data = sanitize(export_data, fields)
        json.dump(export_data, fp, indent=2)


class Filters:
    registry = {
        JsonFilter.Label: JsonFilter,
        CsvFilter.Label: CsvFilter
    }

    @classmethod
    def list(cls):
        return ";;".join(cls.registry.keys())

    @classmethod
    def get(cls, spec):
        return cls.registry[spec]()

    @classmethod
    def first(cls):
        for key in cls.registry:
            return key


class DialogHelper:

    def get_attrs(self):
        return self.attrs

    def is_default_attr(self, attr):
        if self.default_attrs is None:
            return True
        return attr in self.default_attrs

    def dialog_helper_init(self):
        self.check_all_button.clicked.connect(self.handle_check_all_clicked)
        self.check_none_button.clicked.connect(self.handle_check_none_clicked)
        for attr in self.get_attrs():
            it = QListWidgetItem()
            it.setText(attr)
            it.setData(Qt.UserRole, attr)
            it.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            it.setCheckState(
                Qt.Checked if self.is_default_attr(attr) else Qt.Unchecked)
            self.attr_list.addItem(it)

    def handle_check_all_clicked(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            it.setCheckState(Qt.Checked)

    def handle_check_none_clicked(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            it.setCheckState(Qt.Unchecked)

    @yield_to_list
    def get_checked_attrs(self):
        for i in range(self.attr_list.count()):
            it = self.attr_list.item(i)
            if it.checkState() == Qt.Checked:
                yield it.data(Qt.UserRole)


class ImportDialog(DialogHelper, DialogWidgetBase, DialogWidget):
    import_accepted = pyqtSignal(object)

    def __init__(self, parent, data, attrs, default_attrs, as_list=False):
        super().__init__(parent)
        self.setupUi(self)
        self.data = data
        self.attrs = attrs
        self.default_attrs = default_attrs
        self.as_list = as_list
        self.dialog_helper_init()
        self.finished.connect(self.handle_finished)

    def handle_finished(self, result):
        if result == QDialog.Accepted:
            checked_attrs = self.get_checked_attrs()
            if self.as_list:
                data = [sanitize(it, checked_attrs) for it in self.data]
            else:
                data = sanitize(self.data, checked_attrs)
            self.import_accepted.emit(data)

    @classmethod
    def init(cls, parent, attrs, default_attrs, as_list=False):
        file_path, selected_filter = QFileDialog.getOpenFileName(
            parent, "Import data file",
            filter=Filters.list(),
            initialFilter=Filters.first())
        if not file_path:
            return None
        filter = Filters.get(selected_filter)
        _attrs = [*attrs]
        if default_attrs is not None:
            _attrs.extend(it for it in default_attrs if it not in _attrs)
        with open(file_path, "r", encoding="UTF-8") as fp:
            data = filter.import_data(fp, _attrs, as_list)
        return cls(parent, data, attrs, default_attrs, as_list)


class ExportDialog(DialogHelper, DialogWidgetBase, DialogWidget):
    def __init__(self, parent, data, attrs, default_attrs):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Export data")
        self.data = data
        self.attrs = attrs
        self.default_attrs = default_attrs
        self.dialog_helper_init()
        self.finished.connect(self.handle_finished)

    def handle_finished(self, result):
        if result != QDialog.Accepted:
            return
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export data file",
            filter=Filters.list(), initialFilter=Filters.first())
        if not file_path:
            return self.reject()
        filter = Filters.get(selected_filter)
        with open(file_path, "w", encoding="UTF-8") as fp:
            filter.export_data(fp, self.data, self.get_checked_attrs())

    @classmethod
    def init(cls, parent, data, attrs, default_attrs):
        return cls(parent, data, attrs, default_attrs)


class ImportExportManager(QObject):
    import_finished = pyqtSignal(int)
    export_finished = pyqtSignal(int)

    def __init__(self, target_widget, default_attrs=None):
        super().__init__(target_widget)
        self.target_widget = target_widget
        self.default_attrs = default_attrs
        self.export_action = create_action(None, "Export ...",
                                           self.handle_export_action)
        self.import_action = create_action(None, "Import ...",
                                           self.handle_import_action)
        self.model_index = QModelIndex()

    def populate_menu(self, menu):
        menu.addAction(self.export_action)
        menu.addAction(self.import_action)

    def connect_custom_context_menu(self):
        self.target_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.target_widget.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, point):
        self.model_index = self.target_widget.indexAt(point)
        model_data = self.get_model_data()
        if model_data is not None:
            context_menu = QMenu()
            self.populate_menu(context_menu)
            context_menu.exec(self.target_widget.mapToGlobal(point))

    def handle_export_action(self):
        if not self.model_index.isValid():
            return
        data = self.get_model_data()
        attrs = list(data.keys())
        dialog = ExportDialog.init(self.target_widget, data, attrs,
                                   self.default_attrs)
        dialog.finished.connect(self.export_finished.emit)
        dialog.open()

    def get_model_data(self):
        model = self.model_index.model()
        entry = model.data(self.model_index, Qt.UserRole)
        if entry:
            return entry.as_dict()

    def handle_import_action(self):
        if not self.model_index.isValid():
            return
        model = self.model_index.model()
        entry = model.data(self.model_index, Qt.UserRole)
        attrs = entry.fields()
        dialog = ImportDialog.init(self.target_widget, attrs,
                                   self.default_attrs)
        if dialog:
            dialog.import_accepted.connect(entry.update)
            dialog.finished.connect(self.import_finished.emit)
            dialog.open()
