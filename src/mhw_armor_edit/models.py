# coding: utf-8
import errno
import logging
import os
from collections import defaultdict, namedtuple

from PyQt5.QtCore import (QObject, pyqtSignal)

from mhw_armor_edit.editor import FilePluginRegistry
from mhw_armor_edit.ftypes.gmd import Gmd

log = logging.getLogger()
TranslationEntry = namedtuple("TranslationEntry", ("priority", "table"))


class Translations:
    Tables = {
        "armor": r"common\text\steam\armor_eng.gmd",
        "armor_series": r"common\text\steam\armor_series_eng.gmd",
        "item": r"common\text\steam\item_eng.gmd",
        "skill": r"common\text\vfont\skill_eng.gmd",
        "skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
        "lbg": r"common\text\steam\lbg_eng.gmd",
        "hbg": r"common\text\steam\hbg_eng.gmd",
        "bow": r"common\text\steam\bow_eng.gmd",
        "c_axe": r"common\text\steam\c_axe_eng.gmd",
        "g_lance": r"common\text\steam\g_lance_eng.gmd",
        "hammer": r"common\text\steam\hammer_eng.gmd",
        "l_sword": r"common\text\steam\l_sword_eng.gmd",
        "lance": r"common\text\steam\lance_eng.gmd",
        "rod": r"common\text\steam\rod_eng.gmd",
        "s_axe": r"common\text\steam\s_axe_eng.gmd",
        "sword": r"common\text\steam\sword_eng.gmd",
        "tachi": r"common\text\steam\tachi_eng.gmd",
        "w_sword": r"common\text\steam\w_sword_eng.gmd",
        "whistle": r"common\text\steam\whistle_eng.gmd",
    }

    def __init__(self):
        self.tables = defaultdict(list)

    def load(self, priority, root_path):
        for key, rpath in self.Tables.items():
            abs_path = os.path.join(root_path, rpath)
            abs_path = os.path.normpath(abs_path)
            self._load_table(priority, key, abs_path)

    def unload(self, priority):
        for key, tables in self.tables.items():
            self.tables[key] = [
                table for table in tables
                if table.priority != priority
            ]
            tables.sort()

    def _load_table(self, priority, key, abs_path):
        exists = os.path.exists(abs_path)
        if not exists:
            log.debug("translation file %s not found", abs_path)
            return
        with open(abs_path, "rb") as fp:
            try:
                table = Gmd.load(fp)
                self.add_table(key, priority, table)
                log.debug("translation file loaded: %s", abs_path)
            except Exception as e:
                log.exception("failed loading translation file  %s", abs_path)

    def add_table(self, key, priority, table):
        self.tables[key].append(TranslationEntry(priority, table))
        self.tables[key].sort()

    def get(self, table_name, index):
        try:
            table = self.get_table(table_name)
            return table.get_string(index, f"{table_name}{index}")
        except (IndexError, AttributeError) as e:
            log.exception("failed getting index:%s on table:%s",
                          index, table_name)
            return f"{table_name} {index} <missing t9n>"

    def get_table(self, name):
        try:
            return self.tables.get(name)[-1].table
        except (TypeError, IndexError, AttributeError):
            log.exception("failed getting table:%s", name)
            return None


class WorkspaceFile(QObject):
    reloaded = pyqtSignal()

    def __init__(self, workspace, rel_path, model, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.rel_path = rel_path
        self.abs_path, _ = workspace.get_path(self.rel_path)
        self.model = model

    def set_model(self, model):
        self.model = model
        self.reloaded.emit()

    def set_workspace(self, workspace):
        self.workspace = workspace
        self.abs_path, _ = workspace.get_path(self.rel_path)

    def reload(self):
        self.model = self.workspace.load_file_model(
            self.abs_path, self.rel_path)
        self.reloaded.emit()

    def close(self):
        self.workspace.close_file(self)

    def save(self):
        self.workspace.ensure_dirs(self.rel_path)
        with open(self.abs_path, "wb") as fp:
            self.model["model"].save(fp)

    def __repr__(self):
        return f"<WorkspaceFile {self.abs_path}>"

    def __hash__(self):
        return hash(self.workspace) ^ hash(self.abs_path)


class Workspace(QObject):
    rootPathChanged = pyqtSignal(str)
    fileOpened = pyqtSignal(str, str)
    fileActivated = pyqtSignal(str, str)
    fileClosed = pyqtSignal(str, str)
    fileLoadError = pyqtSignal(str, str, str)

    def __init__(self, name, file_icon, translations, priority, parent=None):
        super().__init__(parent)
        self.name = name
        self.file_icon = file_icon
        self.root_path = None
        self.files = dict()
        self.translations = translations
        self.priority = priority

    @property
    def is_valid(self):
        return self.root_path is not None

    def get_path(self, rel_path):
        path = os.path.join(self.root_path, rel_path)
        exists = os.path.exists(path)
        return path, exists

    def get_rel_path(self, abs_path):
        return os.path.relpath(abs_path, self.root_path)

    def set_root_path(self, path):
        self.translations.unload(self.priority)
        self.root_path = path
        while self.files:
            key, ws_file = self.files.popitem()
            self.fileClosed.emit(ws_file.abs_path, ws_file.rel_path)
        self.translations.load(self.priority, self.root_path)
        self.rootPathChanged.emit(self.root_path)

    def open_file(self, path):
        path = os.path.normpath(path)
        rel_path = self.get_rel_path(path)
        if path in self.files:
            self.fileActivated.emit(path, rel_path)
        else:
            try:
                model = self.load_file_model(path, rel_path)
                self.files[path] = WorkspaceFile(self, rel_path, model)
                self.fileOpened.emit(path, rel_path)
            except Exception as e:
                log.exception("error loading path: %s", path)
                self.fileLoadError.emit(path, rel_path, str(e))

    def load_file_model(self, path, rel_path):
        model = FilePluginRegistry.load_model(self, path, rel_path)
        model["translations"] = self.translations
        return model

    def close_file(self, ws_file):
        try:
            self.files.pop(ws_file.abs_path)
            self.fileClosed.emit(ws_file.abs_path, ws_file.rel_path)
        except (ValueError, KeyError):
            log.exception("error while closing file %s", ws_file)

    def transfer_file(self, ws_file):
        abs_path, exists = self.get_path(ws_file.rel_path)
        if abs_path not in self.files:
            ws_file.close()
            self.files[abs_path] = ws_file
            ws_file.set_workspace(self)
            ws_file.save()
            self.fileOpened.emit(ws_file.abs_path, ws_file.rel_path)
        else:
            self.files[abs_path].set_model(ws_file.model)
            self.files[abs_path].save()
            self.fileActivated.emit(ws_file.abs_path, ws_file.rel_path)

    def ensure_dirs(self, rel_path):
        abs_path, _ = self.get_path(rel_path)
        dir_path = os.path.dirname(abs_path)
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
