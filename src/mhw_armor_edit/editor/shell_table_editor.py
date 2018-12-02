# coding: utf-8
import logging

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QTreeView, QVBoxLayout,
                             QPushButton, QSpinBox,
                             QHBoxLayout, QLabel, QStyle)

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.sh_tbl import ShlTbl
from mhw_armor_edit.tree import TreeModel, TreeNode

log = logging.getLogger(__name__)
DOC_CAPACITY = """<h3>Capacity Notes</h3>
<p>Capacity higher than 10 can crash the game,<br>
especially when used with Free Element/Ammo up skill.</p>
"""
DOC_RECOIL = """<h3>Recoil Presets</h3>
<table border="1" cellpadding="3" cellspacing="1">
<thead>
<tr> <th>Value</th> <th>Effect</th> </tr>
</thead>
<tbody>
<tr> <td>00</td> <td>Normal (Recoil +1)</td> </tr>
<tr> <td>01, 02, 03</td> <td>Normal (Recoil +2)</td> </tr>
<tr> <td>4, 5, 7, 11, 20, 21, 24, 32</td> <td>Normal (Recoil +3)</td> </tr>
<tr> <td>6, 8, 9, 12, 13, 19, 25</td> <td>Normal (Recoil +4)</td> </tr>
<tr> <td>28, 29, 30</td> <td>Rapid Fire (Recoil +2)</td> </tr>
<tr> <td>31, 33</td> <td>Rapid Fire (Recoil +3)</td> </tr>
<tr> <td>18</td> <td>Follow-Up / Mortar (Recoil +1)</td> </tr>
<tr> <td>14, 27</td> <td>Follow-Up / Mortar (Recoil +2)</td> </tr>
<tr> <td>15, 16, 22, 23, 26</td> <td>Follow-Up / Mortar (Recoil +3)</td> </tr>
<tr> <td>10</td> <td>Blot Action / Single Shot / Auto-Reload</td> </tr>
<tr> <td>17</td> <td>Wyvern Shot Charge</td> </tr>
</tbody>
</table>
"""
DOC_RELOAD = """<h3>Reload Presets</h3>
<table border="1" cellpadding="3" cellspacing="1">
<thead>
<tr> <th>Value</th> <th>Effect</th> </tr>
</thead>
<tbody>
<tr> <td>17</td> <td>Fast</td> </tr>
<tr> <td>0, 1, 14, 18</td> <td>Normal</td> </tr>
<tr> <td>2, 3, 4, 5, 11, 15, 16</td> <td>Slow</td> </tr>
<tr> <td>6, 7, 8, 9, 10, 12, 13</td> <td>Very Slow</td> </tr>
</tbody>
</table>
"""

class ShellTableTreeModel(TreeModel):
    columns = ("Type", "Capacity", "Recoil", "Reload")

    def __init__(self, parent=None):
        self.entries = []
        super().__init__(parent)
        self.column_font = QFont()
        self.column_font.setFamily("Consolas")

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.columns)

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole:
            if orient == Qt.Horizontal:
                return self.columns[section]

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return node.name
            elif index.column() == 1:
                return node.capacity
            elif index.column() == 2:
                return node.recoil
            elif index.column() == 3:
                return node.reload
        elif role == Qt.FontRole:
            if index.column() in (1, 2, 3):
                return self.column_font
        return None

    def setData(self, index, value, role=None):
        if not index.isValid():
            return False
        node = index.internalPointer()
        try:
            value = int(value)
        except (ValueError, TypeError):
            return False
        if role == Qt.EditRole:
            if index.column() == 1:
                node.capacity = value
                self.dataChanged.emit(index, index)
                return True
            elif index.column() == 2:
                node.recoil = value
                self.dataChanged.emit(index, index)
                return True
            elif index.column() == 3:
                node.reload = value
                return True
                self.dataChanged.emit(index, index)
        return False

    def flags(self, index):
        if not index.isValid():
            return super().flags(index)
        node = index.internalPointer()
        if isinstance(node, ShellTreeEntryNode) and index.column() in (1, 2, 3):
            return super().flags(index) | Qt.ItemIsEditable
        return super().flags(index)

    def _get_root_nodes(self):
        return [
            ShellTreeRootNode(entry, None, index)
            for index, entry in enumerate(self.entries)
        ]

    def update(self, entries):
        self.beginResetModel()
        self.entries = entries
        self.root_nodes = self._get_root_nodes()
        self.endResetModel()


