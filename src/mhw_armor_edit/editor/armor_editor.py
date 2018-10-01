# -*- coding: utf-8 -*-
import logging
from collections.__init__ import defaultdict

from PyQt5.QtCore import (Qt, QModelIndex, QAbstractTableModel)
from PyQt5.QtWidgets import (QSplitter, QBoxLayout, QWidget, QTreeView,
                             QTabWidget, QStackedLayout,
                             QDataWidgetMapper, QSpinBox, QLabel, QComboBox,
                             QHeaderView)

from mhw_armor_edit.editor.crafting_editor import CraftingRequirementsEditor
from mhw_armor_edit.ftypes.am_dat import AmDatEntry
from mhw_armor_edit.tree import TreeModel, TreeNode
from mhw_armor_edit.utils import FormGroupbox, ItemDelegate

log = logging.getLogger()

#
# class FileModel:
#     def __init__(self, path, data):
#         self.path = path
#         self.data = data
#
#     def save(self):
#         with open(self.path, "wb") as fp:
#             fp.write(self.data.data)
#
#     @classmethod
#     def load(cls, path):
#         with open(path, "rb") as fp:
#             data = AmDat.load(fp)
#         return cls(path, data)


class SkillItemModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = tuple()

    def update(self, gmd):
        self.beginResetModel()
        if not gmd:
            self.items = []
        else:
            self.items = [
                (i // 3, gmd.string_table[i])
                for i in range(0, len(gmd.string_table), 3)
            ]
            self.items[0] = (0, "---")
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, qindex: QModelIndex, role=None):
        if not qindex.isValid():
            return None
        entry = self.items[qindex.row()]
        if qindex.column() == 0:
            if role == Qt.EditRole or role == Qt.DisplayRole:
                return entry[1]
            elif role == Qt.UserRole:
                return entry[0]
        return None


class ArmorPieceItemModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fields = AmDatEntry.fields()
        self.entry = None
        self.translations = None

    def update(self, entry, translations):
        self.beginResetModel()
        self.entry = entry
        self.translations = translations
        self.endResetModel()

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.fields)

    def rowCount(self, parent=None, *args, **kwargs):
        return 1

    def data(self, qindex: QModelIndex, role=None):
        attr = self.fields[qindex.column()]
        value = getattr(self.entry, attr)
        if role == Qt.DisplayRole or Qt.EditRole:
            if attr in ("gmd_name_index", "gmd_desc_index"):
                return self.translations.get("armor", value)
            return value

    def setData(self, qindex: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            try:
                attr = self.fields[qindex.column()]
                setattr(self.entry, attr, int(value))
                self.dataChanged.emit(qindex, qindex)
                return True
            except ValueError:
                log.debug("error setting attr")
        return False

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
        self.setContentsMargins(0, 0, 0, 0)
        self.skill_model = SkillItemModel()
        self.item_model = ArmorPieceItemModel()
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setItemDelegate(ItemDelegate())
        self.mapper.setModel(self.item_model)
        self._init()

    def update_model(self, entry, translations):
        self.translations = translations
        self.item_model.update(entry, translations)
        self.skill_model.update(self.translations.get_table("skill_pt"))
        self.mapper.setCurrentIndex(0)

    def _init(self):
        self._init_info()
        self._init_basic()
        self._init_resistance()
        self._init_gem_slots()
        self._init_set_skills()
        self._init_piece_skills()

    def _map(self, section, widget, property_name=None):
        if property_name is None:
            self.mapper.addMapping(widget, section)
        else:
            self.mapper.addMapping(widget, section, property_name.encode("UTF-8"))
        if isinstance(widget, QComboBox):
            widget.activated.connect(self.mapper.submit)
        return widget

    def _skill_combo_box(self):
        widget = QComboBox(self)
        widget.setModel(self.skill_model)
        widget.setEditable(True)
        return widget

    def _init_piece_skills(self):
        box = FormGroupbox("Piece Skills")
        self.layout().addWidget(box, 1)
        box += "Skill 1", self._map(AmDatEntry.skill1.index, self._skill_combo_box())
        box += "Level", self._map(AmDatEntry.skill1_lvl.index, _spinbox(box, 0, 10))
        box += "Skill 2", self._map(AmDatEntry.skill2.index, self._skill_combo_box())
        box += "Level", self._map(AmDatEntry.skill2_lvl.index, _spinbox(box, 0, 10))
        box += "Skill 3", self._map(AmDatEntry.skill3.index, self._skill_combo_box())
        box += "Level", self._map(AmDatEntry.skill3_lvl.index, _spinbox(box, 0, 10))

    def _init_set_skills(self):
        box = FormGroupbox("Set Skills")
        self.layout().addWidget(box, 0)
        box += "Skill 1", self._map(AmDatEntry.set_skill1.index, self._skill_combo_box())
        box += "Level", self._map(AmDatEntry.set_skill1_lvl.index, _spinbox(box, 0, 10))
        box += "Skill 2", self._map(AmDatEntry.set_skill2.index, self._skill_combo_box())
        box += "Level", self._map(AmDatEntry.set_skill2_lvl.index, _spinbox(box, 0, 10))
        pass

    def _init_gem_slots(self):
        box = FormGroupbox("Gem Slots")
        self.layout().addWidget(box, 0)
        box += "Active slots", self._map(AmDatEntry.num_gem_slots.index, _spinbox(box, 0, 3))
        box += "Slot 1 Level", self._map(AmDatEntry.gem_slot1_lvl.index, _spinbox(box, 0, 3))
        box += "Slot 2 Level", self._map(AmDatEntry.gem_slot2_lvl.index, _spinbox(box, 0, 3))
        box += "Slot 3 Level", self._map(AmDatEntry.gem_slot3_lvl.index, _spinbox(box, 0, 3))

    def _init_resistance(self):
        box = FormGroupbox("Resistance")
        self.layout().addWidget(box, 0)
        box += "Fire", self._map(AmDatEntry.fire_res.index, _spinbox(box, -127, 127))
        box += "Water", self._map(AmDatEntry.water_res.index, _spinbox(box, -127, 127))
        box += "Thunder", self._map(AmDatEntry.thunder_res.index, _spinbox(box, -127, 127))
        box += "Ice", self._map(AmDatEntry.ice_res.index, _spinbox(box, -127, 127))
        box += "Dragon", self._map(AmDatEntry.dragon_res.index, _spinbox(box, -127, 127))

    def _init_basic(self):
        box = FormGroupbox("Basic")
        self.layout().addWidget(box, 0)
        box += "Defense", self._map(AmDatEntry.defense.index, _spinbox(box, 0, 0xffff))
        box += "Rarity", self._map(AmDatEntry.rarity.index, _spinbox(box, 0, 7))
        box += "Cost", self._map(AmDatEntry.cost.index, _spinbox(box, 0, 0xffff))

    def _init_info(self):
        box = FormGroupbox("Info")
        self.layout().addWidget(box, 0)
        box += "Index:", self._map(AmDatEntry.index.index, QLabel("", parent=box), "text")
        box += "Set-ID:", self._map(AmDatEntry.set_id.index, QLabel("", parent=box), "text")
        box += "Name:", self._map(AmDatEntry.gmd_name_index.index, QLabel("", parent=box), "text")
        box += "Description:", self._map(AmDatEntry.gmd_desc_index.index, QLabel("", parent=box), "text")
        box += "Variant:", self._map(AmDatEntry.variant.index, QLabel("", parent=box), "text")
        box += "Equip-Slot:", self._map(AmDatEntry.equip_slot.index, QLabel("", parent=box), "text")


class ArmorEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.translations = None
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
        self.armor_piece_widget.update_model(entry, self.translations)
        self.crafting_requirements_editor.set_index(entry.index)

    def set_model(self, model):
        self.model = model["model"]
        self.translations = model["translations"]
        self.crafting_requirements_editor.set_model(model)
        if self.model is None:
            self.parts_model = None
            self.parts_tree_view.setModel(None)
        else:
            self.parts_model = ArmorSetTreeModel(
                self.model.entries, self.translations)
            self.parts_tree_view.setModel(self.parts_model)
            self.parts_tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
            self.parts_tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.parts_tree_view.header().setStretchLastSection(False)
            for i in range(2, self.parts_model.columnCount(None)):
                self.parts_tree_view.header().hideSection(i)


# class ArmorEditorWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.file_model = None
#         self.current_piece_view_ctrl = ArmorPieceViewCtrl()
#         self.init_actions()
#         self.init_toolbar()
#         self.init_menubar()
#         self.init_ui()
#         self.current_piece_view_ctrl.update(None)
#
#     def get_icon(self, name):
#         return self.style().standardIcon(name)
#
#     def init_actions(self):
#         self.open_file_action = create_action(
#             self.get_icon(QStyle.SP_DialogOpenButton),
#             "Open file ...",
#             self.handle_open_file_action,
#             QKeySequence.Open)
#         self.save_file_action = create_action(
#             self.get_icon(QStyle.SP_DialogSaveButton),
#             "Save ...",
#             self.handle_save_file_action,
#             QKeySequence.Save)
#         self.save_file_as_action = create_action(
#             self.get_icon(QStyle.SP_DialogSaveButton),
#             "Save as ...",
#             self.handle_save_file_as_action,
#             QKeySequence.SaveAs)
#         self.export_csv_action = create_action(
#             self.get_icon(QStyle.SP_FileIcon),
#             "Export CSV...",
#             self.handle_export_csv_action,
#             None)
#         self.close_file_action = create_action(
#             self.get_icon(QStyle.SP_DialogCloseButton),
#             "Close file",
#             self.handle_close_file_action,
#             QKeySequence(Qt.CTRL + Qt.Key_W))
#
#     def init_menubar(self):
#         menubar = self.menuBar()
#         file_menu = menubar.addMenu("File")
#         file_menu.insertAction(None, self.open_file_action)
#         file_menu.insertAction(None, self.save_file_action)
#         file_menu.insertAction(None, self.save_file_as_action)
#         file_menu.addSeparator()
#         file_menu.insertAction(None, self.export_csv_action)
#         file_menu.addSeparator()
#         file_menu.insertAction(None, self.close_file_action)
#
#     def init_ui(self):
#         self.armor_editor = ArmorEditor(self)
#         self.setCentralWidget(self.armor_editor)
#         self.setGeometry(300, 300, 600, 400)
#         self.setWindowTitle('Armor Editor')
#         self.show()
#
#     def init_toolbar(self):
#         toolbar = self.addToolBar("Main")
#         toolbar.insertAction(None, self.open_file_action)
#         toolbar.insertAction(None, self.save_file_action)
#         toolbar.insertAction(None, self.close_file_action)
#
#     def handle_open_file_action(self):
#         file_path, _ = QFileDialog.getOpenFileName(parent=self)
#         if file_path:
#             self.handle_file_selected(file_path)
#
#     def handle_save_file_action(self):
#         if self.file_model is None:
#             return
#         try:
#             self.file_model.save()
#         except Exception as e:
#             QMessageBox.warning(self,
#                                 "Error writing file", str(e),
#                                 QMessageBox.Ok, QMessageBox.Ok)
#
#     def handle_save_file_as_action(self):
#         if self.file_model is None:
#             return
#         file_path, _ = QFileDialog.getSaveFileName(self)
#         if file_path:
#             self.file_model.path = file_path
#             self.handle_save_file_action()
#
#     def handle_export_csv_action(self):
#         if self.file_model is None:
#             return
#         file_path, _ = QFileDialog.getSaveFileName(self)
#         if file_path:
#             with open(file_path, "w") as fp:
#                 writer = csv.DictWriter(fp, AmDatEntry.fields(),
#                                         delimiter=";", quotechar='"',
#                                         doublequote=False, escapechar='"',
#                                         lineterminator="\n")
#                 writer.writeheader()
#                 writer.writerows(entry.as_dict() for entry in self.file_model.data)
#
#     def handle_close_file_action(self):
#         self.armor_editor.set_model(None)
#         self.file_model = None
#
#     def handle_file_selected(self, file_path):
#         try:
#             self.file_model = FileModel.load(file_path)
#         except Exception as e:
#             self.file_model = None
#             QMessageBox.warning(self,
#                                 "Error opening file", str(e),
#                                 QMessageBox.Ok, QMessageBox.Ok)
#             return
#         self.armor_editor.set_model(self.file_model.data)


class ArmorEntryNode(TreeNode):
    def __init__(self, ref, parent, row):
        super().__init__(parent, row)
        self.ref = ref

    @property
    def id(self):
        return self.ref.index

    @property
    def name(self):
        return self.ref.gmd_name_index


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


# if __name__ == '__main__':
#     logging.basicConfig(level=logging.DEBUG)
#     Definitions.load()
#     app = QApplication(sys.argv)
#     window = ArmorEditorWindow()
#     sys.exit(app.exec_())
