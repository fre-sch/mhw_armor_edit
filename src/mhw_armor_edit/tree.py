# coding: utf-8
import logging
from collections import defaultdict

from PyQt5.QtCore import (Qt, QAbstractItemModel, QModelIndex,
                          QAbstractTableModel)
from PyQt5.QtGui import QFont

from mhw_armor_edit.assets import Definitions
from mhw_armor_edit.ftypes.am_dat import AmDatEntry

log = logging.getLogger(__name__)


class TreeModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        self.root_nodes = self._get_root_nodes()

    def _get_root_nodes(self):
        raise NotImplementedError()

    def index(self, row: int, column: int, parent: QModelIndex):
        # is this the hidden root index
        if not parent.isValid():
            return self.createIndex(row, column, self.root_nodes[row])
        parent_node = parent.internalPointer()
        return self.createIndex(row, column, parent_node.subnodes[row])

    def parent(self, index: QModelIndex):
        # is index the hidden root index
        if not index.isValid():
            return QModelIndex()
        # does it have parents
        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        return self.createIndex(node.parent.row, 0, node.parent)

    def reset(self):
        self.root_nodes = self._get_root_nodes()
        super().reset()

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.root_nodes)
        node = parent.internalPointer()
        return len(node.subnodes)


class TreeNode:
    def __init__(self, parent, row):
        self.parent = parent
        self.row = row
        self.subnodes = []


class ArmorSetNode(TreeNode):
    def __init__(self, ref, parent, row, children):
        super().__init__(parent, row)
        self.ref = ref
        self.subnodes = [
            ArmorEntryNode(elem, self, index)
            for index, elem in enumerate(children)
        ]

    @property
    def id(self):
        return self.ref[0]

    @property
    def name(self):
        return self.ref[1]


class ArmorEntryNode(TreeNode):
    def __init__(self, ref, parent, row):
        super().__init__(parent, row)
        self.ref = ref

    @property
    def id(self):
        return self.ref.index

    @property
    def name(self):
        return Definitions.lookup("equip_slot", self.ref.equip_slot)


class ArmorSetTreeModel(TreeModel):
    def __init__(self, entries):
        self.entries = entries
        self.columns = AmDatEntry.fields()
        super().__init__()

    def _get_root_nodes(self):
        groups = defaultdict(list)
        keys = list()
        for entry in self.entries:
            group_key = entry.set_id
            groups[group_key].append(entry)
            if group_key not in keys:
                keys.append(group_key)
        return [
            ArmorSetNode(
                (key, Definitions.lookup("set", key)),
                None, index, groups[key])
            for index, key in enumerate(keys)
        ]

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return node.name
            elif index.column() == 1:
                return node.id
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal \
                and role == Qt.DisplayRole:
            if section == 0:
                return "Name"
            if section == 1:
                return "ID"
        return None


class StructTableModel(QAbstractTableModel):
    def __init__(self, fields, entries):
        self.fields = fields
        self.entries = entries
        super().__init__()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.entries)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.fields)

    def data(self, qindex, role=None):
        if role == Qt.DisplayRole:
            entry = self.entries[qindex.row()]
            field = self.fields[qindex.column()]
            return getattr(entry, field)
        elif role == Qt.FontRole:
            font = QFont()
            font.setFamily("Consolas")
            return font
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        return None

    def setData(self, qindex, value, role=None):
        if role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            field = self.fields[qindex.column()]
            try:
                setattr(entry, field, int(value))
                self.dataChanged.emit(qindex, qindex)
            except Exception as e:
                log.exception("error setting value")

    def flags(self, qindex):
        return super().flags(qindex) | Qt.ItemIsEditable

    def headerData(self, section, orient, role=None):
        if orient == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.fields[section]
        elif orient == Qt.Vertical:
            if role == Qt.DisplayRole:
                return section
        return None
