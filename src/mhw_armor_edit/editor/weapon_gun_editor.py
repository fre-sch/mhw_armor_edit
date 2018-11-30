# coding: utf-8
import logging

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.wp_dat_g import WpDatGEntry, WpDatG
from mhw_armor_edit.struct_table import SortFilterTableView, StructTableModel
from mhw_armor_edit.utils import get_t9n

log = logging.getLogger()


class WpDatGTableModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(WpDatGEntry.fields(), [], parent=parent)
        self.model = None

    def get_field_value(self, entry, field):
        value = getattr(entry, field)
        if field in ("gmd_name_index", "gmd_description_index"):
            return get_t9n(self.model, "t9n", value)
        return value

    def update(self, model):
        self.model = model
        entries = [] if model is None else model.data.entries
        super().update(entries)


class WpDatGEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = WpDatGTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class WpDatGPlugin(EditorPlugin):
    pattern = "*.wp_dat_g"
    data_factory = WpDatG
    widget_factory = WpDatGEditor
    relations = {
        r"common\equip\lbg.wp_dat_g": {
            "shell_table": r"common\equip\shell_table.shl_tbl",
            "t9n": r"common\text\steam\lbg_eng.gmd",
            "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
        },
        r"common\equip\hbg.wp_dat_g": {
            "shell_table": r"common\equip\shell_table.shl_tbl",
            "t9n": r"common\text\steam\hbg_eng.gmd",
            "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
        },
        r"common\equip\bow.wp_dat_g": {
            "bottle_table": r"common\equip\bottle_table.bbtbl",
            "t9n": r"common\text\steam\bow_eng.gmd",
            "t9n_skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
        },
    }
