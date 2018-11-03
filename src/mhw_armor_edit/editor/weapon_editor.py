# coding: utf-8
import logging

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.ftypes.wp_dat import WpDatEntry
from mhw_armor_edit.struct_table import SortFilterTableView

log = logging.getLogger()


class WpDatTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = WpDatEntry.fields()
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
                if self.translation_key:
                    return self.translations.get(self.translation_key, value)
            return value
        elif role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            attr = self.columns[qindex.column()]
            return getattr(entry, attr)
        elif role == Qt.FontRole:
            font = QFont()
            font.setFamily("Consolas")
            return font

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

    def update(self, entries, translations, translation_key):
        self.beginResetModel()
        self.translation_key = translation_key
        self.entries = entries
        self.translations = translations
        self.endResetModel()


def _get_transnlation_key(keys, rel_path):
    for key in keys:
        if key in rel_path:
            return key


class WpDatEditor(QWidget):
    translation_keys = ("c_axe", "g_lance", "hammer", "l_sword", "lance", "rod",
                        "s_axe", "w_sword", "sword", "tachi", "whistle")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = WpDatTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model["model"]
        if model is None:
            self.table_model.update([], None, None)
        else:
            translation_key = _get_transnlation_key(
                self.translation_keys, model["rel_path"])
            self.table_model.update(
                self.model.entries,
                model["translations"],
                translation_key
            )
