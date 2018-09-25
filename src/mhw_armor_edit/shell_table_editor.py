# coding: utf-8
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtWidgets import QWidget, QTableView, QStackedLayout, QGridLayout

from mhw_armor_edit.ftypes.sh_tbl import ShellTableEntry
from mhw_armor_edit.tree import StructTableModel


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
        self.table_view = QTableView(self)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(self.table_view)

    def set_model(self, model):
        self.model = model
        if model is None:
            self.table_view.setModel(None)
        else:
            self.table_view.setModel(
                StructTableModel(ShellTableEntry.fields(),
                                 self.model.entries)
            )
            self.table_view.resizeColumnsToContents()
