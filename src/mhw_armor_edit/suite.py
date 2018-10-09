# coding: utf-8
import logging
import os
import sys
from contextlib import contextmanager
from functools import partial

from PyQt5.QtCore import Qt, QSize, QSettings, QPoint
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileSystemModel,
                             QTreeView, QStyle,
                             QFileDialog, QTabWidget, QBoxLayout,
                             QWidget, QMessageBox, QDockWidget)

from mhw_armor_edit.assets import Assets
from mhw_armor_edit.editor import FilePluginRegistry
from mhw_armor_edit.models import Workspace, Translations
from mhw_armor_edit.utils import create_action

log = logging.getLogger()


@contextmanager
def show_error_dialog(parent, title="Error"):
    try:
        yield
    except Exception as e:
        QMessageBox.warning(parent, title, str(e), QMessageBox.Ok, QMessageBox.Ok)


class EditorView(QWidget):
    def __init__(self, workspace_file, child_widget, parent=None):
        super().__init__(parent)
        self.workspace_file = workspace_file
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.setLayout(layout)
        child_widget.set_model(self.workspace_file.model)
        layout.addWidget(child_widget)
        self.workspace_file.reloaded.connect(
            lambda: child_widget.set_model(self.workspace_file.model)
        )

    @classmethod
    def factory(cls, parent, workspace_file):
        plugin = FilePluginRegistry.get_plugin(workspace_file.abs_path)
        widget_inst = plugin.widget_factory()
        inst = cls(workspace_file, widget_inst, parent)
        return inst


