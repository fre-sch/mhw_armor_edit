# coding: utf-8
import logging
from collections import defaultdict

from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel
from PyQt5.QtWidgets import (QWidget, QTableView,
                             QStackedLayout, QDataWidgetMapper,
                             QSpinBox, QGridLayout, QLabel)

from mhw_armor_edit.ftypes.eq_crt import EqCrtEntry, EqCrt
from mhw_armor_edit.tree import TreeModel, TreeNode
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView

log = logging.getLogger()


class CraftingRequirementGroupNode(TreeNode):
    def __init__(self, ref, parent, row, children):
        super().__init__(parent, row)
        self.ref = ref
        self.subnodes = [
            CraftingRequirementEntryNode(entry, prefix, self, i)
            for i, entry in enumerate(children)
            for prefix in ("item1", "item2", "item3", "item4")
        ]


class CraftingRequirementEntryNode(TreeNode):
    def __init__(self, ref, prefix, parent, row):
        super().__init__(parent, row)
        self.ref = ref
        self.prefix = prefix


class CraftingRequirementModel(TreeModel):
    def __init__(self, entries: EqCrt):
        self.entries = entries
        self.group_keys_ordered = []
        super().__init__()

    def index_for_group(self, group_key):
        try:
            group_index = self.group_keys_ordered.index(group_key)
            return self.createIndex(0, 0, self.root_nodes[group_index])
        except IndexError as e:
            return QModelIndex()

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def data(self, qindex: QModelIndex, role=None):
        if not qindex.isValid():
            return
        node = qindex.internalPointer()
        if isinstance(node, CraftingRequirementGroupNode):
            if role == Qt.DisplayRole:
                return str(node.ref[qindex.column()])
        else:
            if role == Qt.DisplayRole:
                if qindex.column() == 0:
                    attr = node.prefix + "_id"
                    return getattr(node.ref, attr)
                elif qindex.column() == 1:
                    attr = node.prefix + "_qty"
                    return getattr(node.ref, attr)

    def headerData(self, section, orient, role=None):
        if orient == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return ("Item-ID", "Quantity")[section]

    def _get_root_nodes(self):
        groups = defaultdict(list)
        self.group_keys_ordered = []
        for entry in self.entries:
            group_key = (entry.equip_type, entry.equip_id)
            groups[group_key].append(entry)
            if group_key not in self.group_keys_ordered:
                self.group_keys_ordered.append(group_key)
        return [
            CraftingRequirementGroupNode(
                (group_key, "", "", ""),
                None, index, groups[group_key])
            for index, group_key in enumerate(self.group_keys_ordered)
        ]


class CraftingRequirementsEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setLayout(QGridLayout(self))
        self.model = None
        self.item_model = StructTableModel(EqCrtEntry.fields(), [])
        self.data_mapper = QDataWidgetMapper(self)
        self.data_mapper.setModel(self.item_model)
        self.add_row(0, "Item-ID", "Quantity")
        self.add_row_edit(1, EqCrtEntry.item1_id.index, EqCrtEntry.item1_qty.index)
        self.add_row_edit(2, EqCrtEntry.item2_id.index, EqCrtEntry.item2_qty.index)
        self.add_row_edit(3, EqCrtEntry.item3_id.index, EqCrtEntry.item3_qty.index)
        self.add_row_edit(4, EqCrtEntry.item4_id.index, EqCrtEntry.item4_qty.index)
        self.layout().setRowStretch(4, 1)

    def add_row(self, row, value1, value2):
        self.layout().addWidget(QLabel(value1), row, 0, Qt.AlignTop)
        self.layout().addWidget(QLabel(value2), row, 1, Qt.AlignTop)

    def add_row_edit(self, row, mapping1, mapping2):
        id_box = QSpinBox(self)
        id_box.setMaximum(0xffff)
        qty_box = QSpinBox(self)
        qty_box.setMaximum(0xff)
        self.data_mapper.addMapping(id_box, mapping1)
        self.data_mapper.addMapping(qty_box, mapping2)
        self.layout().addWidget(id_box, row, 0, Qt.AlignTop)
        self.layout().addWidget(qty_box, row, 1, Qt.AlignTop)

    def find_by_equip_id(self, equip_id):
        for i, entry in enumerate(self.model.entries):
            if entry.equip_id == equip_id:
                return i, entry

    def set_index(self, index):
        index, entry = self.find_by_equip_id(index)
        self.data_mapper.setCurrentIndex(index)

    def set_model(self, model):
        self.model = model
        if model is None:
            return
        self.item_model.update(self.model["model"].entries)


class CraftingTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = EqCrtEntry.fields()
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
            if attr in ("key_item", "item1_id", "item2_id", "item3_id", "item4_id"):
                return self.translations.get("item", value * 2)
            return value

    def update(self, entries, translations):
        self.beginResetModel()
        self.entries = entries
        self.translations = translations
        self.endResetModel()


class CraftingTableEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = CraftingTableModel(self)
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
            self.table_view.resizeRowsToContents()
