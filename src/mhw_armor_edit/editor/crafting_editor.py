# coding: utf-8
import logging
from collections import defaultdict

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import (QWidget, QStackedLayout, QDataWidgetMapper,
                             QSpinBox, QGridLayout, QLabel, QComboBox)

from mhw_armor_edit.editor.models import ItmTranslationModel, EditorPlugin
from mhw_armor_edit.ftypes.eq_crt import EqCrtEntry, EqCrt
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.tree import TreeModel, TreeNode
from mhw_armor_edit.utils import ItemDelegate, get_t9n_item

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
        layout = QGridLayout(self)
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.model = None
        self.equip_type = None
        self._map_equip_id_to_index = {}
        self.item_model = StructTableModel(EqCrtEntry.fields(), self)
        self.item_mapper = QDataWidgetMapper(self)
        self.item_mapper.setItemDelegate(ItemDelegate())
        self.item_mapper.setModel(self.item_model)
        self.t9n_item_model = ItmTranslationModel(self)
        self.add_row(0, "Item", "Quantity")
        self.add_row_edit(1, EqCrtEntry.item1_id.index, EqCrtEntry.item1_qty.index)
        self.add_row_edit(2, EqCrtEntry.item2_id.index, EqCrtEntry.item2_qty.index)
        self.add_row_edit(3, EqCrtEntry.item3_id.index, EqCrtEntry.item3_qty.index)
        self.add_row_edit(4, EqCrtEntry.item4_id.index, EqCrtEntry.item4_qty.index)
        self.layout().setRowStretch(4, 1)

    def set_current(self, equip_id):
        if equip_id in self._map_equip_id_to_index:
            self.setDisabled(False)
            index = self._map_equip_id_to_index[equip_id]
            self.item_mapper.setCurrentIndex(index)
        else:
            self.setDisabled(True)

    def add_row(self, row, value1, value2):
        self.layout().addWidget(QLabel(value1), row, 0, Qt.AlignTop)
        self.layout().addWidget(QLabel(value2), row, 1, Qt.AlignTop)

    def add_row_edit(self, row, mapping1, mapping2):
        id_editor = QComboBox(self)
        id_editor.setModel(self.t9n_item_model)
        id_editor.setEditable(True)
        qty_editor = QSpinBox(self)
        qty_editor.setMinimum(0)
        qty_editor.setMaximum(0xff)
        self.item_mapper.addMapping(id_editor, mapping1)
        self.item_mapper.addMapping(qty_editor, mapping2)
        self.layout().addWidget(id_editor, row, 0, Qt.AlignTop)
        self.layout().addWidget(qty_editor, row, 1, Qt.AlignTop)

    def set_model(self, model, equip_type):
        self.model = model
        self.equip_type = equip_type
        if model is None:
            return
        crafting_model = model.get_relation_data("crafting")
        t9n_item_model = model.get_relation_data("t9n_item")
        if crafting_model:
            self.item_model.update(crafting_model.entries)
            self._map_equip_id_to_index = {
                entry.equip_id: index
                for index, entry in enumerate(crafting_model.entries)
                if not equip_type or equip_type == entry.equip_type
            }
        if t9n_item_model:
            self.t9n_item_model.update(t9n_item_model)


class CraftingTableModel(StructTableModel):
    ItemIds = "key_item", "item1_id", "item2_id", "item3_id", "item4_id"

    def __init__(self, parent=None):
        super().__init__(EqCrtEntry.fields(), parent)
        self.model = None

    def get_field_value(self, entry, field):
        value = getattr(entry, field)
        if field in self.ItemIds:
            return get_t9n_item(self.model, "t9n_item", value)
        return value

    def update(self, model):
        self.model = model
        super().update([] if model is None else model.data.entries)


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
        self.model = model
        self.table_model.update(self.model)


class EqCrtPlugin(EditorPlugin):
    pattern = "*.eq_crt"
    data_factory = EqCrt
    widget_factory = CraftingTableEditor
    relations = {
        r"common\equip\armor.eq_crt": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        },
        r"common\equip\ot_equip.eq_crt": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        },
        r"common\equip\weapon.eq_crt": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        }
    }
