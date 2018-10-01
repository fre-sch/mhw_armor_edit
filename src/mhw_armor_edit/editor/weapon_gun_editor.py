# coding: utf-8
import logging

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.ftypes.wp_dat_g import WpDatGEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView


log = logging.getLogger()


class WpDatGTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = WpDatGEntry.fields()
        self.entries = []
        self.translations = None

    def columnCount(self, parent:QModelIndex=None, *args, **kwargs):
        return len(self.columns)

    def rowCount(self, parent:QModelIndex=None, *args, **kwargs):
        return len(self.entries)

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole:
            if orient == Qt.Horizontal:
                return self.columns[section]

    def data(self, qindex:QModelIndex, role=None):
        if role == Qt.DisplayRole:
            entry = self.entries[qindex.row()]
            attr = self.columns[qindex.column()]
            value = getattr(entry, attr)
            if attr in ("gmd_name_index", "gmd_description_index"):
                return self.translations.get("lbg", value)
            return value
        elif role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            attr = self.columns[qindex.column()]
            return getattr(entry, attr)

    def setData(self, qindex:QModelIndex, value, role=None):
        if role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            field = self.columns[qindex.column()]
            try:
                setattr(entry, field, int(value))
                self.dataChanged.emit(qindex, qindex)
                return True
            except Exception as e:
                log.exception("error setting value")
        return False

    def flags(self, qindex):
        return super().flags(qindex) | Qt.ItemIsEditable

    def update(self, entries, translations):
        self.beginResetModel()
        self.entries = entries
        self.translations = translations
        self.endResetModel()


class WpDatGEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = WpDatGTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model["model"]
        if model is None:
            self.table_model.update([])
        else:
            self.table_model.update(self.model.entries, model["translations"])
            self.table_view.resizeColumnsToContents()
