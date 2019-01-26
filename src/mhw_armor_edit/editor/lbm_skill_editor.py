# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin, WeaponAugment
from mhw_armor_edit.ftypes.lbm_skill import LbmSkill, LbmSkillEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n_item


class LbmSkillTableModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(("index", *LbmSkillEntry.fields()), parent)

    def get_field_value(self, entry, field):
        value = getattr(entry, field)
        if field == "augment_type":
            return WeaponAugment(value).name
        if field == "item_id":
            return get_t9n_item(self.model, "t9n_item", value)
        return value

    def update(self, model):
        self.model = model
        if model is None:
            super().update([])
        else:
            super().update(model.data.entries)


class LbmSkillEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = LbmSkillTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class LbmSkillPlugin(EditorPlugin):
    pattern = "*.lbm_skill"
    data_factory = LbmSkill
    widget_factory = LbmSkillEditor
    relations = {
        r"common\equip\limit_break_mat_skill.lbm_skill": {
            "t9n_item": r"common\text\steam\item_eng.gmd",
        }
    }
