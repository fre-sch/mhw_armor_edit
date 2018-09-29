# -*- coding: utf-8 -*-
import csv
import logging
import sys
from collections.__init__ import defaultdict

from PyQt5.QtCore import (Qt, QModelIndex, QAbstractTableModel)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QMainWindow, QApplication,
                             QSplitter, QBoxLayout, QWidget, QStyle,
                             QTreeView,
                             QFileDialog,
                             QMessageBox, QTabWidget, QStackedLayout,
                             QDataWidgetMapper, QSpinBox)

from mhw_armor_edit.assets import Definitions
from mhw_armor_edit.crafting_editor import CraftingRequirementsEditor
from mhw_armor_edit.ftypes.am_dat import AmDat, AmDatEntry
from mhw_armor_edit.tree import TreeModel, TreeNode
from mhw_armor_edit.utils import create_action, FormGroupbox
from mhw_armor_edit.view_ctrl import (ArmorPieceViewCtrl)

log = logging.getLogger()


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


class ArmorPieceItemModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fields = AmDatEntry.fields()
        self.entry = None

    def update(self, entry):
        self.beginResetModel()
        self.entry = entry
        self.endResetModel()

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.fields)

    def rowCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, qindex: QModelIndex, role=None):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            return getattr(self.entry, self.fields[qindex.column()])

    def setData(self, qindex: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            try:
                attr = self.fields[qindex.column()]
                setattr(self.entry, attr, int(value))
                self.dataChanged.emit(qindex, qindex)
                log.debug("attr set %s: %s", attr, value)
            except ValueError:
                log.debug("error setting attr")

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return self.fields[section]


def _spinbox(parent, min, max):
    widget = QSpinBox(parent)
    widget.setRange(min, max)
    return widget


class ArmorPieceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QBoxLayout(QBoxLayout.TopToBottom))
        self.item_model = ArmorPieceItemModel()
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.item_model)
        self._init()

    def update_model(self, entry):
        self.item_model.update(entry)
        self.mapper.setCurrentIndex(0)

    def _init(self):
        # self._init_info()
        # self._init_basic()
        # self._init_resistance()
        # self._init_gem_slots()
        # self._init_set_skills()
        self._init_piece_skills()

    def _map(self, section, widget):
        self.mapper.addMapping(widget, section)
        return widget

    def _init_piece_skills(self):
        box = FormGroupbox("Piece Skills")
        self.layout().addWidget(box, 0)
        box += "Skill 1", self._map(AmDatEntry.skill1.index, _spinbox(box, 0, 0xffff))
        box += "Level", self._map(AmDatEntry.skill1_lvl.index, _spinbox(box, 0, 10))
        box += "Skill 2", self._map(AmDatEntry.skill2.index, _spinbox(box, 0, 0xffff))
        box += "Level", self._map(AmDatEntry.skill2_lvl.index, _spinbox(box, 0, 10))
        box += "Skill 3", self._map(AmDatEntry.skill3.index, _spinbox(box, 0, 0xffff))
        box += "Level", self._map(AmDatEntry.skill3_lvl.index, _spinbox(box, 0, 10))

    def _init_set_skills(self):
        # box = FormGroupbox("Set Skills")
        # self.layout().addWidget(box, 0)
        # view.set_skill1.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completion_enabled=True)
        # view.set_skill1_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        # view.set_skill2.ctrl = ComboBoxWidgetCtrl(Definitions.skill, completion_enabled=True)
        # view.set_skill2_lvl.ctrl = SpinBoxWidgetCtrl(0, 10)
        # box += "Skill 1", view.set_skill1.ctrl.widget
        # box += "Level", view.set_skill1_lvl.ctrl.widget
        # box += "Skill 2", view.set_skill2.ctrl.widget
        # box += "Level", view.set_skill2_lvl.ctrl.widget
        pass

    def _init_gem_slots(self):
        # box = FormGroupbox("Gem Slots")
        # self.layout().addWidget(box, 0)
        # view.num_gem_slots.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        # view.gem_slot1_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        # view.gem_slot2_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        # view.gem_slot3_lvl.ctrl = ComboBoxWidgetCtrl(Definitions.gem_slot)
        # box += "Active slots", view.num_gem_slots.ctrl.widget
        # box += "Slot 1 Level", view.gem_slot1_lvl.ctrl.widget
        # box += "Slot 2 Level", view.gem_slot2_lvl.ctrl.widget
        # box += "Slot 3 Level", view.gem_slot3_lvl.ctrl.widget
        pass

    def _init_resistance(self):
        # box = FormGroupbox("Resistance")
        # self.layout().addWidget(box, 0)
        # view.fire_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        # view.water_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        # view.thunder_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        # view.ice_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        # view.dragon_res.ctrl = SpinBoxWidgetCtrl(-127, 127)
        # box += "Fire", view.fire_res.ctrl.widget
        # box += "Water", view.water_res.ctrl.widget
        # box += "Thunder", view.thunder_res.ctrl.widget
        # box += "Ice", view.ice_res.ctrl.widget
        # box += "Dragon", view.dragon_res.ctrl.widget
        pass

    def _init_basic(self):
        # box = FormGroupbox("Basic")
        # self.layout().addWidget(box, 0)
        # view.defense.ctrl = SpinBoxWidgetCtrl(0, 0xffff)
        # view.rarity.ctrl = ComboBoxWidgetCtrl(Definitions.rarity)
        # view.cost.ctrl = SpinBoxWidgetCtrl(0, 0xffff)
        # box += "Defense", view.defense.ctrl.widget
        # box += "Rarity", view.rarity.ctrl.widget
        # box += "Cost", view.cost.ctrl.widget
        pass

    def _init_info(self):
        # box = FormGroupbox(None)
        # self.layout().addWidget(box)
        # view.set_name.ctrl = LabelWidgetCtrl(Definitions.set)
        # view.index.ctrl = LabelWidgetCtrl([])
        # view.variant.ctrl = LabelWidgetCtrl(Definitions.variant)
        # view.equip_slot.ctrl = LabelWidgetCtrl(Definitions.equip_slot)
        # view.gmd_string_index.ctrl = LabelWidgetCtrl()
        # box += "Set:", view.set_name.ctrl.widget
        # box += "Index:", view.index.ctrl.widget
        # box += "String-Index:", view.gmd_string_index.ctrl.widget
        # box += "Variant:", view.variant.ctrl.widget
        # box += "Equip Slot:", view.equip_slot.ctrl.widget
        pass


class ArmorEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.parts_model = None
        self.crafting_requirements_editor = CraftingRequirementsEditor(self)
        tab_widget = QTabWidget()
        self.armor_piece_widget = ArmorPieceWidget(self)
        tab_widget.addTab(self.armor_piece_widget, "Data")
        tab_widget.addTab(self.crafting_requirements_editor, "Crafting requirements")
        split = self.init_splitter(
            self.init_parts_tree(),
            tab_widget
        )
        self.setLayout(QStackedLayout(self))
        self.layout().addWidget(split)

    def init_splitter(self, first, second):
        split = QSplitter(Qt.Horizontal, self)
        split.addWidget(first)
        split.addWidget(second)
        split.setChildrenCollapsible(False)
        split.setSizes([250, ])
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 5)
        return split

    def init_parts_tree(self):
        self.parts_tree_view = QTreeView()
        self.parts_tree_view.activated.connect(self.handle_parts_tree_activated)
        return self.parts_tree_view

    def handle_parts_tree_activated(self, qindex: QModelIndex):
        if isinstance(qindex.internalPointer(), ArmorSetNode):
            return
        entry = qindex.internalPointer().ref
        self.armor_piece_widget.update_model(entry)
        self.crafting_requirements_editor.set_index(entry.index)

    def set_model(self, model):
        self.model = model["model"]
        self.crafting_requirements_editor.set_model(model)
        if self.model is None:
            self.parts_model = None
            self.parts_tree_view.setModel(None)
        else:
            self.parts_model = ArmorSetTreeModel(
                self.model.entries, model["translations"])
            self.parts_tree_view.setModel(self.parts_model)
            for i in range(2, self.parts_model.columnCount(None)):
                self.parts_tree_view.header().hideSection(i)


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


class ArmorEntryNode(TreeNode):
    def __init__(self, ref, parent, row):
        super().__init__(parent, row)
        self.ref = ref

    @property
    def id(self):
        return self.ref.index

    @property
    def name(self):
        return self.ref.gmd_string_index


class ArmorSetNode(TreeNode):
    def __init__(self, ref, parent, row, children):
        super().__init__(parent, row)
        self.ref = ref
        self.subnodes = [
            ArmorEntryNode(elem, self, index)
            for index, elem in enumerate(children)
        ]

    @property
    def id(self):
        return self.ref

    @property
    def name(self):
        return self.ref


class ArmorSetTreeModel(TreeModel):
    def __init__(self, entries, translations):
        self.entries = entries
        self.columns = AmDatEntry.fields()
        self.translations = translations
        super().__init__()

    def _get_root_nodes(self):
        groups = defaultdict(list)
        keys = list()
        for entry in self.entries:
            group_key = entry.set_id
            groups[group_key].append(entry)
            if group_key not in keys:
                keys.append(group_key)
        return [
            ArmorSetNode(
                key,
                None, index, groups[key])
            for index, key in enumerate(keys)
        ]

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                key = "armor" if isinstance(node, ArmorEntryNode) else "armor_series"
                return self.translations.get(key, node.name)
            elif index.column() == 1:
                return node.id
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal \
                and role == Qt.DisplayRole:
            if section == 0:
                return "Name"
            if section == 1:
                return "ID"
        return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Definitions.load()
    app = QApplication(sys.argv)
    window = ArmorEditorWindow()
    sys.exit(app.exec_())
