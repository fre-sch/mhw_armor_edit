# coding: utf-8
import logging
import os
import sys
from collections import namedtuple
from fnmatch import fnmatch

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QSize
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter,
                             QFileSystemModel, QTreeView, QStyle,
                             QFileDialog, QTabWidget, QBoxLayout,
                             QWidget, QMessageBox)

from mhw_armor_edit.editor.armor_editor import ArmorEditor
from mhw_armor_edit.editor.crafting_editor import (CraftingTableEditor)
from mhw_armor_edit.editor.gmd_editor import GmdTableEditor
from mhw_armor_edit.editor.itm_editor import ItmTableEditor
from mhw_armor_edit.editor.shell_table_editor import ShellTableEditor
from mhw_armor_edit.editor.weapon_gun_editor import WpDatGEditor
from mhw_armor_edit.ftypes.am_dat import AmDat
from mhw_armor_edit.ftypes.eq_crt import EqCrt
from mhw_armor_edit.ftypes.gmd import Gmd
from mhw_armor_edit.ftypes.itm import Itm
from mhw_armor_edit.ftypes.sh_tbl import ShellTable
from mhw_armor_edit.ftypes.wp_dat_g import WpDatG
from mhw_armor_edit.utils import create_action

log = logging.getLogger()

EditorPlugin = namedtuple("EditorPlugin", (
    "pattern",
    "data_factory",
    "widget_factory"
))

Relations = {
    r"common\equip\armor.am_dat": {
        "crafting": r"common\equip\armor.eq_crt",
    }
}


class FilePluginRegistry:
    registered = (
        EditorPlugin(
            "*.am_dat",
            AmDat,
            ArmorEditor,
        ),
        EditorPlugin(
            "*.shl_tbl",
            ShellTable,
            ShellTableEditor,
        ),
        EditorPlugin(
            "*.eq_crt",
            EqCrt,
            CraftingTableEditor,
        ),
        EditorPlugin(
            "*.gmd",
            Gmd,
            GmdTableEditor,
        ),
        EditorPlugin(
            "*.itm",
            Itm,
            ItmTableEditor,
        ),
        EditorPlugin(
            "*.wp_dat_g",
            WpDatG,
            WpDatGEditor,
        )
    )

    @classmethod
    def get_plugin(cls, path):
        for plugin in cls.registered:
            if fnmatch(path, plugin.pattern):
                return plugin

    @classmethod
    def load_model(cls, workspace, path, rel_path, is_relation=False):
        plugin = cls.get_plugin(path)
        model = {}
        with open(path, "rb") as fp:
            model["model"] = plugin.data_factory.load(fp)
        if not is_relation:
            model.update(cls._load_relations(rel_path, workspace))
        return model

    @classmethod
    def _load_relations(cls, rpath, workspace):
        rel_models = {}
        relations = Relations.get(rpath)
        if not relations:
            return rel_models
        for key, relation_rpath in relations.items():
            relation_path, exists = workspace.get_path(relation_rpath)
            if not exists:
                rel_models[key] = None
            else:
                rel_model = cls.load_model(
                    workspace, relation_path, relation_rpath, True)
                rel_models[key] = rel_model["model"]
        return rel_models


class Translations:
    Tables = {
        "armor": r"common\text\steam\armor_eng.gmd",
        "armor_series": r"common\text\steam\armor_series_eng.gmd",
        "item": r"common\text\steam\item_eng.gmd",
        "skill": r"common\text\vfont\skill_eng.gmd",
        "skill_pt": r"common\text\vfont\skill_pt_eng.gmd",
        "lbg": r"common\text\steam\lbg_eng.gmd",
    }

    def __init__(self):
        self.tables = {}

    def load(self, workspace):
        for key, rpath in self.Tables.items():
            self._load_table(workspace, key, rpath)

    def _load_table(self, workspace, key, rpath):
        abs_path, exists = workspace.get_path(rpath)
        if not exists:
            log.debug("translation file %s not found", abs_path)
            return
        with open(abs_path, "rb") as fp:
            try:
                self.tables[key] = Gmd.load(fp)
                log.debug("translation file %s loaded", abs_path)
            except Exception as e:
                log.exception("failed loading translation file  %s", abs_path)

    def get(self, table_name, index):
        table = self.tables.get(table_name)
        if not table:
            return f"{table_name}{index}"
        return table.get_string(index, f"{table_name}{index}")

    def get_table(self, name):
        return self.tables.get(name)


class Workspace(QObject):
    rootPathChanged = pyqtSignal(str)
    fileOpened = pyqtSignal(str, str)
    fileActivated = pyqtSignal(str, str)
    fileClosed = pyqtSignal(str, str)
    fileLoadError = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_path = None
        self.files = []
        self.file_models = {}
        self.translations = Translations()

    def get_path(self, rel_path):
        path = os.path.join(self.root_path, rel_path)
        exists = os.path.exists(path)
        return path, exists

    def get_rel_path(self, abs_path):
        return os.path.relpath(abs_path, self.root_path)

    def set_root_path(self, path):
        self.root_path = path
        self.translations.load(self)
        self.rootPathChanged.emit(self.root_path)

    def open_file(self, path):
        rel_path = self.get_rel_path(path)
        if path in self.files:
            self.fileActivated.emit(path, rel_path)
        else:
            try:
                model = FilePluginRegistry.load_model(self, path, rel_path)
                model["translations"] = self.translations
                self.file_models[path] = model
                self.files.append(path)
                self.fileOpened.emit(path, rel_path)
            except Exception as e:
                log.exception("error loading path: %s", path)
                self.fileLoadError.emit(path, rel_path, str(e))

    def close_file(self, path):
        self.files.remove(path)
        self.file_models.pop(path)
        self.fileClosed.emit(path, self.get_rel_path(path))

    def save_file(self, path):
        with open(path, "wb") as fp:
            self.file_models[path]["model"].save(fp)


