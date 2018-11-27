# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.bbtbl import BbtblEntry, Bbtbl
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView


class BbtblEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = StructTableModel(
            ("index", ) + BbtblEntry.fields(), [])
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        if model is None:
            self.table_model.update([])
        else:
            self.table_model.update(self.model.data.entries)


class BbtblPlugin(EditorPlugin):
    pattern = "*.bbtbl"
    data_factory = Bbtbl
    widget_factory = BbtblEditor
    relations = {}
