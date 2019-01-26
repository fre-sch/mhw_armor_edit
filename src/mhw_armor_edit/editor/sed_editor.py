# coding: utf-8
from PyQt5.QtWidgets import QWidget, QStackedLayout

from mhw_armor_edit.editor.models import EditorPlugin, EquipType
from mhw_armor_edit.ftypes.sed import Sed, SedEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView


class SedTableModel(StructTableModel):
    def __init__(self, parent=None):
        super().__init__(SedEntry.fields(), parent)

    def get_field_value(self, entry, field):
        value = getattr(entry, field)
        if field == "equip_type":
            return EquipType(value).name
        return super().get_field_value(entry, field)


class SedEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = SedTableModel(self)
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        if model is None:
            self.table_model.update([])
        else:
            self.table_model.update(model.data.entries)


class SedPlugin(EditorPlugin):
    pattern = "*.sed"
    data_factory = Sed
    widget_factory = SedEditor
    relations = {}
