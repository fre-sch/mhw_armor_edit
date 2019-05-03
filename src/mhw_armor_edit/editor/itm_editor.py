# coding: utf-8
import logging
from enum import IntEnum, auto

from PyQt5 import uic
from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, Qt)
from PyQt5.QtWidgets import (QHeaderView,
                             QDataWidgetMapper)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.itm import Itm
from mhw_armor_edit.import_export import ImportExportManager
from mhw_armor_edit.utils import get_t9n_item, get_t9n


log = logging.getLogger()
ItmEditorWidget, ItmEditorWidgetBase = uic.loadUiType(Assets.load_asset_file("item_editor.ui"))


class FlagAttr:
    def __init__(self, flag):
        self.flag = flag

    def __get__(self, that, owner):
        if that is None:
            return self
        return that.entry.flags & self.flag != 0

    def __set__(self, that, toggle):
        if toggle:
            that.entry.flags = that.entry.flags | self.flag
        else:
            that.entry.flags = that.entry.flags & ~self.flag


class Column(IntEnum):
    name = 0
    description = 1
    id = 2
    sub_type = 3
    type = 4
    rarity = 5
    carry_limit = 6
    order = 7
    icon_id = 8
    icon_color = 9
    sell_price = 10
    buy_price = 11
    flag_is_default_item = 12
    flag_is_quest_only = 13
    flag_unknown1 = 14
    flag_is_consumable = 15
    flag_is_appraisal = 16
    flag_unknown2 = 17
    flag_is_mega = 18
    flag_is_level_one = 19
    flag_is_level_two = 20
    flag_is_level_three = 21
    flag_is_glitter = 22
    flag_is_deliverable = 23
    flag_is_not_shown = 24


class ModelAdapter:
    flag_is_default_item = FlagAttr(2 ** 0)
    flag_is_quest_only = FlagAttr(2 ** 1)
    flag_unknown1 = FlagAttr(2 ** 2)
    flag_is_consumable = FlagAttr(2 ** 3)
    flag_is_appraisal = FlagAttr(2 ** 4)
    flag_unknown2 = FlagAttr(2 ** 5)
    flag_is_mega = FlagAttr(2 ** 6)
    flag_is_level_one = FlagAttr(2 ** 7)
    flag_is_level_two = FlagAttr(2 ** 8)
    flag_is_level_three = FlagAttr(2 ** 9)
    flag_is_glitter = FlagAttr(2 ** 10)
    flag_is_deliverable = FlagAttr(2 ** 11)
    flag_is_not_shown = FlagAttr(2 ** 12)

    def __init__(self, model, entry):
        self.model = model
        self.entry = entry
        self.description = get_t9n(self.model, "t9n", self.entry.id * 2 + 1)
        self.name = get_t9n_item(self.model, "t9n", self.entry.id)

    def __getitem__(self, index):
        attr = Column(index).name
        try:
            return getattr(self, attr)
        except AttributeError:
            return getattr(self.entry, attr)

    def __setitem__(self, index, value):
        attr = Column(index).name
        if hasattr(self, attr):
            setattr(self, attr, value)
        else:
            setattr(self.entry, attr, value)


class ItmTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.entries = []

    def columnCount(self, parent: QModelIndex=None, *args, **kwargs):
        return len(Column)

    def rowCount(self, parent: QModelIndex=None, *args, **kwargs):
        return len(self.entries)

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole:
            if orient == Qt.Horizontal:
                return Column(section).name

    def data(self, qindex: QModelIndex, role=None):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            column = qindex.column()
            adapt = ModelAdapter(self.model, entry)
            return adapt[column]
        elif role == Qt.UserRole:
            entry = self.entries[qindex.row()]
            return entry

    def setData(self, qindex: QModelIndex, value, role=None):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            entry = self.entries[qindex.row()]
            try:
                value = int(value)
                return self.set_entry_value(entry, value, qindex)
            except (TypeError, ValueError):
                return False
        return False

    def set_entry_value(self, entry, value, qindex):
        adapt = ModelAdapter(self.model, entry)
        try:
            adapt[qindex.column()] = value
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
        self.import_export_manager = ImportExportManager(
            self.item_browser, ItmPlugin.import_export.get("safe_attrs"))
        self.import_export_manager.connect_custom_context_menu()
        self.mapper.addMapping(self.name_value, Column.name, b"text")
        self.mapper.addMapping(self.id_value, Column.id, b"text")
        self.mapper.addMapping(self.description_value, Column.description, b"text")
        self.mapper.addMapping(self.subtype_value, Column.sub_type, b"currentIndex")
        self.mapper.addMapping(self.type_value, Column.type, b"currentIndex")
        self.mapper.addMapping(self.rarity_value, Column.rarity)
        self.mapper.addMapping(self.carry_limit_value, Column.carry_limit)
        self.mapper.addMapping(self.sort_order_value, Column.order)
        self.mapper.addMapping(self.icon_id_value, Column.icon_id)
        self.mapper.addMapping(self.icon_color_value, Column.icon_color)
        self.mapper.addMapping(self.sell_price_value, Column.sell_price)
        self.mapper.addMapping(self.buy_price_value, Column.buy_price)
        self.add_flag_mapping(self.flag_is_default_item, Column.flag_is_default_item)
        self.add_flag_mapping(self.flag_is_quest_only, Column.flag_is_quest_only)
        self.add_flag_mapping(self.flag_unknown1, Column.flag_unknown1)
        self.add_flag_mapping(self.flag_is_consumable, Column.flag_is_consumable)
        self.add_flag_mapping(self.flag_is_appraisal, Column.flag_is_appraisal)
        self.add_flag_mapping(self.flag_unknown2, Column.flag_unknown2)
        self.add_flag_mapping(self.flag_is_mega, Column.flag_is_mega)
        self.add_flag_mapping(self.flag_is_level_one, Column.flag_is_level_one)
        self.add_flag_mapping(self.flag_is_level_two, Column.flag_is_level_two)
        self.add_flag_mapping(self.flag_is_level_three, Column.flag_is_level_three)
        self.add_flag_mapping(self.flag_is_glitter, Column.flag_is_glitter)
        self.add_flag_mapping(self.flag_is_deliverable, Column.flag_is_deliverable)
        self.add_flag_mapping(self.flag_is_not_shown, Column.flag_is_not_shown)

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
