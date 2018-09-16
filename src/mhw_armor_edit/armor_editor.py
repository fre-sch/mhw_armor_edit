# -*- coding: utf-8 -*-
import logging
import sys

from PyQt5.QtCore import (Qt, QModelIndex)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication,
                             QSplitter, QGroupBox, QFormLayout,
                             QLabel, QBoxLayout, QWidget, QGridLayout,
                             QStyle, QTreeView, QFileDialog,
                             QMessageBox, QTabWidget)

from mhw_armor_edit import AmDat
from mhw_armor_edit.assets import Definitions
from mhw_armor_edit.tree import ArmorSetTreeModel, ArmorSetNode, ArmorListModel
from mhw_armor_edit.view_ctrl import (ComboBoxWidgetCtrl, SpinBoxWidgetCtrl,
                                      LabelWidgetCtrl,
                                      PieceViewCtrl)

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def groupbox(layout, title=None):
    box = QGroupBox()
    box.setStyleSheet("QGroupBox {font-weight:bold}")
    if title:
        box.setTitle(title)
        box.setFlat(True)
    box.setLayout(layout)
    return box, layout


def tree_index_is_root(index: QModelIndex):
    return not index.isValid()


def create_action(icon, title, handler, shortcut=None):
    action = QAction(icon, title)
    if shortcut is not None:
        action.setShortcut(shortcut)
    action.triggered.connect(handler)
    return action


class FileModel:
    def __init__(self, path, data):
        self.path = path
        self.data = data

    def save(self):
        with open(self.path, "wb") as fp:
            fp.write(self.data.data)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as fp:
            data = AmDat.make(fp)
        return cls(path, data)


class ArmorPieceWidget(QWidget):
    def __init__(self, view, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self._init(view)

    def _init(self, view):
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.setLayout(layout)
        self._init_basic(layout, view)
        self._init_resistance(layout, view)
        self._init_gem_slots(layout, view)
        self._init_set_skills(layout, view)
        self._init_piece_skills(layout, view)

    def _init_piece_skills(self, layout, view):
        box, box_layout = groupbox(QFormLayout(), "Piece Skills")
        layout.addWidget(box, 0)
        view.skill1.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completer=True)
        view.skill1_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        view.skill2.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completer=True)
        view.skill2_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        view.skill3.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completer=True)
        view.skill3_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        box_layout.addRow(QLabel("Skill 1"), view.skill1.ctrl.widget)
        box_layout.addRow(QLabel("Level"), view.skill1_lvl.ctrl.widget)
        box_layout.addRow(QLabel("Skill 2"), view.skill2.ctrl.widget)
        box_layout.addRow(QLabel("Level"), view.skill2_lvl.ctrl.widget)
        box_layout.addRow(QLabel("Skill 3"), view.skill3.ctrl.widget)
        box_layout.addRow(QLabel("Level"), view.skill3_lvl.ctrl.widget)

    def _init_set_skills(self, layout, view):
        box, box_layout = groupbox(QFormLayout(), "Set Skills")
        layout.addWidget(box, 0)
        view.set_skill1.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completer=True)
        view.set_skill1_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        view.set_skill2.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completer=True)
        view.set_skill2_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        box_layout.addRow(QLabel("Skill 1"), view.set_skill1.ctrl.widget)
        box_layout.addRow(QLabel("Level"), view.set_skill1_lvl.ctrl.widget)
        box_layout.addRow(QLabel("Skill 2"), view.set_skill2.ctrl.widget)
        box_layout.addRow(QLabel("Level"), view.set_skill2_lvl.ctrl.widget)

    def _init_gem_slots(self, layout, view):
        box, box_layout = groupbox(QFormLayout(), "Gem Slots")
        layout.addWidget(box, 0)
        view.num_gem_slots.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        view.gem_slot1_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        view.gem_slot2_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        view.gem_slot3_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        box_layout.addRow(QLabel("Active slots"), view.num_gem_slots.ctrl.widget)
        box_layout.addRow(QLabel("Slot 1 Level"), view.gem_slot1_lvl.ctrl.widget)
        box_layout.addRow(QLabel("Slot 2 Level"), view.gem_slot2_lvl.ctrl.widget)
        box_layout.addRow(QLabel("Slot 3 Level"), view.gem_slot3_lvl.ctrl.widget)

    def _init_resistance(self, layout, view):
        box, box_layout = groupbox(QFormLayout(), "Resistance")
        layout.addWidget(box, 0)
        view.fire_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        view.water_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        view.thunder_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        view.ice_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        view.dragon_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        box_layout.addRow(QLabel("Fire"), view.fire_res.ctrl.widget)
        box_layout.addRow(QLabel("Water"), view.water_res.ctrl.widget)
        box_layout.addRow(QLabel("Thunder"), view.thunder_res.ctrl.widget)
        box_layout.addRow(QLabel("Ice"), view.ice_res.ctrl.widget)
        box_layout.addRow(QLabel("Dragon"), view.dragon_res.ctrl.widget)

    def _init_basic(self, layout, view):
        section_box, section_layout = groupbox(QGridLayout())
        layout.addWidget(section_box)
        section_layout.setColumnStretch(0, 0)
        section_layout.setColumnStretch(1, 1)
        section_layout.setColumnStretch(2, 0)
        section_layout.setColumnStretch(3, 1)

        view.set_name.ctrl = LabelWidgetCtrl(Definitions.set)
        section_layout.addWidget(QLabel("Set:"), 0, 0, Qt.AlignLeft)
        section_layout.addWidget(view.set_name.ctrl.widget, 0, 1, Qt.AlignLeft)

        section_layout.addWidget(QLabel("Index:"), 0, 2, Qt.AlignLeft)
        view.index.ctrl = LabelWidgetCtrl([])
        section_layout.addWidget(view.index.ctrl.widget, 0, 3, Qt.AlignLeft)

        section_layout.addWidget(QLabel("Variant:"), 2, 0, Qt.AlignLeft)
        view.variant.ctrl = LabelWidgetCtrl(Definitions.variant)
        section_layout.addWidget(view.variant.ctrl.widget, 2, 1, Qt.AlignLeft)
        section_layout.addWidget(QLabel("Equip Slot:"), 2, 2, Qt.AlignLeft)
        view.equip_slot.ctrl = LabelWidgetCtrl(Definitions.equip_slot)
        section_layout.addWidget(view.equip_slot.ctrl.widget, 2, 3, Qt.AlignLeft)

        section_box, section_layout = groupbox(QFormLayout(), "Basic")
        layout.addWidget(section_box, 0)
        view.defense.ctrl = SpinBoxWidgetCtrl(0, 0xffff)
        section_layout.addRow(QLabel("Defense"), view.defense.ctrl.widget)
        view.rarity.ctrl = ComboBoxWidgetCtrl(Definitions.rarity)
        section_layout.addRow(QLabel("Rarity"), view.rarity.ctrl.widget)
        view.cost.ctrl = SpinBoxWidgetCtrl(0, 0xffff)
        section_layout.addRow(QLabel("Cost"), view.cost.ctrl.widget)


class StructuredEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_model = None
        self.current_piece_view_ctrl = PieceViewCtrl()
        self.init_actions()
        self.init_toolbar()
        self.init_menubar()
        self.init_ui()
        self.current_piece_view_ctrl.update(None)

    def get_icon(self, name):
        return self.style().standardIcon(name)

    def init_actions(self):
        self.open_file_action = create_action(
            self.get_icon(QStyle.SP_DialogOpenButton),
            "Open file ...",
            self.handle_open_file_action,
            QKeySequence.Open)
        self.save_file_action = create_action(
            self.get_icon(QStyle.SP_DialogSaveButton),
            "Save ...",
            self.handle_save_file_action,
            QKeySequence.Save)
        self.save_file_as_action = create_action(
            self.get_icon(QStyle.SP_DialogSaveButton),
            "Save as ...",
            self.handle_save_file_as_action,
            QKeySequence.SaveAs)
        self.close_file_action = create_action(
            self.get_icon(QStyle.SP_DialogCloseButton),
            "Close file",
            self.handle_close_file_action,
            QKeySequence(Qt.CTRL + Qt.Key_W))

    def init_menubar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.insertAction(None, self.open_file_action)
        file_menu.insertAction(None, self.save_file_action)
        file_menu.insertAction(None, self.save_file_as_action)
        file_menu.insertAction(None, self.close_file_action)

    def init_ui(self):
        split = QSplitter(Qt.Horizontal, self)
        split.setChildrenCollapsible(False)
        tab_widget = QTabWidget(split)
        tab_widget.addTab(self.init_parts_tree(), "Sets")
        tab_widget.addTab(self.init_parts_list(), "List")
        split.addWidget(tab_widget)
        split.addWidget(ArmorPieceWidget(self.current_piece_view_ctrl))
        self.setCentralWidget(split)
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Armor Editor')
        self.show()

    def init_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.insertAction(None, self.open_file_action)
        toolbar.insertAction(None, self.save_file_action)
        toolbar.insertAction(None, self.close_file_action)

    def init_parts_list(self):
        self.parts_list_view = QTreeView()
        self.parts_list_view.activated.connect(self.handle_parts_list_activated)
        return self.parts_list_view

    def init_parts_tree(self):
        self.parts_tree_view = QTreeView()
        self.parts_tree_view.activated.connect(self.handle_parts_tree_activated)
        return self.parts_tree_view

    def handle_open_file_action(self):
        file_path, _ = QFileDialog.getOpenFileName(parent=self)
        if file_path:
            self.handle_file_selected(file_path)

    def handle_save_file_action(self):
        if self.file_model is None:
            return
        try:
            self.file_model.save()
        except Exception as e:
            QMessageBox.warning(self,
                                "Error writing file", str(e),
                                QMessageBox.Ok, QMessageBox.Ok)

    def handle_save_file_as_action(self):
        if self.file_model is None:
            return
        file_path, _ = QFileDialog.getSaveFileName(self)
        if file_path:
            self.file_model.path = file_path
            self.handle_save_file_action()

    def handle_close_file_action(self):
        self.file_model = None
        self.parts_tree_view.setModel(None)
        self.parts_list_view.setModel(None)
        self.current_piece_view_ctrl.update(None)

    def handle_file_selected(self, file_path):
        try:
            self.file_model = FileModel.load(file_path)
        except Exception as e:
            self.file_model = None
            QMessageBox.warning(self,
                                "Error opening file", str(e),
                                QMessageBox.Ok, QMessageBox.Ok)
            return
        self.parts_tree_view.setModel(
            ArmorSetTreeModel(self.file_model.data.entries))
        self.parts_list_view.setModel(
            ArmorListModel(self.file_model.data.entries))

    def handle_parts_tree_activated(self, qindex):
        if isinstance(qindex.internalPointer(), ArmorSetNode):
            return
        index = qindex.internalPointer().ref.index
        model = self.file_model.data.find_first(index=index)
        self.current_piece_view_ctrl.update(model)

    def handle_parts_list_activated(self, qindex):
        index = qindex.row()
        model = self.file_model.data.find_first(index=index)
        self.current_piece_view_ctrl.update(model)


if __name__ == '__main__':
    Definitions.load()
    app = QApplication(sys.argv)
    ex = StructuredEditorWindow()
    sys.exit(app.exec_())
