# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.sgpa import Sgpa
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n_item, get_t9n_skill


class SgpaTableModel(StructTableModel):
    def __init__(self):
        super().__init__((
            "id",
            "name",
            "order",
            "size",
            "skill1_id",
            "skill1_name",
            "skill1_incr",
            "skill2_id",
            "skill2_name",
            "skill2_incr",
        ), [])

    def get_field_value(self, entry, field):
        if field == "name":
            return get_t9n_item(self.model, "t9n_item", entry.id)
        if field == "skill1_name":
            return get_t9n_skill(self.model, "t9n_skill_pt", entry.skill1_id)
        if field == "skill2_name":
            return get_t9n_skill(self.model, "t9n_skill_pt", entry.skill2_id)
        return getattr(entry, field)

    def update(self, model):
        self.model = model
        entries = [] if model is None else model.data.entries
        super().update(entries)


class SgpaEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = SgpaTableModel()
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class SgpaPlugin(EditorPlugin):
    pattern = "*.sgpa"
    data_factory = Sgpa
    widget_factory = SgpaEditor
    relations = {
        r"common\item\skillGemParam.sgpa": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
            "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
        }
    }
