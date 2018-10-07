# coding: utf-8
import logging

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt

log = logging.getLogger()


class SkillTranslationModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = tuple()

    def update(self, gmd):
        self.beginResetModel()
        if not gmd:
            self.items = []
        else:
            self.items = [
                (i // 3, f"{gmd.string_table[i]}({i//3})")
                for i in range(0, len(gmd.string_table), 3)
            ]
            self.items[0] = (0, "---")
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, qindex: QModelIndex, role=None):
        if not qindex.isValid():
            return None
        entry = self.items[qindex.row()]
        if qindex.column() == 0:
            if role == Qt.EditRole or role == Qt.DisplayRole:
                return entry[1]
            elif role == Qt.UserRole:
                return entry[0]
        return None


class ItmTranslationModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = tuple()

    def update(self, gmd):
        self.beginResetModel()
        if not gmd:
            self.items = []
        else:
            self.items = [
                (i // 2, f"{gmd.string_table[i]}({i//2})")
                for i in range(0, len(gmd.string_table), 2)
            ]
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, qindex: QModelIndex, role=None):
        if not qindex.isValid():
            return None
        entry = self.items[qindex.row()]
        if qindex.column() == 0:
            if role == Qt.EditRole or role == Qt.DisplayRole:
                return entry[1]
            elif role == Qt.UserRole:
                return entry[0]
        return None
