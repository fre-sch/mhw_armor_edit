# coding: utf-8
import logging

from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel
from PyQt5.QtWidgets import (QAction, QGroupBox, QFormLayout, QLabel, QWidget,
                             QItemDelegate, QComboBox)


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


def create_action(icon, title, handler, shortcut=None):
    action = QAction(icon, title)
    if shortcut is not None:
        action.setShortcut(shortcut)
    action.triggered.connect(handler)
    return action


class FormGroupbox(QGroupBox):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("QGroupBox {font-weight:bold}")
        self.setLayout(QFormLayout(self))
        if title:
            self.setTitle(title)
            self.setFlat(True)

    def __iadd__(self, other):
        left, right = other
        if not isinstance(left, QWidget):
            left = QLabel(str(left))
        if not isinstance(right, QWidget):
            right = QLabel(str(right))
        self.layout().addRow(left, right)
        return self


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
