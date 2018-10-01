# coding: utf-8
import logging

from PyQt5.QtCore import (Qt, QAbstractTableModel, QModelIndex,
                          QSortFilterProxyModel, pyqtSignal)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QTableView, QLineEdit, QMainWindow,
                             QAction, QHeaderView)

from mhw_armor_edit.tree import log

log = logging.getLogger()


class FilterHeader(QHeaderView):
    filter_changed = pyqtSignal(int, str)

    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self._editors = []
        self.setSectionResizeMode(QHeaderView.Interactive)
        self.setSectionsClickable(True)
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
        editor_clear_action.triggered.connect(self._create_filter_changed_handler(section))
        return editor

    def _create_filter_changed_handler(self, section):
        def handler():
            self.filter_changed.emit(section, self._editors[section].text())
        return handler

    def sizeHint(self):
        size = super().sizeHint()
        if self._editors:
            height = self._editors[0].sizeHint().height()
            size.setHeight(size.height() + height)
        return size

    def updateGeometries(self):
        if self._editors:
            height = self._editors[0].sizeHint().height() + 2
            self.setViewportMargins(0, 0, 0, height)
        else:
            self.setViewportMargins(0, 0, 0, 0)
        super().updateGeometries()
        self.adjust_positions()

    def adjust_positions(self):
        for index, editor in enumerate(self._editors):
            height = editor.sizeHint().height()
            editor.move(
                self.sectionPosition(index) - self.offset() + 7,
                height + 2)
            editor.resize(self.sectionSize(index) - 4, height)

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

    def set_filter(self, section, filter_text):
        log.debug("section: %s, filter: %s", section, filter_text)
        self._proxy_model.setFilterWildcard(filter_text)
        self._proxy_model.setFilterKeyColumn(section)

    def setModel(self, model):
        self.horizontalHeader().set_filter_boxes(model.columnCount())
        self._proxy_model.setSourceModel(model)
        super().setModel(self._proxy_model)


class StructTableModel(QAbstractTableModel):
    def __init__(self, fields, entries):
        self.fields = fields
        self.entries = entries
        super().__init__()

    def update(self, entries):
        self.beginResetModel()
        self.entries = entries
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.entries)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.fields)

    def data(self, qindex, role=None):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            entry = self.entries[qindex.row()]
            field = self.fields[qindex.column()]
            return getattr(entry, field)
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
        # elif orient == Qt.Vertical:
        #     if role == Qt.DisplayRole:
        #         return section
        return None


class ExampleModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = ("ID", "Firstname", "Lastname", "Age")
        self.items = tuple(
            (i, f"firstname {i}", f"lastname {i}", 20 + i)
            for i in range(100)
        )

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.columns)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def headerData(self, section, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return self.columns[section]

    def data(self, qindex: QModelIndex, role=None):
        if role == Qt.DisplayRole:
            return self.items[qindex.row()][qindex.column()]


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TableView Example")
        self.setGeometry(300, 300, 1000, 800)
        self.model = None
        self.table_view = SortFilterTableView(self)
        self.table_model = ExampleModel(self)
        self.table_view.setModel(self.table_model)
        self.table_view.resizeColumnsToContents()
        self.table_view.resizeRowsToContents()
        self.setCentralWidget(self.table_view)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s %(message)s")
    app = QApplication(sys.argv)
    window = Example()
    window.show()
    sys.exit(app.exec_())
