# coding: utf-8
import logging

from PyQt5.QtCore import (QAbstractItemModel, QModelIndex)

log = logging.getLogger(__name__)


class TreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_nodes = self._get_root_nodes()

    def _get_root_nodes(self):
        raise NotImplementedError()

    def index(self, row: int, column: int, parent: QModelIndex):
        # is this the hidden root index
        if not parent.isValid():
            if len(self.root_nodes):
                return self.createIndex(row, column, self.root_nodes[row])
            return QModelIndex()
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


