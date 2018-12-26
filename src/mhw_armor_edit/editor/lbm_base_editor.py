# coding: utf-8

from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin, EquipType
from mhw_armor_edit.ftypes.lbm_base import LbmBase, LbmBaseEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n_item


class LbmBaseTableModel(StructTableModel):
    ItemIds = ("item1_id", "item2_id")

    def __init__(self, parent=None):
        super().__init__(LbmBaseEntry.fields(), parent)

    def get_field_value(self, entry, field):
        value = getattr(entry, field)
        if field in self.ItemIds:
            return get_t9n_item(self.model, "t9n_item", value)
        if field == "equip_type":
            return EquipType(value).name
        return value

    def update(self, model):
        self.model = model
        if model is None:
            super().update([])
        else:
            super().update(model.data.entries)


class LbmBaseEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = LbmBaseTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class LbmBasePlugin(EditorPlugin):
    pattern = "*.lbm_base"
    data_factory = LbmBase
    widget_factory = LbmBaseEditor
    relations = {
        r"common\equip\limit_break_mat_base.lbm_base": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        }
    }
