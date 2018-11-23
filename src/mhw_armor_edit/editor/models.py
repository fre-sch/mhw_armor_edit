# coding: utf-8
import logging
from fnmatch import fnmatch

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt

log = logging.getLogger()


class SkillTranslationModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = tuple()

    def update(self, gmd):
        self.beginResetModel()
        if not gmd:
            self.items = []
        else:
            self.items = [
                (i // 3, f"{gmd.string_table[i]}({i//3})")
                for i in range(0, len(gmd.string_table), 3)
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


class FilePluginRegistry:
    plugins = []
    relations = {}

    @classmethod
    def get_plugin(cls, path):
        for plugin in cls.plugins:
            if fnmatch(path, plugin.pattern):
                return plugin

    @classmethod
    def load_model(cls, path, rel_path, is_relation=False):
        plugin = cls.get_plugin(path)
        model = {"path": path, "rel_path": rel_path}
        with open(path, "rb") as fp:
            data_model = plugin.data_factory.load(fp)
        if is_relation:
            return data_model
        model["model"] = data_model
        return model

    @classmethod
    def load_relations(cls, model, directories):
        relations = cls.relations.get(model["rel_path"])
        if not relations:
            return
        for key, relation_rpath in relations.items():
            model[key] = cls._load_relation(directories, relation_rpath)


    @classmethod
    def _load_relation(cls, directories, relation_rpath):
        for directory in directories:
            if not directory.is_valid:
                continue

            relation_path, exists = directory.get_child_path(relation_rpath)
            if exists:
                return cls.load_model(relation_path, relation_rpath, True)
