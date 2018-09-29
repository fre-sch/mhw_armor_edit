# coding: utf-8
from PyQt5.QtWidgets import QWidget, QTableView, QStackedLayout

from mhw_armor_edit.ftypes.sh_tbl import ShellTableEntry
from mhw_armor_edit.struct_table import StructTableModel, SortFilterTableView

"""
[ Normal v ]
[ Pierce   ]
[ Spread   ]
     count   type   reload
1    [____]  [____] [____]
2    [____]  [____] [____]
3    [____]  [____] [____]

"""
class ShellTableEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.table_model = StructTableModel(
            ShellTableEntry.fields(), [])
        self.table_view = SortFilterTableView(self)
        self.table_view.setModel(self.table_model)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model["model"]
        if model is None:
            self.table_model.update([])
        else:
            self.table_model.update(self.model.entries)
            self.table_view.resizeColumnsToContents()
