# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
from enum import IntEnum

from PyQt5 import uic
from PyQt5.QtCore import (Qt, QModelIndex)
from PyQt5.QtWidgets import (QDataWidgetMapper, QHeaderView, QMenu)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor.models import (SkillTranslationModel,
                                          EditorPlugin)
from mhw_armor_edit.ftypes.am_dat import AmDatEntry, AmDat
from mhw_armor_edit.import_export import (ExportDialog, ImportDialog,
                                          ImportExportManager)
from mhw_armor_edit.tree import TreeModel, TreeNode
from mhw_armor_edit.utils import ItemDelegate, get_t9n, create_action

log = logging.getLogger()
ArmorEditorWidget, ArmorEditorWidgetBase = uic.loadUiType(
    Assets.load_asset_file("armor_editor.ui"))

Column = IntEnum("Column", [("name", 0), ] + [
    (field_name, getattr(AmDatEntry, field_name).index + 1)
    for field_name in AmDatEntry.fields()
])


class ArmorEditor(ArmorEditorWidgetBase, ArmorEditorWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.model = None
        self.parts_tree_model = ArmorSetTreeModel()
        self.skill_model = SkillTranslationModel()
        self.armor_item_mapper = QDataWidgetMapper(self)
        self.armor_item_mapper.setItemDelegate(ItemDelegate())
        self.armor_item_mapper.setModel(self.parts_tree_model)
        self.parts_tree_view.setModel(self.parts_tree_model)
        self.parts_tree_view.activated.connect(self.handle_parts_tree_activated)
        self.import_export_manager = ImportExportManager(self.parts_tree_view)
        self.import_export_manager.connect_custom_context_menu()
        for it in ("set_skill1_value", "set_skill2_value", "skill1_value",
                   "skill2_value", "skill3_value"):
            getattr(self, it).setModel(self.skill_model)
        mappings = [
            (self.id_value, Column.id, b"text"),
            (self.name_value, Column.gmd_name_index, b"text"),
            (self.description_value, Column.gmd_desc_index, b"text"),
            (self.setid_value, Column.set_id),
            (self.set_group_value, Column.set_group),
            (self.type_value, Column.type, b"currentIndex"),
            (self.order_value, Column.order),
            (self.variant_value, Column.variant, b"currentIndex"),
            (self.equip_slot_value, Column.equip_slot, b"currentIndex"),
            (self.gender_value, Column.gender, b"currentIndex"),
            (self.mdl_main_id_value, Column.mdl_main_id),
            (self.mdl_secondary_id_value, Column.mdl_secondary_id),
            (self.icon_color_value, Column.icon_color),
            (self.defense_value, Column.defense),
            (self.rarity_value, Column.rarity),
            (self.cost_value, Column.cost),
            (self.fire_res_value, Column.fire_res),
            (self.water_res_value, Column.water_res),
            (self.thunder_res_value, Column.thunder_res),
            (self.ice_res_value, Column.ice_res),
            (self.dragon_res_value, Column.dragon_res),
            (self.set_skill1_value, Column.set_skill1),
            (self.set_skill1_lvl_value, Column.set_skill1_lvl),
            (self.set_skill2_value, Column.set_skill2),
            (self.set_skill2_lvl_value, Column.set_skill2_lvl),
            (self.skill1_value, Column.skill1),
            (self.skill1_lvl_value, Column.skill1_lvl),
            (self.skill2_value, Column.skill2),
            (self.skill2_lvl_value, Column.skill2_lvl),
            (self.skill3_value, Column.skill3),
            (self.skill3_lvl_value, Column.skill3_lvl),
            (self.num_gem_slots, Column.num_gem_slots),
            (self.gem_slot1_lvl_value, Column.gem_slot1_lvl),
            (self.gem_slot2_lvl_value, Column.gem_slot2_lvl),
            (self.gem_slot3_lvl_value, Column.gem_slot3_lvl),
        ]
        for mapping in mappings:
            self.armor_item_mapper.addMapping(*mapping)

    def handle_parts_tree_activated(self, qindex: QModelIndex):
        if isinstance(qindex.internalPointer(), ArmorSetNode):
            return
        self.armor_item_mapper.setRootIndex(qindex.parent())
        self.armor_item_mapper.setCurrentModelIndex(qindex)
        entry = qindex.internalPointer().ref
        self.crafting_requirements_editor.set_current(entry.id)

    def set_model(self, model):
        self.model = model
        if self.model is None:
            self.parts_tree_model = None
            self.parts_tree_view.setModel(None)
            return

        self.skill_model.update(model.get_relation_data("t9n_skill_pt"))
        self.crafting_requirements_editor.set_model(model, None)
        self.parts_tree_model.update(model)
        self.configure_tree_view()

    def configure_tree_view(self):
        header = self.parts_tree_view.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)
        for i in range(2, self.parts_tree_model.columnCount(None)):
            header.hideSection(i)


