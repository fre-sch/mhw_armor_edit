# coding: utf-8
import logging

from PyQt5 import uic
from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, Qt)
from PyQt5.QtWidgets import (QWidget, QHeaderView,
                             QDataWidgetMapper)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.itm import ItmEntry, Itm
from mhw_armor_edit.utils import get_t9n

log = logging.getLogger()


class ItmTableModel(QAbstractTableModel):
    FlagOffset = 0x1000
    FlagOffsetEnd = 0x2000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = ("Name", ) + ItmEntry.fields()
        self.model = None
        self.entries = []

    def columnCount(self, parent: QModelIndex=None, *args, **kwargs):
        return len(self.columns)

    def rowCount(self, parent: QModelIndex=None, *args, **kwargs):
        return len(self.entries)

    def is_flag_column(self, column):
        return self.FlagOffset <= column < self.FlagOffsetEnd

    def index(self, row, column, parent=None, *args, **kwargs):
        if self.is_flag_column(column):
            return self.createIndex(row, column)
        return super().index(row, column, parent, *args, **kwargs)

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole:
            if orient == Qt.Horizontal:
                return self.columns[section]

    def data(self, qindex: QModelIndex, role=None):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            if qindex.column() == 0:
                return get_t9n(self.model, "t9n", entry.id * 2)
            elif qindex.column() < self.FlagOffset:
                attr = self.columns[qindex.column()]
                return getattr(entry, attr)
            elif self.is_flag_column(qindex.column()):
                flag = qindex.column() ^ self.FlagOffset
                return entry.flags & flag != 0

    def setData(self, qindex: QModelIndex, value, role=None):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            entry = self.entries[qindex.row()]
            if 1 < qindex.column() < self.FlagOffset:
                self.set_entry_value(entry, value, qindex)
            elif self.is_flag_column(qindex.column()):
                return self.set_entry_flag(entry, value, qindex)
        return False

    def set_entry_value(self, entry, value, qindex):
        attr = self.columns[qindex.column()]
        try:
            setattr(entry, attr, int(value))
            self.dataChanged.emit(qindex, qindex)
            return True
        except (ValueError, TypeError):
            return False

    def set_entry_flag(self, entry, checked, qindex):
        try:
            flag_value = qindex.column() ^ self.FlagOffset
            if checked:
                entry.flags = entry.flags | flag_value
            else:
                entry.flags = entry.flags & ~flag_value
            self.dataChanged.emit(qindex, qindex)
            return True
        except (ValueError, TypeError):
            return False

    def update(self, model):
        self.beginResetModel()
        self.model = model
        self.entries = model["model"].entries
        self.endResetModel()

    @classmethod
    def flag(cls, index):
        return cls.FlagOffset | 2**index


class ItmEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.itm_model = ItmTableModel(self)
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.itm_model)
        uic.loadUi(Assets.load_asset_file("item_editor.ui"), self)
        self.item_browser.setModel(self.itm_model)
        self.item_browser.activated.connect(self.mapper.setCurrentModelIndex)
        self.mapper.addMapping(self.name_value, 0, b"text")
        self.mapper.addMapping(self.id_value, ItmEntry.id.index + 1)
        self.mapper.addMapping(self.subtype_value, ItmEntry.sub_type.index + 1, b"currentIndex")
        self.mapper.addMapping(self.type_value, ItmEntry.type.index + 1, b"currentIndex")
        self.mapper.addMapping(self.rarity_value, ItmEntry.rarity.index + 1)
        self.mapper.addMapping(self.carry_limit_value, ItmEntry.carry_limit.index + 1)
        self.mapper.addMapping(self.sort_order_value, ItmEntry.order.index + 1)
        self.mapper.addMapping(self.icon_id_value, ItmEntry.icon_id.index + 1)
        self.mapper.addMapping(self.icon_color_value, ItmEntry.icon_color.index + 1)
        self.mapper.addMapping(self.sell_price_value, ItmEntry.sell_price.index + 1)
        self.mapper.addMapping(self.buy_price_value, ItmEntry.buy_price.index + 1)
        self.add_flag_mapping(self.flag_is_default_item, ItmTableModel.flag(0))
        self.add_flag_mapping(self.flag_is_quest_only, ItmTableModel.flag(1))
        self.add_flag_mapping(self.flag_unknown1, ItmTableModel.flag(2))
        self.add_flag_mapping(self.flag_is_consumable, ItmTableModel.flag(3))
        self.add_flag_mapping(self.flag_is_appraisal, ItmTableModel.flag(4))
        self.add_flag_mapping(self.flag_unknown2, ItmTableModel.flag(5))
        self.add_flag_mapping(self.flag_is_mega, ItmTableModel.flag(6))
        self.add_flag_mapping(self.flag_is_level_one, ItmTableModel.flag(7))
        self.add_flag_mapping(self.flag_is_level_two, ItmTableModel.flag(8))
        self.add_flag_mapping(self.flag_is_level_three, ItmTableModel.flag(9))
        self.add_flag_mapping(self.flag_is_glitter, ItmTableModel.flag(10))
        self.add_flag_mapping(self.flag_is_deliverable, ItmTableModel.flag(11))
        self.add_flag_mapping(self.flag_is_not_shown, ItmTableModel.flag(12))

    def add_flag_mapping(self, widget, flag_column):
        self.mapper.addMapping(widget, flag_column)
        widget.released.connect(self.mapper.submit)

    def set_model(self, model):
        self.model = model
        if model.get("model") is None:
            self.itm_model.update(None)
        else:
            self.itm_model.update(self.model)
            self.item_browser.header().setSectionResizeMode(
                0, QHeaderView.Stretch)
            self.item_browser.header().setSectionResizeMode(
                1, QHeaderView.ResizeToContents)
            self.item_browser.header().setStretchLastSection(False)
            for i in range(2, self.itm_model.columnCount(None)):
                self.item_browser.header().hideSection(i)


class ItmPlugin(EditorPlugin):
    pattern = "*.itm"
    data_factory = Itm
    widget_factory = ItmEditor
    relations = {
        r"common\item\itemData.itm": {
            "t9n": r"common\text\steam\item_eng.gmd",
        }
    }
