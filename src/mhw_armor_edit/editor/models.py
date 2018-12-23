# coding: utf-8
import logging
from enum import IntEnum
from fnmatch import fnmatch

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt

log = logging.getLogger()


class WeaponType(IntEnum):
    GreatSword = 0
    SwordShield = 1
    DualBlades = 2
    LongSword = 3
    Hammer = 4
    HuntingHorn = 5
    Lance = 6
    GunLance = 7
    SwitchAxe = 8
    ChargeBlade = 9
    InsectGlaive = 10
    Bow = 11
    HeavyBowgun = 12
    LightBowgun = 13


class SkillTranslationModel(QAbstractTableModel):
    def __init__(self, parent=None, filter_ids=None):
        super().__init__(parent)
        self.items = tuple()
        self.filter_ids = (0, *filter_ids) if filter_ids is not None else None

    def update(self, gmd):
        self.beginResetModel()
        if not gmd:
            self.items = []
        else:
            self.items = [
                (i // 3, f"{gmd.string_table[i]}({i//3})")
                for index, i in enumerate(range(0, len(gmd.string_table), 3))
                if self.filter_ids is None or index in self.filter_ids
            ]
            self.items[0] = (0, "---")
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, qindex: QModelIndex, role=None):
        if not qindex.isValid():
            return None
        entry = self.items[qindex.row()]
        if qindex.column() == 0:
            if role == Qt.EditRole or role == Qt.DisplayRole:
                return entry[1]
            elif role == Qt.UserRole:
                return entry[0]
        return None


class ItmTranslationModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = tuple()

    def update(self, gmd):
        self.beginResetModel()
        if not gmd:
            self.items = []
        else:
            self.items = [
                (i // 2, f"{gmd.string_table[i]}({i//2})")
                for i in range(0, len(gmd.string_table), 2)
            ]
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, qindex: QModelIndex, role=None):
        if not qindex.isValid():
            return None
        entry = self.items[qindex.row()]
        if qindex.column() == 0:
            if role == Qt.EditRole or role == Qt.DisplayRole:
                return entry[1]
            elif role == Qt.UserRole:
                return entry[0]
        return None


class EditorPlugin:
    pattern = None
    data_factory = None
    widget_factory = None
    relations = {}

    def __init_subclass__(subcls, **kwargs):
        super().__init_subclass__(**kwargs)
        FilePluginRegistry.plugins.append(subcls)
        FilePluginRegistry.relations.update(subcls.relations)


class ATTRS:
    """Marker for special attributes in relations"""
    pass


class FilePluginRegistry:
    plugins = []
    relations = {}
    lang = "eng"

    @classmethod
    def get_plugin(cls, path):
        for plugin in cls.plugins:
            if fnmatch(path, plugin.pattern):
                return plugin

    @classmethod
    def load_model(cls, ws_file, is_relation=False):
        plugin = cls.get_plugin(ws_file.abs_path)
        with open(ws_file.abs_path, "rb") as fp:
            data = plugin.data_factory.load(fp)
            ws_file.set_data(data)
        return ws_file

    @classmethod
    def load_relations(cls, ws_file, directories):
        relations = cls.relations.get(ws_file.rel_path)
        if not relations:
            return
        for key, value in relations.items():
            if key == ATTRS:
                ws_file.set_attrs(value)
                continue
            rel_ws_file = cls._load_relation(ws_file, directories, value)
            if rel_ws_file is not None:
                ws_file.add_relation(key, rel_ws_file)

    @classmethod
    def _load_relation(cls, parent, directories, relation_rpath):
        for directory in directories:
            if not directory.is_valid:
                continue
            relation_rpath = cls.handle_t9n_lang(relation_rpath)
            relation_path, exists = directory.get_child_path(relation_rpath)
            if exists:
                rel_ws_file = type(parent)(
                    directory,
                    relation_rpath,
                    parent=parent)
                return cls.load_model(rel_ws_file, True)

    @classmethod
    def handle_t9n_lang(cls, path):
        if cls.lang != "eng" and path.endswith("_eng.gmd"):
            return path.replace("_eng.gmd", f"_{cls.lang}.gmd")
        return path
