# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from PyQt5 import uic
from PyQt5.QtCore import (Qt, QModelIndex, QAbstractTableModel)
from PyQt5.QtWidgets import (QWidget, QDataWidgetMapper, QHeaderView)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor.models import (SkillTranslationModel,
                                          ItmTranslationModel)
from mhw_armor_edit.ftypes.am_dat import AmDatEntry
from mhw_armor_edit.ftypes.eq_crt import EqCrtEntry
from mhw_armor_edit.struct_table import StructTableModel
from mhw_armor_edit.tree import TreeModel, TreeNode
from mhw_armor_edit.utils import ItemDelegate

log = logging.getLogger()


class ArmorPieceItemModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fields = AmDatEntry.fields()
        self.entry = None
        self.translations = None

    def update(self, entry, translations):
        self.beginResetModel()
        self.entry = entry
        self.translations = translations
        self.endResetModel()

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.fields)

    def rowCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, qindex: QModelIndex, role=None):
        if role == Qt.DisplayRole or Qt.EditRole:
            attr = self.fields[qindex.column()]
            value = getattr(self.entry, attr)
            if attr in ("gmd_name_index", "gmd_desc_index"):
                return self.translations.get("armor", value)
            return value

    def setData(self, qindex: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            try:
                attr = self.fields[qindex.column()]
                setattr(self.entry, attr, int(value))
                self.dataChanged.emit(qindex, qindex)
                return True
            except ValueError:
                log.debug("error setting attr")
        return False

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return self.fields[section]


class ArmorEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.translations = None
        self.parts_tree_model = None
        self.skill_model = SkillTranslationModel()
        self.armor_item_model = ArmorPieceItemModel()
        self.armor_item_mapper = QDataWidgetMapper(self)
        self.armor_item_mapper.setItemDelegate(ItemDelegate())
        self.armor_item_mapper.setModel(self.armor_item_model)
        self.crafting_item_model = StructTableModel(EqCrtEntry.fields(), [])
        self.crafting_item_mapper = QDataWidgetMapper(self)
        self.crafting_item_mapper.setItemDelegate(ItemDelegate())
        self.crafting_item_mapper.setModel(self.crafting_item_model)
        self.itm_t9n_model = ItmTranslationModel(self)
        uic.loadUi(Assets.load_asset_file("armor_editor.ui"), self)
        self.parts_tree_view.activated.connect(self.handle_parts_tree_activated)
        for it in ("set_skill1_value", "set_skill2_value", "skill1_value", "skill2_value", "skill3_value"):
            getattr(self, it).setModel(self.skill_model)
        mappings = [
            (self.id_value, AmDatEntry.index.index, b"text"),
            (self.setid_value, AmDatEntry.set_id.index, b"text"),
            (self.name_value, AmDatEntry.gmd_name_index.index, b"text"),
            (self.description_value, AmDatEntry.gmd_desc_index.index, b"text"),
            (self.variant_value, AmDatEntry.variant.index, b"text"),
            (self.equip_slot_value, AmDatEntry.equip_slot.index, b"text"),
            (self.defense_value, AmDatEntry.defense.index),
            (self.rarity_value, AmDatEntry.rarity.index),
            (self.cost_value, AmDatEntry.cost.index),
            (self.fire_res_value, AmDatEntry.fire_res.index),
            (self.water_res_value, AmDatEntry.water_res.index),
            (self.thunder_res_value, AmDatEntry.thunder_res.index),
            (self.ice_res_value, AmDatEntry.ice_res.index),
            (self.dragon_res_value, AmDatEntry.dragon_res.index),
            (self.set_skill1_value, AmDatEntry.set_skill1.index),
            (self.set_skill1_lvl_value, AmDatEntry.set_skill1_lvl.index),
            (self.set_skill2_value, AmDatEntry.set_skill2.index),
            (self.set_skill2_lvl_value, AmDatEntry.set_skill2_lvl.index),
            (self.skill1_value, AmDatEntry.skill1.index),
            (self.skill1_lvl_value, AmDatEntry.skill1_lvl.index),
            (self.skill2_value, AmDatEntry.skill2.index),
            (self.skill2_lvl_value, AmDatEntry.skill2_lvl.index),
            (self.skill3_value, AmDatEntry.skill3.index),
            (self.skill3_lvl_value, AmDatEntry.skill3_lvl.index),
            (self.num_gem_slots, AmDatEntry.num_gem_slots.index),
            (self.gem_slot1_lvl_value, AmDatEntry.gem_slot1_lvl.index),
            (self.gem_slot2_lvl_value, AmDatEntry.gem_slot2_lvl.index),
            (self.gem_slot3_lvl_value, AmDatEntry.gem_slot3_lvl.index),
        ]
        for mapping in mappings:
            self.armor_item_mapper.addMapping(*mapping)

        self.crft_item1_id_value.setModel(self.itm_t9n_model)
        self.crafting_item_mapper.addMapping(self.crft_item1_id_value, EqCrtEntry.item1_id.index)
        self.crafting_item_mapper.addMapping(self.crft_item1_qty_value, EqCrtEntry.item1_qty.index)
        self.crft_item2_id_value.setModel(self.itm_t9n_model)
        self.crafting_item_mapper.addMapping(self.crft_item2_id_value, EqCrtEntry.item2_id.index)
        self.crafting_item_mapper.addMapping(self.crft_item2_qty_value, EqCrtEntry.item2_qty.index)
        self.crft_item3_id_value.setModel(self.itm_t9n_model)
        self.crafting_item_mapper.addMapping(self.crft_item3_id_value, EqCrtEntry.item3_id.index)
        self.crafting_item_mapper.addMapping(self.crft_item3_qty_value, EqCrtEntry.item3_qty.index)
        self.crft_item4_id_value.setModel(self.itm_t9n_model)
        self.crafting_item_mapper.addMapping(self.crft_item4_id_value, EqCrtEntry.item4_id.index)
        self.crafting_item_mapper.addMapping(self.crft_item4_qty_value, EqCrtEntry.item4_qty.index)

    def handle_parts_tree_activated(self, qindex: QModelIndex):
        if isinstance(qindex.internalPointer(), ArmorSetNode):
            return
        entry = qindex.internalPointer().ref
        self.armor_item_model.update(entry, self.translations)
        self.armor_item_mapper.setCurrentIndex(0)
        index = self.crafting_item_model.index_of_first(equip_id=entry.index)
        if index is not None:
            self.crafting_item_mapper.setCurrentIndex(index)

    def set_model(self, model):
        self.model = model.get("model")
        self.translations = model.get("translations")

        if self.model is None:
            self.parts_tree_model = None
            self.parts_tree_view.setModel(None)
            return

        self.skill_model.update(self.translations.get_table("skill_pt"))
        self.crafting_item_model.update(model.get("crafting"))
        self.itm_t9n_model.update(self.translations.get_table("item"))
        self.parts_tree_model = ArmorSetTreeModel(self.model.entries, self.translations)
        self.parts_tree_view.setModel(self.parts_tree_model)
        self.parts_tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.parts_tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.parts_tree_view.header().setStretchLastSection(False)
        for i in range(2, self.parts_tree_model.columnCount(None)):
            self.parts_tree_view.header().hideSection(i)


class ArmorEntryNode(TreeNode):
    def __init__(self, ref, parent, row):
        super().__init__(parent, row)
        self.ref = ref

    @property
    def id(self):
        return self.ref.index

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
    def __init__(self, entries, translations):
        self.entries = entries
        self.columns = AmDatEntry.fields()
        self.translations = translations
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
                key,
                None, index, groups[key])
            for index, key in enumerate(keys)
        ]

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                key = "armor" if isinstance(node, ArmorEntryNode) else "armor_series"
                return self.translations.get(key, node.name)
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
