# coding: utf-8
from collections import namedtuple
from fnmatch import fnmatch

from mhw_armor_edit.editor.armor_editor import ArmorEditor
from mhw_armor_edit.editor.bbtbl_editor import BbtblEditor
from mhw_armor_edit.editor.crafting_editor import CraftingTableEditor
from mhw_armor_edit.editor.gmd_editor import GmdTableEditor
from mhw_armor_edit.editor.itm_editor import ItmEditor
from mhw_armor_edit.editor.kire_editor import KireEditor
from mhw_armor_edit.editor.shell_table_editor import ShellTableEditor
from mhw_armor_edit.editor.weapon_gun_editor import WpDatGEditor
from mhw_armor_edit.editor.weapon_editor import WpDatEditor
from mhw_armor_edit.editor.wep_wsl_editor import WepWslEditor
from mhw_armor_edit.ftypes.am_dat import AmDat
from mhw_armor_edit.ftypes.bbtbl import Bbtbl
from mhw_armor_edit.ftypes.eq_crt import EqCrt
from mhw_armor_edit.ftypes.gmd import Gmd
from mhw_armor_edit.ftypes.itm import Itm
from mhw_armor_edit.ftypes.kire import Kire
from mhw_armor_edit.ftypes.sh_tbl import ShellTable
from mhw_armor_edit.ftypes.wp_dat_g import WpDatG
from mhw_armor_edit.ftypes.wp_dat import WpDat
from mhw_armor_edit.ftypes.wep_wsl import WepWsl

EditorPlugin = namedtuple("EditorPlugin", (
    "pattern",
    "data_factory",
    "widget_factory"
))


Relations = {
    r"common\equip\armor.am_dat": {
        "crafting": r"common\equip\armor.eq_crt",
    }
}


class FilePluginRegistry:
    registered = (
        EditorPlugin("*.am_dat", AmDat, ArmorEditor),
        EditorPlugin("*.shl_tbl", ShellTable, ShellTableEditor),
        EditorPlugin("*.eq_crt", EqCrt, CraftingTableEditor),
        EditorPlugin("*.gmd", Gmd, GmdTableEditor),
        EditorPlugin("*.itm", Itm, ItmEditor),
        EditorPlugin("*.wp_dat_g", WpDatG, WpDatGEditor),
        EditorPlugin("*.bbtbl", Bbtbl, BbtblEditor),
        EditorPlugin("*.kire", Kire, KireEditor),
        EditorPlugin("*.wp_dat", WpDat, WpDatEditor),
        EditorPlugin("*.wep_wsl", WepWsl, WepWslEditor),
    )

    @classmethod
    def get_plugin(cls, path):
        for plugin in cls.registered:
            if fnmatch(path, plugin.pattern):
                return plugin

    @classmethod
    def load_model(cls, workspace, path, rel_path, is_relation=False):
        plugin = cls.get_plugin(path)
        model = {"path": path, "rel_path": rel_path}
        with open(path, "rb") as fp:
            model["model"] = plugin.data_factory.load(fp)
        if not is_relation:
            model.update(cls._load_relations(rel_path, workspace))
        return model

    @classmethod
    def _load_relations(cls, rpath, workspace):
        rel_models = {}
        relations = Relations.get(rpath)
        if not relations:
            return rel_models
        for key, relation_rpath in relations.items():
            relation_path, exists = workspace.get_path(relation_rpath)
            if not exists:
                rel_models[key] = None
            else:
                rel_model = cls.load_model(
                    workspace, relation_path, relation_rpath, True)
                rel_models[key] = rel_model["model"]
        return rel_models
