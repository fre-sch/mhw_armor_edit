# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.kire import KireEntry, Kire
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView


class KireEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = StructTableModel(KireEntry.fields(), self)
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


class KirePlugin(EditorPlugin):
    pattern = "*.kire"
    data_factory = Kire
    widget_factory = KireEditor
    relations = {}
