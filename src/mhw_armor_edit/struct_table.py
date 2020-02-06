# coding: utf-8
import logging

from PyQt5.QtCore import (Qt, QAbstractTableModel, QSortFilterProxyModel,
                          pyqtSignal)
from PyQt5.QtGui import (QFont, QFontMetrics, QKeyEvent, QKeySequence)
from PyQt5.QtWidgets import (QTableView, QLineEdit, QAction, QHeaderView,
                             QTreeView, QAbstractItemView, QApplication, QMenu,
                             QStyle)

from mhw_armor_edit.import_export import (ImportExportManager)
from mhw_armor_edit.utils import create_action

log = logging.getLogger()


class FilterHeader(QHeaderView):
    filter_changed = pyqtSignal(int, str)

    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self._editors = []
        self.setSectionResizeMode(QHeaderView.Interactive)
        self.setSectionsClickable(True)
        self.setDefaultAlignment(Qt.AlignLeft)
        self.sectionResized.connect(self.adjust_positions)
        parent.horizontalScrollBar().valueChanged.connect(self.adjust_positions)

    def set_filter_boxes(self, count):
        while self._editors:
            editor = self._editors.pop()
            editor.deleteLater()
        for section in range(count):
            editor = self._create_filter_edit(section)
            self._editors.append(editor)
        self.adjust_positions()

    def _create_filter_edit(self, section):
        editor = QLineEdit(self.parent())
        editor.setClearButtonEnabled(True)
        editor.setPlaceholderText('Filter')
        editor.editingFinished.connect(self._create_filter_changed_handler(section))
        editor_clear_action = editor.findChild(QAction)
        editor_clear_action.triggered.connect(
            lambda: editor.clearFocus(),
            Qt.QueuedConnection)
        return editor

    def _create_filter_changed_handler(self, section):
        def handler():
            self.filter_changed.emit(section, self._editors[section].text())
        return handler

    def editor_height(self, pos=0):
        return self._editors[pos].sizeHint().height()

    def sizeHint(self):
        size = super().sizeHint()
        if self._editors:
            size.setHeight(size.height() + self.editor_height())
        return size

    def updateGeometries(self):
        if self._editors:
            self.setViewportMargins(0, 0, 0, self.editor_height())
        else:
            self.setViewportMargins(0, 0, 0, 0)
        super().updateGeometries()
        self.adjust_positions()

    def adjust_positions(self):
        for index, editor in enumerate(self._editors):
            header_height = super().sizeHint().height()
            editor_height = self.editor_height(index)
            xoffset = self.sectionPosition(index)
            xoffset -= self.horizontalOffset()
            try:
                xoffset += self.parent().verticalHeader().sizeHint().width()
            except AttributeError:
                pass
            editor.move(xoffset + 1, header_height + 1)
            editor.resize(self.sectionSize(index) - 1, editor_height)

    def filter_text(self, index):
        if 0 <= index < len(self._editors):
            return self._editors[index].text()
        return ''

    def set_filter_text(self, index, text):
        if 0 <= index < len(self._editors):
            self._editors[index].setText(text)

    def clear_filters(self):
        for editor in self._editors:
            editor.clear()


class SortFilterTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setDynamicSortFilter(True)
        super().setModel(self._proxy_model)
        header = FilterHeader(self)
        header.filter_changed.connect(self.set_filter)
        self.setHorizontalHeader(header)
        self.setSortingEnabled(True)
        self.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.import_export_manager = ImportExportManager(self)
        self.copy_action = create_action(
            None, "Copy", self.copy_selection_to_clipboard)

    def show_context_menu(self, point):
        self.import_export_manager.set_model_index(self.indexAt(point))
        context_menu = QMenu()
        context_menu.addAction(self.copy_action)
        context_menu.addAction(self.import_export_manager.export_action)
        context_menu.addAction(self.import_export_manager.import_action)
        context_menu.exec(self.mapToGlobal(point))

    def keyPressEvent(self, event: QKeyEvent):
        if event.type() == QKeyEvent.KeyPress \
                and event.matches(QKeySequence.Copy):
            self.copy_selection_to_clipboard()
        else:
            super().keyPressEvent(event)

    def copy_selection_to_clipboard(self):
        selected_indexes = self.selectionModel().selectedIndexes()
        if not selected_indexes or len(selected_indexes) == 0:
            return
        model = self.model()
        result = "\n".join(
            "\t".join(row)
            for row in self.selected_rows(model, selected_indexes)
        )
        cp = QApplication.clipboard()
        cp.setText(result)

    def selected_rows(self, model, selected_indexes):
        row = []
        last_row = selected_indexes[0].row()
        for current in selected_indexes:
            value = str(model.data(current, Qt.DisplayRole))
            if last_row != current.row():
                yield row
                row = [value, ]
            else:
                row.append(value)
            last_row = current.row()

    def set_filter(self, section, filter_text):
        log.debug("set_filter(section: %s, filter: %r)", section, filter_text)
        self._proxy_model.setFilterWildcard(filter_text)
        self._proxy_model.setFilterKeyColumn(section)

    def setModel(self, model):
        self.horizontalHeader().set_filter_boxes(model.columnCount())
        self._proxy_model.setSourceModel(model)
        self._proxy_model.sort(0, Qt.AscendingOrder)
        super().setModel(self._proxy_model)
        font = model.data(0, Qt.FontRole)
        if font is None:
            font = self.font()
        metrics = QFontMetrics(font)
        self.verticalHeader().setDefaultSectionSize(metrics.lineSpacing() * 1.5)
        self.horizontalHeader().setDefaultSectionSize(metrics.maxWidth() * 5)


class SortFilterTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setDynamicSortFilter(True)
        super().setModel(self._proxy_model)
        header = FilterHeader(self)
        header.filter_changed.connect(self.set_filter)
        self.setHeader(header)
        self.setSortingEnabled(True)

    def set_filter(self, section, filter_text):
        self._proxy_model.setFilterWildcard(filter_text)
        self._proxy_model.setFilterKeyColumn(section)

    def setModel(self, model):
        self.header().set_filter_boxes(model.columnCount())
        self._proxy_model.setSourceModel(model)
        self.sortByColumn(0, Qt.AscendingOrder)
        super().setModel(self._proxy_model)


class StructTableModel(QAbstractTableModel):
    def __init__(self, fields, parent=None):
        super().__init__(parent=parent)
        self.fields = fields
        self.entries = []

    def update(self, entries):
        self.beginResetModel()
        self.entries = entries
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.entries)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.fields)

    def get_field_value(self, entry, field):
        return getattr(entry, field)

    def data(self, qindex, role=None):
        if role == Qt.DisplayRole:
            entry = self.entries[qindex.row()]
            field = self.fields[qindex.column()]
            return self.get_field_value(entry, field)
        elif role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            field = self.fields[qindex.column()]
            return getattr(entry, field)
        elif role == Qt.UserRole:
            return self.entries[qindex.row()]
        elif role == Qt.FontRole:
            font = QFont()
            font.setFamily("Consolas")
            return font
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        return None

    def setData(self, qindex, value, role=None):
        if role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            field = self.fields[qindex.column()]
            try:
                setattr(entry, field, int(value))
                self.dataChanged.emit(qindex, qindex)
                return True
            except Exception as e:
                log.exception("error setting value")
        return False

    def flags(self, qindex):
        return super().flags(qindex) | Qt.ItemIsEditable

    def headerData(self, section, orient, role=None):
        if orient == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.fields[section]
        elif orient == Qt.Vertical:
            if role == Qt.DisplayRole:
                return section
        return None

    def find(self, **attrs):
        if not self.entries:
            yield None
            return
        for item in self.entries:
            attrs_match = all(
                getattr(item, key, None) == value
                for key, value in attrs.items()
            )
            if attrs_match:
                yield item

    def find_first(self, **attrs):
        for result in self.find(**attrs):
            return result

    def index_of(self, **attrs):
        if not self.entries:
            yield None
            return
        for i, item in enumerate(self.entries):
            attrs_match = all(
                getattr(item, key, None) == value
                for key, value in attrs.items()
            )
            if attrs_match:
                yield i

    def index_of_first(self, **attrs):
        for result in self.index_of(**attrs):
            return result