class WorkspaceTreeView(QTreeView):
    def __init__(self, workspace, filtered=False, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.filtered = filtered
        self.setModel(QFileSystemModel())
        for i in range(1, 4):
            self.hideColumn(i)
        self.setHeaderHidden(True)
        self.workspace.rootPathChanged.connect(
            self.handle_workspace_root_path_changed)
        self.activated.connect(self.handle_tree_view_activated)

    def handle_workspace_root_path_changed(self, path):
        if not path:
            return
        model = self.model()
        model.setRootPath(path)
        self.setRootIndex(model.index(path))
        # model.setNameFilterDisables(False)
        if self.filtered:
            model.setNameFilters(
                plugin.pattern for plugin in FilePluginRegistry.registered
            )

    def handle_tree_view_activated(self, qindex):
        if self.model().isDir(qindex):
            return
        file_path = self.model().filePath(qindex)
        self.workspace.open_file(file_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translations = Translations()
        self.chunk_workspace = Workspace(
            "CHUNK", QIcon(Assets.get_asset_path("document_a4_locked.png")),
                                         self.translations, 0, parent=self)
        self.chunk_workspace.fileOpened.connect(
            partial(self.handle_workspace_file_opened, self.chunk_workspace))
        self.chunk_workspace.fileActivated.connect(self.handle_workspace_file_activated)
        self.chunk_workspace.fileClosed.connect(self.handle_workspace_file_closed)
        self.chunk_workspace.fileLoadError.connect(self.handle_workspace_file_load_error)
        self.mod_workspace = Workspace(
            "MOD", QIcon(Assets.get_asset_path("document_a4.png")),
                                       self.translations, 1, parent=self)
        self.mod_workspace.fileOpened.connect(
            partial(self.handle_workspace_file_opened, self.mod_workspace))
        self.mod_workspace.fileActivated.connect(self.handle_workspace_file_activated)
        self.mod_workspace.fileClosed.connect(self.handle_workspace_file_closed)
        self.mod_workspace.fileLoadError.connect(self.handle_workspace_file_load_error)
        self.init_actions()
        self.init_menu_bar()
        self.init_toolbar()
        self.setWindowTitle("MHW-Editor-Suite")
        self.init_file_tree(self.chunk_workspace, "Chunk directory", True)
        self.init_file_tree(self.mod_workspace, "Mod directory")
        self.setCentralWidget(self.init_editor_tabs())
        self.load_settings()

    def closeEvent(self, event):
        self.write_settings()

    def load_settings(self):
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope,
                                  "fre-sch.github.com",
                                  "MHW-Editor-Suite")
        self.settings.beginGroup("MainWindow")
        size = self.settings.value("size", QSize(1000, 800))
        position = self.settings.value("position", QPoint(300, 300))
        self.settings.endGroup()
        self.settings.beginGroup("Application")
        chunk_directory = self.settings.value("chunk_directory", None)
        self.settings.endGroup()
        self.resize(size)
        self.move(position)
        if chunk_directory:
            self.chunk_workspace.set_root_path(chunk_directory)

    def write_settings(self):
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("size", self.size())
        self.settings.setValue("position", self.pos())
        self.settings.endGroup()
        self.settings.beginGroup("Application")
        self.settings.setValue("chunk_directory", self.chunk_workspace.root_path)
        self.settings.endGroup()

    def get_icon(self, name):
        return self.style().standardIcon(name)

    def init_actions(self):
        self.open_chunk_workspace_action = create_action(
            self.get_icon(QStyle.SP_DirOpenIcon),
            "Open chunk_directory ...",
            self.handle_open_content_root_action,
            None)
        self.open_mod_workspace_action = create_action(
            self.get_icon(QStyle.SP_DirOpenIcon),
            "Open mod directory ...",
            self.handle_open_mod_workspace_action,
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
        file_menu.insertAction(None, self.open_chunk_workspace_action)
        file_menu.insertAction(None, self.open_mod_workspace_action)
        file_menu.insertAction(None, self.save_file_action)

    def init_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setFloatable(False)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.insertAction(None, self.open_mod_workspace_action)
        toolbar.insertAction(None, self.save_file_action)

    def init_file_tree(self, workspace, title, filtered=False):
        widget = WorkspaceTreeView(workspace, filtered=filtered, parent=self)
        dock = QDockWidget(title, self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetMovable)
        dock.setWidget(widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def init_editor_tabs(self):
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setDocumentMode(True)
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(
            self.handle_editor_tab_close_requested)
        return self.editor_tabs

    def handle_workspace_file_opened(self, workspace, path, rel_path):
        workspace_file = workspace.files[path]
        editor_view = EditorView.factory(self.editor_tabs, workspace_file)
        editor_view.setObjectName(path)
        self.editor_tabs.addTab(editor_view,
                                workspace.file_icon,
                                f"{workspace.name}: {rel_path}")
        self.editor_tabs.setCurrentWidget(editor_view)
        self.save_file_action.setDisabled(False)

    def handle_workspace_file_activated(self, path, rel_path):
        widget = self.editor_tabs.findChild(QWidget, path)
        self.editor_tabs.setCurrentWidget(widget)

    def handle_workspace_file_closed(self, path, rel_path):
        widget = self.editor_tabs.findChild(QWidget, path)
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
        editor_view.workspace_file.close()

    def handle_open_content_root_action(self):
        path = QFileDialog.getExistingDirectory(parent=self)
        self.chunk_workspace.set_root_path(os.path.normpath(path))

    def handle_open_mod_workspace_action(self):
        path = QFileDialog.getExistingDirectory(parent=self)
        self.mod_workspace.set_root_path(os.path.normpath(path))

    def handle_save_file_action(self):
        editor = self.editor_tabs.currentWidget()
        ws_file = editor.workspace_file
        if ws_file.workspace is self.chunk_workspace:
            if self.mod_workspace.is_valid:
                self.transfer_file_to_mod_workspace(ws_file)
            else:
                self.save_base_content_file(ws_file)
        else:
            with show_error_dialog(self, "Error writing file"):
                ws_file.save()
                log.debug(f"file {ws_file.abs_path} saved.")

    def save_base_content_file(self, ws_file):
        result = QMessageBox.question(
            self, "Save base content file?",
            "Do you really want to update this chunk file?",
            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if result == QMessageBox.Ok:
            with show_error_dialog(self, "Error writing file"):
                ws_file.save()

    def transfer_file_to_mod_workspace(self, ws_file):
        mod_abs_path, exists = self.mod_workspace.get_path(ws_file.rel_path)
        if not exists:
            self.mod_workspace.transfer_file(ws_file)
        else:
            result = QMessageBox.question(
                self,
                "File exists, overwrite?",
                f"File '{ws_file.rel_path}' already found in mod directory, overwrite?",
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            if result == QMessageBox.Ok:
                self.mod_workspace.transfer_file(ws_file)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s %(message)s")
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QMainWindow::separator:vertical,
    QSplitter::handle:horizontal {
        width: 0px;
        margin: 0 6px;
        max-height: 100px;
        border-left: 1px dotted palette(dark);
        border-right: 1px dotted palette(base);
    }
    QMainWindow::separator:horizontal,
    QSplitter::handle:vertical {
        height: 0px;
        margin: 6px 0;
        border-top: 1px dotted palette(dark);
        border-bottom: 1px dotted palette(base);
    }
    QDockWidget::title {
        padding-top: 1ex;
        background-color: palette(window);
    }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
