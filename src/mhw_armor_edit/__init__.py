# coding: utf-8
import logging
import os
import re
import sys
from collections import namedtuple

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter,
                             QFileSystemModel, QTreeView, QAction, QStyle,
                             QFileDialog, QTabWidget, QGroupBox, QBoxLayout,
                             QWidget, QMessageBox)

from mhw_armor_edit.armor_editor import ArmorPieceWidget, ArmorEditor
from mhw_armor_edit.crafting_editor import CraftingTableEditor
from mhw_armor_edit.ftypes.eq_crt import EqCrt
from mhw_armor_edit.shell_table_editor import ShellTableEditor
from mhw_armor_edit.ftypes.am_dat import AmDat
from mhw_armor_edit.ftypes.sh_tbl import ShellTable
from mhw_armor_edit.view_ctrl import ArmorPieceViewCtrl

log = logging.getLogger(__name__)

EditorPlugin = namedtuple("EditorPlugin", (
    "regex",
    "data_factory",
    "widget_factory"
))


class FilePluginRegistry:
    registered = (
        EditorPlugin(
            re.compile(r"\.am_dat$"),
            AmDat,
            ArmorEditor,
        ),
        EditorPlugin(
            re.compile(r"\.shl_tbl$"),
            ShellTable,
            ShellTableEditor,
        ),
        EditorPlugin(
            re.compile(r"\.eq_crt$"),
            EqCrt,
            CraftingTableEditor,
        )
    )

    @classmethod
    def get_plugin(cls, path):
        for plugin in cls.registered:
            if plugin.regex.search(path):
                return plugin

    @classmethod
    def load_model(cls, path):
        plugin = cls.get_plugin(path)
        with open(path, "rb") as fp:
            return plugin.data_factory.load(fp)


def create_action(icon, title, handler, shortcut=None):
    action = QAction(icon, title)
    if shortcut is not None:
        action.setShortcut(shortcut)
    action.triggered.connect(handler)
    return action


class Workspace(QObject):
    rootPathChanged = pyqtSignal(str)
    fileOpened = pyqtSignal(str, str, int)
    fileActivated = pyqtSignal(str, str, int)
    fileClosed = pyqtSignal(str, str, int)
    fileLoadError = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_path = None
        self.files = []
        self.file_models = {}

    def get_path(self, rel_path):
        path = os.path.join(self.root_path, rel_path)
        exists = os.path.exists(rel_path)
        return path, exists

    def get_rel_path(self, abs_path):
        return os.path.relpath(abs_path, self.root_path)

    def set_root_path(self, path):
        self.root_path = path
        self.rootPathChanged.emit(self.root_path)

    def open_file(self, path):
        rel_path = self.get_rel_path(path)
        if path in self.files:
            index = self.files.index(path)
            self.fileActivated.emit(path, rel_path, index)
        else:
            self.files.append(path)
            index = self.files.index(path)
            try:
                self.file_models[path] = FilePluginRegistry.load_model(path)
                self.fileOpened.emit(path, rel_path, index)
            except Exception as e:
                self.fileLoadError.emit(path, rel_path, str(e))

    def close_file(self, path):
        index = self.files.index(path)
        self.files.remove(path)
        self.file_models.pop(path)
        self.fileClosed.emit(path, self.get_rel_path(path), index)


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
        self.setWindowTitle("Editor")
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
            self.get_icon(QStyle.SP_DialogOpenButton),
            "Open workspace ...",
            self.handle_open_workspace_action,
            QKeySequence.Open)

    def init_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.insertAction(None, self.open_workspace_action)

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

    def handle_workspace_file_opened(self, path, rel_path, index):
        log.debug("handle_workspace_file_opened(%s)", rel_path)
        data_model = self.workspace.file_models[path]
        editor_view = EditorView.factory(data_model, self.editor_tabs, path)
        editor_view.setObjectName(rel_path)
        self.editor_tabs.addTab(editor_view, rel_path)
        self.editor_tabs.setCurrentWidget(editor_view)

    def handle_workspace_file_activated(self, path, rel_path, index):
        log.debug("handle_workspace_file_activated(%s)", rel_path)
        widget = self.editor_tabs.findChild(QWidget, rel_path)
        self.editor_tabs.setCurrentWidget(widget)

    def handle_workspace_file_closed(self, path, rel_path, index):
        log.debug("handle_workspace_file_closed(%s)", rel_path)
        widget = self.editor_tabs.findChild(QWidget, rel_path)
        tab_index = self.editor_tabs.indexOf(widget)
        self.editor_tabs.removeTab(tab_index)
        # clean up widget to avoid problems adding one of its kind again later
        widget.deleteLater()

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

    def handle_open_workspace_action(self):
        path = QFileDialog.getExistingDirectory(parent=self)
        self.workspace.set_root_path(path)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s %(message)s")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
