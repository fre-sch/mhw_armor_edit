# coding: utf-8
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import (QWidget, QStackedLayout)

from mhw_armor_edit.ftypes.itm import ItmEntry
from mhw_armor_edit.struct_table import SortFilterTableView, StructTableModel


class ItmTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = ItmEntry.fields()
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
            if attr == "id":
                return self.translations.get("item", value * 2)
            return value

    def update(self, entries, translations):
        self.beginResetModel()
        self.entries = entries
        self.translations = translations
        self.endResetModel()


class ItmTableEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = ItmTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model["model"]
        if model is None:
            self.table_model.update([], None)
        else:
            self.table_model.update(self.model.entries,
                                    model["translations"])
            self.table_view.resizeColumnsToContents()
