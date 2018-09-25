# coding: utf-8

from PyQt5.QtWidgets import (QWidget, QTableView,
                             QStackedLayout)

from mhw_armor_edit.ftypes.eq_crt import EqCrtEntry
from mhw_armor_edit.tree import StructTableModel


class CraftingTableEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_view = QTableView(self)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        if model is None:
            self.table_view.setModel(None)
        else:
            self.table_view.setModel(
                StructTableModel(EqCrtEntry.fields(),
                                 self.model.entries)
            )
            self.table_view.resizeColumnsToContents()
