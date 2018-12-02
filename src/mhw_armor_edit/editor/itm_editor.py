# coding: utf-8
import logging
from enum import IntEnum

from PyQt5 import uic
from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, Qt)
from PyQt5.QtWidgets import (QHeaderView,
                             QDataWidgetMapper)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.itm import ItmEntry, Itm
from mhw_armor_edit.utils import get_t9n_item, get_t9n

log = logging.getLogger()


ItmEditorWidget, ItmEditorWidgetBase = uic.loadUiType(Assets.load_asset_file("item_editor.ui"))


class Column(IntEnum):
    name = 0
    description = 1
    id = ItmEntry.id.index + 2
    sub_type = ItmEntry.sub_type.index + 2
    type = ItmEntry.type.index + 2
    rarity = ItmEntry.rarity.index + 2
    carry_limit = ItmEntry.carry_limit.index + 2
    order = ItmEntry.order.index + 2
    icon_id = ItmEntry.icon_id.index + 2
    icon_color = ItmEntry.icon_color.index + 2
    sell_price = ItmEntry.sell_price.index + 2
    buy_price = ItmEntry.buy_price.index + 2


class ItmTableModel(QAbstractTableModel):
    FlagOffset = 0x1000
    FlagOffsetEnd = 0x2000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = [it.name for it in Column]
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
            if qindex.column() == Column.name:
                return get_t9n_item(self.model, "t9n", entry.id)
            elif qindex.column() == Column.description:
                return get_t9n(self.model, "t9n", entry.id * 2 + 1)
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
        if self.model is None:
            self.entries = []
        else:
            self.entries = model.data.entries
        self.endResetModel()

    @classmethod
    def flag(cls, index):
        return cls.FlagOffset | 2**index


class ItmEditor(ItmEditorWidgetBase, ItmEditorWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.model = None
        self.itm_model = ItmTableModel(self)
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.itm_model)
        self.item_browser.setModel(self.itm_model)
        self.item_browser.activated.connect(self.handle_item_browser_activated)
        self.mapper.addMapping(self.name_value, Column.name.value, b"text")
        self.mapper.addMapping(self.id_value, Column.id.value, b"text")
        self.mapper.addMapping(self.description_value, Column.description.value, b"text")
        self.mapper.addMapping(self.subtype_value, Column.sub_type.value, b"currentIndex")
        self.mapper.addMapping(self.type_value, Column.type.value, b"currentIndex")
        self.mapper.addMapping(self.rarity_value, Column.rarity.value)
        self.mapper.addMapping(self.carry_limit_value, Column.carry_limit.value)
        self.mapper.addMapping(self.sort_order_value, Column.order.value)
        self.mapper.addMapping(self.icon_id_value, Column.icon_id.value)
        self.mapper.addMapping(self.icon_color_value, Column.icon_color.value)
        self.mapper.addMapping(self.sell_price_value, Column.sell_price.value)
        self.mapper.addMapping(self.buy_price_value, Column.buy_price.value)
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

    def handle_item_browser_activated(self, qindex):
        source_qindex = qindex.model().mapToSource(qindex)
        self.mapper.setCurrentModelIndex(source_qindex)

    def add_flag_mapping(self, widget, flag_column):
        self.mapper.addMapping(widget, flag_column)
        widget.released.connect(self.mapper.submit)

    def set_model(self, model):
        self.model = model
        self.itm_model.update(model)
        if model is not None:
            header = self.item_browser.header()
            # header = self.item_browser.horizontalHeader()
            header.hideSection(Column.description)
            header.setSectionResizeMode(Column.name, QHeaderView.Stretch)
            header.setSectionResizeMode(Column.id, QHeaderView.Fixed)
            header.resizeSection(Column.id, 50)
            header.setStretchLastSection(False)
            for i in range(3, self.itm_model.columnCount(None)):
                header.hideSection(i)
            self.item_browser.sortByColumn(Column.id, Qt.AscendingOrder)


class ItmPlugin(EditorPlugin):
    pattern = "*.itm"
    data_factory = Itm
    widget_factory = ItmEditor
    relations = {
        r"common\item\itemData.itm": {
            "t9n": r"common\text\steam\item_eng.gmd",
        }
    }
