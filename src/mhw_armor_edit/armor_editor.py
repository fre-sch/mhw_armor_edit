# -*- coding: utf-8 -*-
import csv
import logging
import sys

from PyQt5.QtCore import (Qt)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication,
                             QSplitter, QGroupBox, QFormLayout,
                             QLabel, QBoxLayout, QWidget, QStyle, QTreeView,
                             QFileDialog,
                             QMessageBox, QTabWidget, QStackedLayout)

from mhw_armor_edit.assets import Definitions
from mhw_armor_edit.tree import ArmorSetTreeModel, ArmorSetNode, ArmorListModel
from mhw_armor_edit.ftypes.am_dat import AmDat, AmDatEntry
from mhw_armor_edit.view_ctrl import (ComboBoxWidgetCtrl, SpinBoxWidgetCtrl,
                                      LabelWidgetCtrl,
                                      ArmorPieceViewCtrl)

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class FormGroupbox(QGroupBox):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("QGroupBox {font-weight:bold}")
        self.setLayout(QFormLayout(self))
        if title:
            self.setTitle(title)
            self.setFlat(True)

    def __iadd__(self, other):
        self.layout().addRow(QLabel(other[0]), other[1])
        return self


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
            data = AmDat.load(fp)
        return cls(path, data)


class ArmorPieceWidget(QWidget):
    def __init__(self, view, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self._init(view)

    def _init(self, view):
        self.setLayout(QBoxLayout(QBoxLayout.TopToBottom))
        self._init_info(view)
        self._init_basic(view)
        self._init_resistance(view)
        self._init_gem_slots(view)
        self._init_set_skills(view)
        self._init_piece_skills(view)

    def _init_piece_skills(self, view):
        box = FormGroupbox("Piece Skills")
        self.layout().addWidget(box, 0)
        view.skill1.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completion_enabled=True)
        view.skill1_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        view.skill2.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completion_enabled=True)
        view.skill2_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        view.skill3.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completion_enabled=True)
        view.skill3_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        box += "Skill 1", view.skill1.ctrl.widget
        box += "Level", view.skill1_lvl.ctrl.widget
        box += "Skill 2", view.skill2.ctrl.widget
        box += "Level", view.skill2_lvl.ctrl.widget
        box += "Skill 3", view.skill3.ctrl.widget
        box += "Level", view.skill3_lvl.ctrl.widget

    def _init_set_skills(self, view):
        box = FormGroupbox("Set Skills")
        self.layout().addWidget(box, 0)
        view.set_skill1.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completion_enabled=True)
        view.set_skill1_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        view.set_skill2.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completion_enabled=True)
        view.set_skill2_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        box += "Skill 1", view.set_skill1.ctrl.widget
        box += "Level", view.set_skill1_lvl.ctrl.widget
        box += "Skill 2", view.set_skill2.ctrl.widget
        box += "Level", view.set_skill2_lvl.ctrl.widget

    def _init_gem_slots(self, view):
        box = FormGroupbox("Gem Slots")
        self.layout().addWidget(box, 0)
        view.num_gem_slots.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        view.gem_slot1_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        view.gem_slot2_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        view.gem_slot3_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        box += "Active slots", view.num_gem_slots.ctrl.widget
        box += "Slot 1 Level", view.gem_slot1_lvl.ctrl.widget
        box += "Slot 2 Level", view.gem_slot2_lvl.ctrl.widget
        box += "Slot 3 Level", view.gem_slot3_lvl.ctrl.widget

    def _init_resistance(self, view):
        box = FormGroupbox("Resistance")
        self.layout().addWidget(box, 0)
        view.fire_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        view.water_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        view.thunder_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        view.ice_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        view.dragon_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        box += "Fire", view.fire_res.ctrl.widget
        box += "Water", view.water_res.ctrl.widget
        box += "Thunder", view.thunder_res.ctrl.widget
        box += "Ice", view.ice_res.ctrl.widget
        box += "Dragon", view.dragon_res.ctrl.widget

    def _init_basic(self, view):
        box = FormGroupbox("Basic")
        self.layout().addWidget(box, 0)
        view.defense.ctrl = SpinBoxWidgetCtrl(0, 0xffff)
        view.rarity.ctrl = ComboBoxWidgetCtrl(Definitions.rarity)
        view.cost.ctrl = SpinBoxWidgetCtrl(0, 0xffff)
        box += "Defense", view.defense.ctrl.widget
        box += "Rarity", view.rarity.ctrl.widget
        box += "Cost", view.cost.ctrl.widget

    def _init_info(self, view):
        box = FormGroupbox(None)
        self.layout().addWidget(box)
        view.set_name.ctrl = LabelWidgetCtrl(Definitions.set)
        view.index.ctrl = LabelWidgetCtrl([])
        view.variant.ctrl = LabelWidgetCtrl(Definitions.variant)
        view.equip_slot.ctrl = LabelWidgetCtrl(Definitions.equip_slot)
        view.gmd_string_index.ctrl = LabelWidgetCtrl()
        box += "Set:", view.set_name.ctrl.widget
        box += "Index:", view.index.ctrl.widget
        box += "String-Index:", view.gmd_string_index.ctrl.widget
        box += "Variant:", view.variant.ctrl.widget
        box += "Equip Slot:", view.equip_slot.ctrl.widget


class ArmorEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.armor_data = None
        self.current_piece_view_ctrl = ArmorPieceViewCtrl()
        split = QSplitter(Qt.Horizontal, self)
        split.setChildrenCollapsible(False)
        tab_widget = QTabWidget(split)
        tab_widget.addTab(self.init_parts_tree(), "Sets")
        tab_widget.addTab(self.init_parts_list(), "List")
        split.addWidget(tab_widget)

        tab_widget = QTabWidget(split)
        tab_widget.addTab(ArmorPieceWidget(self.current_piece_view_ctrl), "Config")
        tab_widget.addTab(QLabel(""), "Crafting")
        split.addWidget(tab_widget)
        split.setSizes([250, ])
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 5)
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(split)

    def init_parts_list(self):
        self.parts_list_view = QTreeView()
        self.parts_list_view.activated.connect(self.handle_parts_list_activated)
        return self.parts_list_view

    def init_parts_tree(self):
        self.parts_tree_view = QTreeView()
        self.parts_tree_view.activated.connect(self.handle_parts_tree_activated)
        return self.parts_tree_view

    def handle_parts_tree_activated(self, qindex):
        if isinstance(qindex.internalPointer(), ArmorSetNode):
            return
        index = qindex.internalPointer().ref.index
        model = self.armor_data.find_first(index=index)
        self.current_piece_view_ctrl.update(model)

    def handle_parts_list_activated(self, qindex):
        index = qindex.row()
        model = self.armor_data.find_first(index=index)
        self.current_piece_view_ctrl.update(model)

    def set_model(self, armor_data):
        self.armor_data = armor_data
        if armor_data is None:
            self.parts_tree_view.setModel(None)
            self.parts_list_view.setModel(None)
        else:
            self.parts_tree_view.setModel(
                ArmorSetTreeModel(self.armor_data.entries)
            )
            self.parts_list_view.setModel(
                ArmorListModel(self.armor_data.entries)
            )
            self.parts_list_view.setColumnWidth(0, 50)
        self.current_piece_view_ctrl.update(None)


class ArmorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_model = None
        self.current_piece_view_ctrl = ArmorPieceViewCtrl()
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
        self.export_csv_action = create_action(
            self.get_icon(QStyle.SP_FileIcon),
            "Export CSV...",
            self.handle_export_csv_action,
            None)
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
        file_menu.addSeparator()
        file_menu.insertAction(None, self.export_csv_action)
        file_menu.addSeparator()
        file_menu.insertAction(None, self.close_file_action)

    def init_ui(self):
        self.armor_editor = ArmorEditor(self)
        self.setCentralWidget(self.armor_editor)
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Armor Editor')
        self.show()

    def init_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.insertAction(None, self.open_file_action)
        toolbar.insertAction(None, self.save_file_action)
        toolbar.insertAction(None, self.close_file_action)

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

    def handle_export_csv_action(self):
        if self.file_model is None:
            return
        file_path, _ = QFileDialog.getSaveFileName(self)
        if file_path:
            with open(file_path, "w") as fp:
                writer = csv.DictWriter(fp, AmDatEntry.fields(),
                                        delimiter=";", quotechar='"',
                                        doublequote=False, escapechar='"',
                                        lineterminator="\n")
                writer.writeheader()
                writer.writerows(entry.as_dict() for entry in self.file_model.data)

    def handle_close_file_action(self):
        self.armor_editor.set_model(None)
        self.file_model = None

    def handle_file_selected(self, file_path):
        try:
            self.file_model = FileModel.load(file_path)
        except Exception as e:
            self.file_model = None
            QMessageBox.warning(self,
                                "Error opening file", str(e),
                                QMessageBox.Ok, QMessageBox.Ok)
            return
        self.armor_editor.set_model(self.file_model.data)


if __name__ == '__main__':
    Definitions.load()
    app = QApplication(sys.argv)
    window = ArmorEditorWindow()
    sys.exit(app.exec_())
