# coding: utf-8
import logging
from contextlib import contextmanager
from functools import wraps
from typing import Sequence, Mapping

from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, QSettings
from PyQt5.QtWidgets import (QAction, QWidget, QItemDelegate, QComboBox)

log = logging.getLogger(__name__)


def get_t9n(model, key, index):
    t9n = model.get_relation_data(key)
    if t9n is None:
        return f"{key}({index})"
    # val = t9n.get_string(index, f"{key}({index})")
    # return f"{val}({index})"
    try:
        val = t9n.items[index].value
        if not val:
            return f"<blank:{index}>"
        return val \
            .replace("<ICON ALPHA>", " α") \
            .replace("<ICON BETA>", " β") \
            .replace("<ICON GAMMA>", " γ")
    except IndexError:
        log.warning("missing item at index %s", index)
        return f"{key}({index}) <missing t9n>"


def get_t9n_item(model, key, index):
    return get_t9n(model, key, index * 2)


def get_t9n_skill(model, key, index):
    return get_t9n(model, key, index * 3)


def create_action(icon, title, handler, shortcut=None, checkable=None):
    action = QAction(title) if icon is None else QAction(icon, title)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if checkable is not None:
        action.setCheckable(checkable)
    action.triggered.connect(handler)
    return action


class ItemDelegate(QItemDelegate):
    """
    An item delegate that is aware of comboboxes and able to use Qt.UserRole data
    """
    def setEditorData(self, editor: QWidget, qindex: QModelIndex):
        if isinstance(editor, QComboBox):
            index = editor.findData(qindex.data(), Qt.UserRole)
            editor.setCurrentIndex(index)
        else:
            super().setEditorData(editor, qindex)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     qindex: QModelIndex):
        if isinstance(editor, QComboBox):
            value = editor.currentData(Qt.UserRole)
            model.setData(qindex, value, Qt.EditRole)
        else:
            super().setModelData(editor, model, qindex)


def is_sequence(value):
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (bytes, bytearray, str, Mapping))
    )


def yield_to_list(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        return list(fn(*args, **kwargs))
    return inner


class SettingsGroup:
    def __init__(self, inst: QSettings, key):
        self.inst = inst
        inst.beginGroup(key)

    def __setitem__(self, key, value):
        self.inst.setValue(key, value)

    def get(self, key, default):
        return self.inst.value(key, default)

    def childKeys(self):
        return self.inst.childKeys()

    @classmethod
    @contextmanager
    def begin(cls, settings, key):
        try:
            yield cls(settings, key)
        finally:
            settings.endGroup()


class AppSettings:
    def __init__(self):
        self.handle = QSettings(QSettings.IniFormat, QSettings.UserScope,
                                "fre-sch.github.com", "MHW-Editor-Suite")

    def main_window(self):
        return SettingsGroup.begin(self.handle, "MainWindow")

    def application(self):
        return SettingsGroup.begin(self.handle, "Application")

    def import_export(self):
        return SettingsGroup.begin(self.handle, "ImportExport")
