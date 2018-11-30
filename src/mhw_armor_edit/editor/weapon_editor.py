# coding: utf-8
import logging

from PyQt5 import uic
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import (QDataWidgetMapper,
                             QHeaderView)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor.models import EditorPlugin, SkillTranslationModel
from mhw_armor_edit.ftypes.wp_dat import WpDatEntry, WpDat
from mhw_armor_edit.kire_widget import KireGaugeModelEntryAdapter
from mhw_armor_edit.utils import get_t9n, ItemDelegate

log = logging.getLogger()
WeaponEditorWidget, WeaponEditorWidgetBase = uic.loadUiType(
    Assets.load_asset_file("weapon_editor.ui"))


class WpDatTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = WpDatEntry.fields()
        self.entries = []
        self.model = None

    def columnCount(self, parent:QModelIndex=None, *args, **kwargs):
        return len(self.columns)

    def rowCount(self, parent:QModelIndex=None, *args, **kwargs):
        return len(self.entries)

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole:
            if orient == Qt.Horizontal:
                return self.columns[section]

    def data(self, qindex:QModelIndex, role=None):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            attr = self.columns[qindex.column()]
            value = getattr(entry, attr)
            if attr in ("gmd_name_index", "gmd_description_index"):
                return get_t9n(self.model, "t9n", value)
            elif attr == "kire_id":
                kire_model = self.model.get_relation_data("kire")
                return kire_model.entries[value]
            return value

    def setData(self, qindex:QModelIndex, value, role=None):
        if role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            field = self.columns[qindex.column()]
            try:
                setattr(entry, field, int(value))
                self.dataChanged.emit(qindex, qindex)
                return True
            except Exception as e:
                log.exception("error setting value (%s %r)",
                              field, value)
        return False

    def update(self, model):
        self.beginResetModel()
        self.model = model
        self.entries = model.data.entries
        self.endResetModel()


class WpDatEditor(WeaponEditorWidgetBase, WeaponEditorWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.model = None
        self.skill_model = SkillTranslationModel(filter_ids=(160, 161, 162))
        self.table_model = WpDatTableModel(self)
        self.weapon_tree_view.activated.connect(self.handle_weapon_tree_view_activated)
        self.kire_widget.set_model(KireGaugeModelEntryAdapter())
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setItemDelegate(ItemDelegate())
        self.mapper.setModel(self.table_model)
        self.skill_id_value.setModel(self.skill_model)
        mappings = [
            (self.id_value, WpDatEntry.id.index, b"text"),
            (self.name_value, WpDatEntry.gmd_name_index.index, b"text"),
            (self.description_value, WpDatEntry.gmd_description_index.index, b"text"),
            (self.order_value, WpDatEntry.order.index),
            (self.tree_id_value, WpDatEntry.tree_id.index),
            (self.tree_position_value, WpDatEntry.tree_position.index),
            (self.is_fixed_upgrade_value, WpDatEntry.is_fixed_upgrade.index, b"checked"),
            (self.base_model_id_value, WpDatEntry.base_model_id.index),
            (self.part1_id_value, WpDatEntry.part1_id.index),
            (self.part2_id_value, WpDatEntry.part2_id.index),
            (self.color_value, WpDatEntry.color.index),
            (self.rarity_value, WpDatEntry.rarity.index),
            (self.cost_value, WpDatEntry.crafting_cost.index),
            (self.raw_damage_value, WpDatEntry.raw_damage.index),
            (self.affinity_value, WpDatEntry.affinity.index),
            (self.defense_value, WpDatEntry.defense.index),
            (self.handicraft_value, WpDatEntry.handicraft.index),
            (self.element_id_value, WpDatEntry.element_id.index, b"currentIndex"),
            (self.element_damage_value, WpDatEntry.element_damage.index),
            (self.hidden_element_id_value, WpDatEntry.hidden_element_id.index, b"currentIndex"),
            (self.hidden_element_damage_value, WpDatEntry.hidden_element_damage.index),
            (self.elderseal_value, WpDatEntry.elderseal.index, b"currentIndex"),
            (self.num_gem_slots, WpDatEntry.num_gem_slots.index),
            (self.gem_slot1_lvl_value, WpDatEntry.gem_slot1_lvl.index),
            (self.gem_slot2_lvl_value, WpDatEntry.gem_slot2_lvl.index),
            (self.gem_slot3_lvl_value, WpDatEntry.gem_slot3_lvl.index),
            (self.skill_id_value, WpDatEntry.skill_id.index),
            (self.wep1_id_value, WpDatEntry.wep1_id.index),
            (self.wep2_id_value, WpDatEntry.wep2_id.index),
            (self.kire_widget, WpDatEntry.kire_id.index),
        ]
        for mapping in mappings:
            self.mapper.addMapping(*mapping)

    def handle_weapon_tree_view_activated(self, qindex):
        self.mapper.setCurrentModelIndex(qindex)

    def set_model(self, model):
        self.model = model
        self.skill_model.update(model.get_relation_data("t9n_skill_pt"))
        self.table_model.update(self.model)
        self.weapon_tree_view.setModel(self.table_model)
        for index, col in enumerate(self.table_model.columns):
            self.weapon_tree_view.hideColumn(index)
        self.weapon_tree_view.showColumn(WpDatEntry.id.index)
        self.weapon_tree_view.showColumn(WpDatEntry.gmd_name_index.index)
        header = self.weapon_tree_view.header()
        header.setSectionResizeMode(
            WpDatEntry.gmd_name_index.index, QHeaderView.Stretch)
        header.setSectionResizeMode(
            WpDatEntry.id.index, QHeaderView.ResizeToContents)


_common_relations = {
    "kire": r"common\equip\kireaji.kire",
    "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
}


class WpDatPlugin(EditorPlugin):
    pattern = "*.wp_dat"
    data_factory = WpDat
    widget_factory = WpDatEditor
    relations = {
        r"common\equip\c_axe.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\c_axe_eng.gmd",
        },
        r"common\equip\g_lance.wp_dat": {
            **_common_relations,
            "wep_glan": r"common\equip\wep_glan.wep_glan",
            "t9n": r"common\text\steam\g_lance_eng.gmd",
        },
        r"common\equip\hammer.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\hammer_eng.gmd",
        },
        r"common\equip\l_sword.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\l_sword_eng.gmd",
        },
        r"common\equip\lance.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\lance_eng.gmd",
        },
        r"common\equip\rod.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\rod_eng.gmd",
        },
        r"common\equip\s_axe.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\s_axe_eng.gmd",
        },
        r"common\equip\sword.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\sword_eng.gmd",
        },
        r"common\equip\tachi.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\tachi_eng.gmd",
        },
        r"common\equip\w_sword.wp_dat": {
            **_common_relations,
            "t9n": r"common\text\steam\w_sword_eng.gmd",
        },
        r"common\equip\whistle.wp_dat": {
            **_common_relations,
            "wep_whistle": r"common\equip\wep_whistle.wep_wsl",
            "t9n": r"common\text\steam\whistle_eng.gmd",
        },
    }
