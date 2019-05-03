# coding: utf-8
import logging

from PyQt5 import uic
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtWidgets import (QDataWidgetMapper,
                             QHeaderView)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor.models import (EditorPlugin, ATTRS, WeaponType,
                                          SkillTranslationModel)
from mhw_armor_edit.editor.shell_table_editor import ShellTableTreeModel
from mhw_armor_edit.ftypes.bbtbl import BbtblEntry
from mhw_armor_edit.ftypes.wp_dat_g import WpDatGEntry, WpDatG
from mhw_armor_edit.import_export import ImportExportManager
from mhw_armor_edit.struct_table import StructTableModel
from mhw_armor_edit.utils import get_t9n, ItemDelegate

log = logging.getLogger()
WeaponGunEditorWidget, WeaponGunEditorWidgetBase = uic.loadUiType(
    Assets.load_asset_file("weapon_gun_editor.ui"))


class WpDatGTableModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(WpDatGEntry.fields(), parent)
        self.model = None

    def get_field_value(self, entry, field):
        value = getattr(entry, field)
        if field in ("gmd_name_index", "gmd_description_index"):
            return get_t9n(self.model, "t9n", value)
        return value

    def data(self, qindex, role=None):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return super().data(qindex, role)
        elif role == Qt.UserRole:
            entry = self.entries[qindex.row()]
            return entry
        return None

    def headerData(self, section, orient, role=None):
        if orient == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == WpDatGEntry.gmd_name_index.index:
                    return "Name"
                return self.fields[section].title()
        super().headerData(section, orient, role)

    def update(self, model):
        self.model = model
        entries = [] if model is None else model.data.entries
        super().update(entries)

    def flags(self, qindex):
        flags = super().flags(qindex)
        if qindex.column() in (WpDatGEntry.id.index,
                               WpDatGEntry.gmd_name_index.index,
                               WpDatGEntry.gmd_description_index):
            return flags & ~Qt.ItemIsEditable
        return flags


class BottleTableModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(BbtblEntry.fields(), parent)

    def update(self, model):
        if model:
            super().update(model.get_relation_data("bottle_table"))


class ShellTableModel(ShellTableTreeModel):
    def update(self, model):
        if model:
            super().update(model.get_relation_data("shell_table"))


