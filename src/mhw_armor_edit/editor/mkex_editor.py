# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.mkex import MkexEntry, Mkex
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n


class TableModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(("item", *MkexEntry.fields()), parent)

    def get_field_value(self, entry, field):
        if field == "item":
            return get_t9n(self.model, "t9n", entry.source_item_id * 2)
        return super().get_field_value(entry, field)

    def update(self, model):
        self.model = model
        entries = [] if model is None else model.data.entries
        super().update(entries)


class MkexEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = TableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class MkexPlugin(EditorPlugin):
    pattern = "*.mkex"
    data_factory = Mkex
    widget_factory = MkexEditor
    relations = {
        r"common\maka\maka_exchange.mkex": {
            "t9n": r"common\text\steam\item_eng.gmd"
        }
    }
