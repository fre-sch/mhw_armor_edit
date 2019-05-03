# coding: utf-8
import logging
import sys
from collections import Mapping, Set
from functools import wraps

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView

from mhw_armor_edit.utils import is_sequence

data = {
    "Gravity": {
        "DefaultGravity": 9.18,
        "DefaultSpeedRate": 21,
    },
    "StageAdjust": {
        "DefaultCapsuleOfs": {
            "x": 0, "y": 0, "z": 0
        },
        "DefaultCapsuleHeight": 0,
        "DefaultCapsuleRadius": 0
    },
    "Stamina": {
        "InitValue": 0,
        "AddOnValue": 0,
        "MinValue": 0,
        "TiredValue": 0,
        "AutoRecover": 0,
        "AutoMaxReduce": 0,
        "AutoMaxReduceTime": 0,
        "EscapeDashRate": 0,
        "NoBattleRate": 0,
        "ReduceRateLimit_Trg": 0,
        "ReduceRateLimit_Time": 0,
    },
    "tags": {
        "foo", "bar", "baz", "wusch"
    }
}


class TreeNode:
    class Unacceptable(Exception):
        pass

    ADAPTERS = []

    def __init__(self, key, value, parent=None, row=0):
        self.key = key
        self.value = self.init(value)
        self.parent = parent
        self.row = row

    @property
    def has_children(self):
        return is_sequence(self.value)

    def __len__(self):
        if self.has_children:
            return len(self.value)
        return 1

    def __getitem__(self, idx):
        if self.has_children:
            return self.value[idx]

    def init(self, value):
        for adapter in self.ADAPTERS:
            try:
                return adapter(self, value)
            except TreeNode.Unacceptable:
                continue
        return value

    def data(self, col):
        if col == 0:
            return self.key
        elif col == 1:
            return self.value

    @classmethod
    def adapter(cls, accept):
        def fn_collector(fn):
            @wraps(fn)
            def adapter_wrapper(parent, value):
                if not accept(value):
                    raise TreeNode.Unacceptable()
                return fn(cls, parent, value)
            cls.ADAPTERS.append(adapter_wrapper)
            return fn
        return fn_collector


@TreeNode.adapter(is_sequence)
def sequence_adapter(cls, parent, value):
    return [cls(i, value, parent, i)
            for i, value in enumerate(value)]


@TreeNode.adapter(lambda value: isinstance(value, Mapping))
def mapping_adapter(cls, parent, value):
    return [cls(key, value, parent, i)
            for i, (key, value) in enumerate(value.items())]


@TreeNode.adapter(lambda value: isinstance(value, Set))
def set_adapter(cls, parent, value):
    return [cls(i, value, parent, i)
            for i, value in enumerate(value)]


class TreeModel(QAbstractItemModel):
    COLUMN_HEADERS = ("Key", "Value")

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.root = TreeNode("__root__", data, None)

    def check_for_root(self, parent: QModelIndex):
        return self.root if not parent.isValid() else parent.internalPointer()

    def columnCount(self, parent: QModelIndex=None):
        return 2

    def headerData(self, section, orient, role=None):
        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            return self.COLUMN_HEADERS[section]

    def rowCount(self, parent: QModelIndex):
        node = self.check_for_root(parent)
        return len(node)

    def index(self, row, col, parent: QModelIndex):
        node = self.check_for_root(parent)
        child = node[row]
        return self.createIndex(row, col, child) if child else QModelIndex()

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()
        child = index.internalPointer()
        parent = child.parent
        if parent is self.root:
            return QModelIndex()
        return self.createIndex(parent.row, 0, parent)

    def hasChildren(self, parent: QModelIndex):
        node = self.check_for_root(parent)
        return node is not None and node.has_children

    def data(self, index: QModelIndex, role):
        if index.isValid() and role == Qt.DisplayRole:
            node = index.internalPointer()
            return node.data(index.column())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Treeview for nested dict/list")
        self.setGeometry(300, 300, 600, 800)
        tree_view = QTreeView()
        tree_view.setModel(TreeModel(data))
        self.setCentralWidget(tree_view)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s %(message)s")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
