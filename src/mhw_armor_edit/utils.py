# coding: utf-8
from PyQt5.QtWidgets import QAction, QGroupBox, QFormLayout, QLabel, QWidget


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