class ShellTreeRootNode(TreeNode):
    GroupKeys = (
        ("normal", 3),
        ("pierce", 3),
        ("spread", 3),
        ("cluster", 3),
        ("wyvern", 1),
        ("sticky", 3),
        ("slicing", 1),
        ("flaming", 1),
        ("water", 1),
        ("freeze", 1),
        ("thunder", 1),
        ("dragon", 1),
        ("poison", 2),
        ("paralysis", 2),
        ("sleep", 2),
        ("exhaust", 2),
        ("recover", 2),
        ("demon", 1),
        ("armor", 1),
        ("unknown", 2),
        ("tranq", 1)
    )

    def __init__(self, ref, parent, row):
        super().__init__(parent, row)
        self.name = row
        self.capacity = None
        self.recoil = None
        self.reload = None
        self.subnodes = [
            ShellTreeGroupNode(group, ref, self, index)
            for index, group in enumerate(self.GroupKeys)
        ]


class ShellTreeGroupNode(TreeNode):
    def __init__(self, group, ref, parent, row):
        super().__init__(parent, row)
        attr, count = group
        self.name = attr.title()
        self.capacity = None
        self.recoil = None
        self.reload = None
        self.subnodes = [
            ShellTreeEntryNode(attr, index + 1, count, ref, self, index)
            for index in range(count)
        ]


class ShellTreeEntryNode(TreeNode):
    def __init__(self, attr, num, count, ref, parent, row):
        super().__init__(parent, row)
        self.ref = ref
        self.attr = attr if count == 1 else f"{attr}{num}"
        self.name = f"{attr} {num}".title()

    @property
    def capacity(self):
        return getattr(self.ref, f"{self.attr}_capacity")

    @capacity.setter
    def capacity(self, value):
        setattr(self.ref, f"{self.attr}_capacity", value)

    @property
    def recoil(self):
        return getattr(self.ref, f"{self.attr}_recoil")

    @recoil.setter
    def recoil(self, value):
        setattr(self.ref, f"{self.attr}_recoil", value)

    @property
    def reload(self):
        return getattr(self.ref, f"{self.attr}_reload")

    @reload.setter
    def reload(self, value):
        setattr(self.ref, f"{self.attr}_reload", value)


class ShellTableEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.shell_model = ShellTableTreeModel()
        self.tree_view = QTreeView(self)
        self.tree_view.setModel(self.shell_model)
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.init_navigation(), 0)
        layout.addWidget(self.tree_view, 1)
        layout.addWidget(self.init_docs(), 0)

    def get_icon(self, name):
        return self.style().standardIcon(name)

    def init_navigation(self):
        self.prev_button = QPushButton(self.get_icon(QStyle.SP_ArrowLeft), "")
        self.prev_button.setFlat(True)
        self.next_button = QPushButton(self.get_icon(QStyle.SP_ArrowRight), "")
        self.next_button.setFlat(True)
        self.prev_button.clicked.connect(self.handle_prev_button_clicked)
        self.next_button.clicked.connect(self.handle_next_button_clicked)
        self.current_index = QSpinBox()
        self.current_index.setMinimumWidth(60)
        self.current_index.valueChanged.connect(self.handle_current_index_changed)
        box = QWidget(self)
        box_layout = QHBoxLayout(box)
        box_layout.setContentsMargins(0, 0, 0, 0)
        box.setLayout(box_layout)
        box_layout.addWidget(self.prev_button, 0)
        box_layout.addWidget(self.next_button, 0)
        box_layout.addWidget(QLabel("Index:"), 0)
        box_layout.addWidget(self.current_index, 0)
        box_layout.addStretch(1)
        return box

    def init_docs(self):
        box = QWidget(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        box.setLayout(layout)
        layout.addWidget(QLabel(DOC_CAPACITY), 0, Qt.AlignTop)
        layout.addWidget(QLabel(DOC_RECOIL), 0, Qt.AlignTop)
        layout.addWidget(QLabel(DOC_RELOAD), 1, Qt.AlignTop)
        return box

    def handle_current_index_changed(self, value):
        try:
            index = int(value)
        except TypeError:
            log.exception("can't parse value as int: %r", value)
            return
        parent_index = QModelIndex()
        qindex = self.shell_model.index(self.current_index.value(), 0, parent_index)
        self.tree_view.setRootIndex(qindex)
        self.tree_view.expandAll()

    def handle_prev_button_clicked(self):
        self.current_index.setValue(self.current_index.value() - 1)

    def handle_next_button_clicked(self):
        self.current_index.setValue(self.current_index.value() + 1)

    def set_model(self, model):
        self.model = model
        if model is None:
            self.shell_model.update([])
            self.current_index.setMaximum(0)
        else:
            self.shell_model.update(self.model.data.entries)
            self.current_index.setMaximum(len(self.model.data.entries) - 1)
            self.handle_current_index_changed(0)
            self.tree_view.header().resizeSection(0, 120)


class ShlTblPlugin(EditorPlugin):
    pattern = "*.shl_tbl"
    data_factory = ShlTbl
    widget_factory = ShellTableEditor
    relations = {}
