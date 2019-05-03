# coding: utf-8
import errno
import logging
import os

from PyQt5.QtCore import (QObject, pyqtSignal)

from mhw_armor_edit.editor.models import FilePluginRegistry

log = logging.getLogger()


class WorkspaceFile(QObject):
    modifiedChanged = pyqtSignal(bool)
    reloaded = pyqtSignal()

    def __init__(self, directory, rel_path, data=None, parent=None):
        super().__init__(parent)
        self.directory = directory
        self.rel_path = rel_path
        self.abs_path, _ = directory.get_child_path(self.rel_path)
        self.data = data
        self.relations = {}
        self.attrs = {}

    def set_attrs(self, attrs):
        self.attrs.update(attrs)

    def get_attr(self, key):
        return self.attrs.get(key)

    def add_relation(self, key, ws_file):
        self.relations[key] = ws_file
        self.relations[key].modified_cb = self.handle_modified

    def get_relation_data(self, key):
        rel = self.relations.get(key)
        if rel is None:
            return None
        return rel.data

    def set_data(self, data):
        self.data = data
        self.data.modified_cb = self.handle_modified
        self.reloaded.emit()

    def handle_modified(self, modified):
        self.modifiedChanged.emit(modified)

    def set_directory(self, directory):
        self.directory = directory
        self.abs_path, _ = directory.get_child_path(self.rel_path)
        for rel in self.relations.values():
            rel.set_directory(directory)

    def get_files_modified(self):
        files = [self, ]
        files.extend(
            rel for rel in self.relations.values()
            if rel.data.modified)
        return files

    def save(self):
        self.directory.ensure_dirs(self.rel_path)
        with open(self.abs_path, "wb") as fp:
            self.data.save(fp)

    def __repr__(self):
        return f"<WorkspaceFile {self.abs_path}>"

    def __hash__(self):
        return hash(self.directory) ^ hash(self.abs_path)


class Directory(QObject):
    changed = pyqtSignal(str)

    def __init__(self, name, file_icon, path, parent=None):
        super().__init__(parent)
        self.name = name
        self.file_icon = file_icon
        self.path = path

    def __repr__(self):
        return f"<Directory {self.name}: {self.path}>"

    def set_path(self, path):
        self.path = path
        self.changed.emit(path)

    @property
    def is_valid(self):
        return self.path is not None and os.path.exists(self.path)

    def get_child_path(self, rel_path):
        path = os.path.join(self.path, rel_path)
        exists = os.path.exists(path)
        return path, exists

    def get_child_rel_path(self, abs_path):
        return os.path.relpath(abs_path, self.path)

    def ensure_dirs(self, rel_path):
        abs_path, _ = self.get_child_path(rel_path)
        dir_path = os.path.dirname(abs_path)
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


class Workspace(QObject):
    fileOpened = pyqtSignal(str, str)
    fileActivated = pyqtSignal(str, str)
    fileClosed = pyqtSignal(str, str)
    fileLoadError = pyqtSignal(str, str, str)

    def __init__(self, directories, parent=None):
        super().__init__(parent)
        self.directories = directories
        self.files = dict()

    def open_file(self, directory, abs_path):
        abs_path = os.path.normpath(abs_path)
        rel_path = directory.get_child_rel_path(abs_path)
        if abs_path in self.files:
            self.fileActivated.emit(abs_path, rel_path)
        else:
            try:
                ws_file = WorkspaceFile(directory, rel_path, parent=self)
                FilePluginRegistry.load_model(ws_file)
                FilePluginRegistry.load_relations(ws_file, self.directories)
                self.files[abs_path] = ws_file
                self.fileOpened.emit(abs_path, rel_path)
            except Exception as e:
                log.exception("error loading path: %s", abs_path)
                self.fileLoadError.emit(abs_path, rel_path, str(e))

    def open_file_any_dir(self, rel_path):
        for directory in self.directories:
            abs_path, exists = directory.get_child_path(rel_path)
            if exists:
                return self.open_file(directory, abs_path)

    def close_file(self, ws_file):
        try:
            self.files.pop(ws_file.abs_path)
            self.fileClosed.emit(ws_file.abs_path, ws_file.rel_path)
        except (ValueError, KeyError):
            log.exception("error while closing file %s", ws_file)
