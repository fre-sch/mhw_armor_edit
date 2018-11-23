# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.wep_wsl import WepWslEntry, WepWsl
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView


class WepWslEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = StructTableModel(WepWslEntry.fields(), [])
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model["model"]
        if model is None:
            self.table_model.update([])
        else:
            self.table_model.update(self.model.entries)


class WepWslPlugin(EditorPlugin):
    pattern = "*.wep_wsl"
    data_factory = WepWsl
    widget_factory = WepWslEditor
    relations = {}
