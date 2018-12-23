# coding: utf-8
# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.skl_dat import SklDat, SklDatEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n


class SkillDataModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(("skill_name", *SklDatEntry.fields()), parent)

    def get_field_value(self, entry, field):
        if field == "skill_name":
            return get_t9n(self.model, "t9n", entry.skill_id * 3)
        return getattr(entry, field)

    def update(self, model):
        self.model = model
        entries = [] if model is None else model.data.entries
        super().update(entries)


class SkillDataEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = SkillDataModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class SklDatPlugin(EditorPlugin):
    pattern = "*.skl_dat"
    data_factory = SklDat
    widget_factory = SkillDataEditor
    relations = {
        r"common\equip\skill_data.skl_dat": {
            "t9n": r"common\text\vfont\skill_pt_eng.gmd"
        }
    }