class WpDatGEditor(WeaponGunEditorWidgetBase, WeaponGunEditorWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.model = None
        self.item_model = WpDatGTableModel(self)
        self.weapon_tree_view.setModel(self.item_model)
        self.shell_table_model = ShellTableModel()
        self.shell_table_view.setModel(self.shell_table_model)
        self.bottle_table_model = BottleTableModel(self)
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setItemDelegate(ItemDelegate())
        self.mapper.setModel(self.item_model)
        self.bottle_mapper = QDataWidgetMapper(self)
        self.bottle_mapper.setItemDelegate(ItemDelegate())
        self.bottle_mapper.setModel(self.bottle_table_model)
        self.weapon_tree_view.activated.connect(self.handle_weapon_tree_view_activated)
        self.skill_model = SkillTranslationModel()
        self.skill_id_value.setModel(self.skill_model)
        self.import_export_manager = ImportExportManager(
            self.weapon_tree_view, WpDatGPlugin.import_export.get("safe_attrs"))
        self.import_export_manager.connect_custom_context_menu()
        mappings = [
            (self.id_value, WpDatGEntry.id.index, b"text"),
            (self.name_value, WpDatGEntry.gmd_name_index.index, b"text"),
            (self.description_value, WpDatGEntry.gmd_description_index.index, b"text"),
            (self.order_value, WpDatGEntry.order.index),
            (self.tree_id_value, WpDatGEntry.tree_id.index),
            (self.tree_position_value, WpDatGEntry.tree_position.index),
            (self.is_fixed_upgrade_value, WpDatGEntry.is_fixed_upgrade.index, b"checked"),
            (self.base_model_id_value, WpDatGEntry.base_model_id.index),
            (self.part1_id_value, WpDatGEntry.part1_id.index),
            (self.part2_id_value, WpDatGEntry.part2_id.index),
            (self.color_value, WpDatGEntry.color.index),
            (self.muzzle_type_value, WpDatGEntry.muzzle_type.index, b"currentIndex"),
            (self.barrel_type_value, WpDatGEntry.barrel_type.index, b"currentIndex"),
            (self.magazine_type_value, WpDatGEntry.magazine_type.index, b"currentIndex"),
            (self.scope_type_value, WpDatGEntry.scope_type.index, b"currentIndex"),
            (self.rarity_value, WpDatGEntry.rarity.index),
            (self.cost_value, WpDatGEntry.crafting_cost.index),
            (self.raw_damage_value, WpDatGEntry.raw_damage.index),
            (self.affinity_value, WpDatGEntry.affinity.index),
            (self.defense_value, WpDatGEntry.defense.index),
            (self.deviation_value, WpDatGEntry.deviation.index, b"currentIndex"),
            (self.special_ammo_type_value, WpDatGEntry.special_ammo_type.index, b"currentIndex"),
            (self.element_id_value, WpDatGEntry.element_id.index, b"currentIndex"),
            (self.element_damage_value, WpDatGEntry.element_damage.index),
            (self.hidden_element_id_value, WpDatGEntry.hidden_element_id.index, b"currentIndex"),
            (self.hidden_element_damage_value, WpDatGEntry.hidden_element_damage.index),
            (self.elderseal_value, WpDatGEntry.elderseal.index, b"currentIndex"),
            (self.num_gem_slots, WpDatGEntry.num_gem_slots.index),
            (self.gem_slot1_lvl_value, WpDatGEntry.gem_slot1_lvl.index),
            (self.gem_slot2_lvl_value, WpDatGEntry.gem_slot2_lvl.index),
            (self.gem_slot3_lvl_value, WpDatGEntry.gem_slot3_lvl.index),
            (self.skill_id_value, WpDatGEntry.skill_id.index),
        ]
        for mapping in mappings:
            self.mapper.addMapping(*mapping)
        mappings = [
            (self.close_range_value, BbtblEntry.close_range.index, b"currentIndex"),
            (self.power_value, BbtblEntry.power.index, b"currentIndex"),
            (self.paralysis_value, BbtblEntry.paralysis.index, b"currentIndex"),
            (self.poison_value, BbtblEntry.poison.index, b"currentIndex"),
            (self.sleep_value, BbtblEntry.sleep.index, b"currentIndex"),
            (self.blast_value, BbtblEntry.blast.index, b"currentIndex"),
        ]
        for mapping in mappings:
            self.bottle_mapper.addMapping(*mapping)

    @property
    def is_bow_type(self):
        return self.model.attrs.get("equip_type") == WeaponType.Bow

    def handle_weapon_tree_view_activated(self, qindex: QModelIndex):
        self.mapper.setCurrentModelIndex(qindex)
        entry = self.item_model.entries[qindex.row()]
        self.tabs_weapon_details.setTabText(
            0, self.item_model.data(qindex, Qt.DisplayRole))
        self.crafting_requirements_editor.set_current(entry.id)
        if self.is_bow_type:
            index = self.bottle_table_model.index(entry.special_ammo_type, 0)
            self.bottle_mapper.setCurrentModelIndex(index)
        else:
            index = self.shell_table_model.index(entry.shell_table_id, 0, QModelIndex())
            self.shell_table_view.setRootIndex(index)
            self.shell_table_view.expandAll()

    def set_model(self, model):
        self.model = model
        self.item_model.update(model)
        self.skill_model.update(model.get_relation_data("t9n_skill_pt"))
        self.crafting_requirements_editor\
            .set_model(model, model.attrs.get("equip_type"))
        if self.is_bow_type:
            self.bottle_table_model.update(model)
            self.hide_tab(self.tab_shell_table)
            self.special_ammo_type_value.deleteLater()
            self.special_ammo_type_label.deleteLater()
        else:
            self.shell_table_model.update(model)
            self.hide_tab(self.tab_bottle_table)
        self.configure_tree_view()

    def configure_tree_view(self):
        for index, col in enumerate(self.item_model.fields):
            self.weapon_tree_view.hideColumn(index)
        self.weapon_tree_view.showColumn(WpDatGEntry.id.index)
        self.weapon_tree_view.showColumn(WpDatGEntry.gmd_name_index.index)
        header = self.weapon_tree_view.header()
        header.setSectionResizeMode(
            WpDatGEntry.gmd_name_index.index, QHeaderView.Stretch)
        header.setSectionResizeMode(
            WpDatGEntry.id.index, QHeaderView.ResizeToContents)

    def hide_tab(self, widget):
        index = self.tabs_weapon_details.indexOf(widget)
        self.tabs_weapon_details.removeTab(index)


class WpDatGPlugin(EditorPlugin):
    pattern = "*.wp_dat_g"
    data_factory = WpDatG
    widget_factory = WpDatGEditor
    relations = {
        r"common\equip\lbg.wp_dat_g": {
            "crafting": r"common\equip\weapon.eq_crt",
            "shell_table": r"common\equip\shell_table.shl_tbl",
            "t9n": r"common\text\steam\lbg_eng.gmd",
            "t9n_item": r"common\text\steam\item_eng.gmd",
            "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
            ATTRS: {
                "equip_type": WeaponType.LightBowgun,
            }
        },
        r"common\equip\hbg.wp_dat_g": {
            "crafting": r"common\equip\weapon.eq_crt",
            "shell_table": r"common\equip\shell_table.shl_tbl",
            "t9n": r"common\text\steam\hbg_eng.gmd",
            "t9n_item": r"common\text\steam\item_eng.gmd",
            "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
            ATTRS: {
                "equip_type": WeaponType.HeavyBowgun,
            }
        },
        r"common\equip\bow.wp_dat_g": {
            "crafting": r"common\equip\weapon.eq_crt",
            "bottle_table": r"common\equip\bottle_table.bbtbl",
            "t9n": r"common\text\steam\bow_eng.gmd",
            "t9n_item": r"common\text\steam\item_eng.gmd",
            "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
            ATTRS: {
                "equip_type": WeaponType.Bow,
            }
        },
    }
    import_export = {
        "safe_attrs": [
            "base_model_id", "part1_id", "part2_id", "color", "is_fixed_upgrade",
            "muzzle_type", "barrel_type", "magazine_type", "scope_type",
            "crafting_cost", "rarity", "raw_damage", "defense", "affinity",
            "element_id", "element_damage", "hidden_element_id",
            "hidden_element_damage", "elderseal", "shell_table_id", "deviation",
            "num_gem_slots", "gem_slot1_lvl", "gem_slot2_lvl", "gem_slot3_lvl",
            "special_ammo_type", "skill_id", "unk6",
        ]
    }
