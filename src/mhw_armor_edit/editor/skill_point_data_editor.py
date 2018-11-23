# coding: utf-8
# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.skl_pt_dat import SklPtDatEntry, SklPtDat
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n


class SkillPointDataModel(StructTableModel):
    def get_field_value(self, entry, field):
        if field == "skill_name":
            return get_t9n(self.model, "t9n", entry.index * 3)
        return getattr(entry, field)

    def update(self, model):
        self.model = model
        entries = [] if model is None else model["model"].entries
        super().update(entries)


class SkillPointDataEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = SkillPointDataModel(
            ("skill_name", "index", ) + SklPtDatEntry.fields(),
            [], parent=self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model["model"]
        self.table_model.update(model)


class SklPtDatPlugin(EditorPlugin):
    pattern = "*.skl_pt_dat"
    data_factory = SklPtDat
    widget_factory = SkillPointDataEditor
    relations = {
        r"common\equip\skill_point_data.skl_pt_dat": {
            "t9n": r"common\text\vfont\skill_pt_eng.gmd"
        }
    }
