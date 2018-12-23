# coding: utf-8
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin
from mhw_armor_edit.ftypes.oam_dat import OAmDat, OAmDatEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView
from mhw_armor_edit.utils import get_t9n


(id, *fields) = OAmDatEntry.fields()
columns = (id, "series", "name", "description", *fields)


class OtomoArmorTableModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(columns, parent)

    def get_field_value(self, entry, field):
        if field == "name":
            return get_t9n(self.model, "t9n_armor", entry.gmd_name_index)
        if field == "description":
            return get_t9n(self.model, "t9n_armor", entry.gmd_desc_index)
        if field == "series":
            return get_t9n(self.model, "t9n_armor_series", entry.set_id)
        return getattr(entry, field)

    def flags(self, qindex: QModelIndex):
        if qindex.isValid():
            if qindex.column() in (1, 2, 3):
                return super().flags(qindex) & ~Qt.ItemIsEditable
        return super().flags(qindex)

    def update(self, model):
        self.model = model
        entries = [] if model is None else model.data.entries
        super().update(entries)


class OtomoArmorEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = OtomoArmorTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        self.table_model.update(model)


class OtomoArmorEditorPlugin(EditorPlugin):
    pattern = "*.oam_dat"
    data_factory = OAmDat
    widget_factory = OtomoArmorEditor
    relations = {
        r"common\equip\otomoArmor.oam_dat": {
            "t9n_armor": r"common\text\steam\ot_armor_eng.gmd",
            "t9n_armor_series": r"common\text\steam\ot_series_eng.gmd",
        }
    }