class EditorView(QWidget):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setLayout(QBoxLayout(QBoxLayout.TopToBottom))

    @classmethod
    def factory(cls, data_model, parent, path):
        plugin = FilePluginRegistry.get_plugin(path)
        widget_inst = plugin.widget_factory()
        inst = cls(path, parent)
        inst.layout().addWidget(widget_inst)
        widget_inst.set_model(data_model)
        return inst


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.workspace = Workspace(self)
        self.workspace.rootPathChanged.connect(
            self.handle_workspace_root_path_changed)
        self.workspace.fileOpened.connect(
            self.handle_workspace_file_opened)
        self.workspace.fileActivated.connect(
            self.handle_workspace_file_activated)
        self.workspace.fileClosed.connect(
            self.handle_workspace_file_closed)
        self.workspace.fileLoadError.connect(
            self.handle_workspace_file_load_error)
        self.init_actions()
        self.init_menu_bar()
        self.init_toolbar()
        self.setWindowTitle("MHW Content Suite")
        self.setGeometry(300, 300, 1000, 800)
        split = QSplitter(Qt.Horizontal, self)
        split.setChildrenCollapsible(False)
        split.addWidget(self.init_file_tree())
        split.addWidget(self.init_editor_tabs())
        split.setSizes([250, ])
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        self.setCentralWidget(split)

    def get_icon(self, name):
        return self.style().standardIcon(name)

    def init_actions(self):
        self.open_workspace_action = create_action(
            self.get_icon(QStyle.SP_DirOpenIcon),
            "Open workspace ...",
            self.handle_open_workspace_action,
            QKeySequence.Open)
        self.save_file_action = create_action(
            self.get_icon(QStyle.SP_DriveHDIcon),
            "Save file",
            self.handle_save_file_action,
            QKeySequence.Save)
        self.save_file_action.setDisabled(True)

    def init_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.insertAction(None, self.save_file_action)
        file_menu.addSeparator()
        file_menu.insertAction(None, self.open_workspace_action)

    def init_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setFloatable(False)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.insertAction(None, self.open_workspace_action)
        toolbar.insertAction(None, self.save_file_action)

    def init_file_tree(self):
        self.file_system_model = QFileSystemModel()
        self.file_tree_view = QTreeView(self)
        self.file_tree_view.setObjectName("file_tree_view")
        self.file_tree_view.setStyleSheet("QTreeView#file_tree_view {margin:2ex}")
        self.file_tree_view.activated.connect(self.handle_file_tree_view_activated)
        self.file_tree_view.setModel(self.file_system_model)
        self.file_tree_view.hideColumn(1)
        self.file_tree_view.hideColumn(2)
        self.file_tree_view.hideColumn(3)
        self.file_tree_view.setHeaderHidden(True)
        return self.file_tree_view

    def init_editor_tabs(self):
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setDocumentMode(True)
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(
            self.handle_editor_tab_close_requested)
        return self.editor_tabs

    def handle_file_tree_view_activated(self, qindex):
        if self.file_system_model.isDir(qindex):
            return
        file_path = self.file_system_model.filePath(qindex)
        self.workspace.open_file(file_path)

    def handle_workspace_file_opened(self, path, rel_path):
        data_model = self.workspace.file_models[path]
        editor_view = EditorView.factory(data_model, self.editor_tabs, path)
        editor_view.setObjectName(rel_path)
        self.editor_tabs.addTab(editor_view, rel_path)
        self.editor_tabs.setCurrentWidget(editor_view)
        self.save_file_action.setDisabled(False)

    def handle_workspace_file_activated(self, path, rel_path):
        widget = self.editor_tabs.findChild(QWidget, rel_path)
        self.editor_tabs.setCurrentWidget(widget)

    def handle_workspace_file_closed(self, path, rel_path):
        widget = self.editor_tabs.findChild(QWidget, rel_path)
        tab_index = self.editor_tabs.indexOf(widget)
        self.editor_tabs.removeTab(tab_index)
        # clean up widget to avoid problems adding one of its kind again later
        widget.deleteLater()
        self.save_file_action.setDisabled(len(self.workspace.files) == 0)

    def handle_workspace_file_load_error(self, path, rel_path, error):
        QMessageBox.warning(self, f"Error loading file `{rel_path}`",
                            f"Error while loading\n{path}:\n\n{error}",
                            QMessageBox.Ok, QMessageBox.Ok)

    def handle_editor_tab_close_requested(self, tab_index):
        editor_view = self.editor_tabs.widget(tab_index)
        self.workspace.close_file(editor_view.path)

    def handle_workspace_root_path_changed(self, path):
        if path:
            self.file_system_model.setRootPath(path)
            self.file_tree_view.setRootIndex(self.file_system_model.index(path))
            self.file_system_model.setNameFilterDisables(False)
            self.file_system_model.setNameFilters(
                plugin.pattern for plugin in FilePluginRegistry.registered
            )

    def handle_open_workspace_action(self):
        path = QFileDialog.getExistingDirectory(parent=self)
        self.workspace.set_root_path(os.path.normpath(path))

    def handle_save_file_action(self):
        editor = self.editor_tabs.currentWidget()
        try:
            self.workspace.save_file(editor.path)
            log.debug(f"file {editor.path} saved.")
        except Exception as e:
            QMessageBox.warning(self,
                                "Error writing file", str(e),
                                QMessageBox.Ok, QMessageBox.Ok)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s %(message)s")
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QSplitter::handle:horizontal {
        background-color: palette(midlight);
    }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
