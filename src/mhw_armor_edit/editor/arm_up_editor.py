# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.arm_up import ArmUp, ArmUpEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView

columns = (
    "index",
    *ArmUpEntry.fields()
)


class ArmUpEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = StructTableModel(columns, self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update([] if model is None else self.model.data.entries)


class ArmUpPlugin(EditorPlugin):
    pattern = "*.arm_up"
    data_factory = ArmUp
    widget_factory = ArmUpEditor
    relations = {}
