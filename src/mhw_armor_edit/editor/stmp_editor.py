# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.stmp import Stmp, StmpEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n_item, get_t9n


class StmpTableModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(StmpEntry.fields(), parent)

    def get_field_value(self, entry, field):
        if field == "item1_id":
            return get_t9n_item(self.model, "t9n_item", entry.item1_id)
        if field == "item2_id":
            return get_t9n_item(self.model, "t9n_item", entry.item2_id)
        return getattr(entry, field)

    def update(self, model):
        self.model = model
        entries = [] if model is None else model.data.entries
        super().update(entries)


class StmpEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = StmpTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class StmpPlugin(EditorPlugin):
    pattern = "*.stmp"
    data_factory = Stmp
    widget_factory = StmpEditor
    relations = {
        r"common\facility\l_delivery.stmp": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
            "t9n_delivery": r"common\text\steam\l_delivery_eng.gmd",
        }
    }