class ArmorEntryNode(TreeNode):
    def __init__(self, ref, parent, row):
        super().__init__(parent, row)
        self.ref = ref

    @property
    def id(self):
        return self.ref.id

    @property
    def name(self):
        return self.ref.gmd_name_index


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
        return self.ref

    @property
    def name(self):
        return self.ref


class ArmorSetTreeModel(TreeModel):
    def __init__(self):
        self.model = None
        self.columns = ("name", *AmDatEntry.fields())
        super().__init__()

    def get_entries(self):
        if self.model is None:
            return []
        return self.model.data.entries

    def _get_root_nodes(self):
        groups = defaultdict(list)
        for entry in self.get_entries():
            group_key = entry.set_id
            groups[group_key].append(entry)
        return [
            ArmorSetNode(
                key,
                None, index, groups[key])
            for index, key in enumerate(sorted(groups.keys()))
        ]

    def columnCount(self, parent):
        return len(self.columns)

    def data(self, index: QModelIndex, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if isinstance(node, ArmorEntryNode):
                return self.get_entry_data(index, node)
            return self.get_setnode_data(index, node)
        elif role == Qt.UserRole:
            if isinstance(node, ArmorEntryNode):
                return node.ref
        return None

    def setData(self, qindex: QModelIndex, value, role=None):
        if not qindex.isValid():
            return False
        node = qindex.internalPointer()
        if isinstance(node, ArmorSetNode):
            return False
        if qindex.column() == 0:
            return False
        entry = node.ref
        field = self.columns[qindex.column()]
        try:
            setattr(entry, field, int(value))
            self.dataChanged.emit(qindex, qindex)
            return True
        except Exception as e:
            log.exception("error setting value")

    def get_setnode_data(self, index, node):
        if index.column() == 0:
            if node.name == 0:
                return "Charms"
            return get_t9n(self.model, "t9n_armor_series", node.name)
        elif index.column() == 1:
            return node.id

    def get_entry_data(self, qindex, node):
        entry = node.ref
        attr = self.columns[qindex.column()]
        if attr == "name":
            return get_t9n(self.model, "t9n_armor", entry.gmd_name_index)
        value = getattr(node.ref, attr)
        if attr in ("gmd_name_index", "gmd_desc_index"):
            return get_t9n(self.model, "t9n_armor", value)
        return value

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section].title()
        return None

    def update(self, model):
        self.beginResetModel()
        self.model = model
        self.root_nodes = self._get_root_nodes()
        self.endResetModel()


class AmDatPlugin(EditorPlugin):
    pattern = "*.am_dat"
    data_factory = AmDat
    widget_factory = ArmorEditor
    relations = {
        r"common\equip\armor.am_dat": {
            "crafting": r"common\equip\armor.eq_crt",
            "t9n_armor": r"common\text\steam\armor_eng.gmd",
            "t9n_armor_series": r"common\text\steam\armor_series_eng.gmd",
            "t9n_item": r"common\text\steam\item_eng.gmd",
            "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
        }
    }
