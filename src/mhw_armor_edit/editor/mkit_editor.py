# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.mkit import MkitEntry, Mkit
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n


class TableModel(StructTableModel):
    def __init__(self):
        super().__init__(("item", "index") + MkitEntry.fields(), [])

    def get_field_value(self, entry, field):
        if field == "item":
            return get_t9n(self.model, "t9n", entry.result_item_id * 2)
        return super().get_field_value(entry, field)

    def update(self, model):
        self.model = model
        entries = [] if model is None else model["model"].entries
        super().update(entries)


class MkitEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = TableModel()
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class MkitPlugin(EditorPlugin):
    pattern = "*.mkit"
    data_factory = Mkit
    widget_factory = MkitEditor
    relations = {
        r"common\maka\maka_item.mkit": {
            "t9n": r"common\text\steam\item_eng.gmd"
        }
    }
