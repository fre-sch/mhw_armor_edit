# coding: utf-8
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.ftypes.gmd import GmdItem
from mhw_armor_edit.struct_table import SortFilterTableView


class GmdTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.columns = GmdItem._fields

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.columns)

    def rowCount(self, parent=None, *args, **kwargs):
        if self.model:
            return len(self.model.items)
        return 0

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            try:
                return self.columns[section]
            except IndexError:
                return None

    def data(self, qindex: QModelIndex, role=None):
        if role == Qt.DisplayRole:
            item = self.model.items[qindex.row()]
            attr = self.columns[qindex.column()]
            return getattr(item, attr)

    def update(self, model):
        self.beginResetModel()
        self.model = model
        self.endResetModel()


class GmdTableEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = GmdTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.table_view.setWordWrap(True)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model["model"]
        self.table_model.update(self.model)
