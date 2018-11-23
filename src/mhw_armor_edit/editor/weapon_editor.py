# coding: utf-8
import logging

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.wp_dat import WpDatEntry, WpDat
from mhw_armor_edit.struct_table import SortFilterTableView
from mhw_armor_edit.utils import get_t9n

log = logging.getLogger()


class WpDatTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = WpDatEntry.fields()
        self.entries = []
        self.model = None

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
                return get_t9n(self.model, "t9n", value)
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

    def update(self, model):
        self.beginResetModel()
        self.model = model
        self.entries = model["model"].entries
        self.endResetModel()


class WpDatEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = WpDatTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(self.model)


class WpDatPlugin(EditorPlugin):
    pattern = "*.wp_dat"
    data_factory = WpDat
    widget_factory = WpDatEditor
    relations = {
        r"common\equip\c_axe.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\c_axe_eng.gmd",
        },
        r"common\equip\g_lance.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "wep_glan": r"common\equip\wep_glan.wep_glan",
            "t9n": r"common\text\steam\g_lance_eng.gmd",
        },
        r"common\equip\hammer.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\hammer_eng.gmd",
        },
        r"common\equip\l_sword.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\l_sword_eng.gmd",
        },
        r"common\equip\lance.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\lance_eng.gmd",
        },
        r"common\equip\rod.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\rod_eng.gmd",
        },
        r"common\equip\s_axe.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\s_axe_eng.gmd",
        },
        r"common\equip\sword.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\sword_eng.gmd",
        },
        r"common\equip\tachi.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\tachi_eng.gmd",
        },
        r"common\equip\w_sword.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "t9n": r"common\text\steam\w_sword_eng.gmd",
        },
        r"common\equip\whistle.wp_dat": {
            "kire": r"common\equip\kireaji.kire",
            "wep_whistle": r"common\equip\wep_whistle.wep_wsl",
            "t9n": r"common\text\steam\whistle_eng.gmd",
        },
    }
