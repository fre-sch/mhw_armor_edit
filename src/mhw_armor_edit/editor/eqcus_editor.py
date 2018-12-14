# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.eq_cus import EqCus, EqCusEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n_item


class EqCusTableModel(StructTableModel):
    ItemIds = ("key_item_id", "item1_id", "item2_id", "item3_id", "item4_id")

    def __init__(self):
        super().__init__(EqCusEntry.fields(), [])

    def get_field_value(self, entry, field):
        value = getattr(entry, field)
        if field in self.ItemIds:
            return get_t9n_item(self.model, "t9n_item", value)
        return value

    def update(self, model):
        self.model = model
        if model is None:
            super().update([])
        else:
            super().update(model.data.entries)


class EqCusEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = EqCusTableModel()
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class EqCusPlugin(EditorPlugin):
    pattern = "*.eq_cus"
    data_factory = EqCus
    widget_factory = EqCusEditor
    relations = {
        r"common\equip\equip_custom.eq_cus": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        },
        r"common\equip\weapon.eq_cus": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        },
        r"common\equip\insect.eq_cus": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        },
        r"common\equip\insect_element.eq_cus": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        }
    }
