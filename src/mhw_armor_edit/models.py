# coding: utf-8
import logging
import os

from PyQt5.QtCore import (QObject, pyqtSignal)

from mhw_armor_edit.editor import FilePluginRegistry
from mhw_armor_edit.ftypes.gmd import Gmd

log = logging.getLogger()


class Translations:
    Tables = {
        "armor": r"common\text\steam\armor_eng.gmd",
        "armor_series": r"common\text\steam\armor_series_eng.gmd",
        "item": r"common\text\steam\item_eng.gmd",
        "skill": r"common\text\vfont\skill_eng.gmd",
        "skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
        "lbg": r"common\text\steam\lbg_eng.gmd",
    }

    def __init__(self):
        self.root_path = None
        self.tables = {}

    def abs_path(self, rel_path):
        try:
            path = os.path.join(self.root_path, rel_path)
            exists = os.path.exists(path)
            return path, exists
        except TypeError:
            return rel_path, False

    def load(self, root_path):
        self.root_path = root_path
        for key, rpath in self.Tables.items():
            self._load_table(key, rpath)

    def _load_table(self, key, rpath):
        abs_path, exists = self.abs_path(rpath)
        if not exists:
            log.debug("translation file %s not found", abs_path)
            return
        with open(abs_path, "rb") as fp:
            try:
                self.tables[key] = Gmd.load(fp)
                log.debug("translation file %s loaded", abs_path)
            except Exception as e:
                log.exception("failed loading translation file  %s", abs_path)

    def get(self, table_name, index):
        table = self.tables.get(table_name)
        if not table:
            return f"{table_name}{index}"
        return table.get_string(index, f"{table_name}{index}")

    def get_table(self, name):
        return self.tables.get(name)

    @classmethod
    def copy(cls, other):
        inst = cls()
        if other is None:
            return inst
        for key, model in other.tables.items():
            inst.tables[key] = model
        return inst


class WorkspaceFile(QObject):
    reloaded = pyqtSignal()

    def __init__(self, workspace, rel_path, model, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.rel_path = rel_path
        self.abs_path, _ = workspace.get_path(self.rel_path)
        self.model = model

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
    translationsLoaded = pyqtSignal()

    def __init__(self, name=None, file_icon=None, translations=None, parent=None):
        super().__init__(parent)
        self.name = name
        self.file_icon = file_icon
        self.root_path = None
        self.files = dict()
        self.translations = Translations.copy(translations)

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
        self.root_path = path
        while self.files:
            key, ws_file = self.files.popitem()
            self.fileClosed.emit(ws_file.abs_path, ws_file.rel_path)
        self.translations.load(self.root_path)
        self.translationsLoaded.emit()
        self.rootPathChanged.emit(self.root_path)

    def set_translations(self, translations):
        self.translations = Translations.copy(translations)
        self.translations.load(self.root_path)

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
            self.files[abs_path].model = ws_file.model
            ws_file.save()
            self.fileActivated.emit(ws_file.abs_path, ws_file.rel_path)
