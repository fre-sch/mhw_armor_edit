# coding: utf-8
import logging
from collections import namedtuple
from functools import partial, partialmethod

from PyQt5.QtCore import pyqtSignal, QObject, Qt, QRectF, pyqtProperty
from PyQt5.QtGui import (QPaintEvent, QPainter, QColor, QLinearGradient,
                         QPainterPath)
from PyQt5.QtWidgets import (QWidget, QMainWindow, QSlider, QFormLayout)

from mhw_armor_edit.ftypes.kire import KireEntry

log = logging.getLogger(__name__)

KireGaugeColors = namedtuple("KireGaugeColors", (
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "white",
    "purple",
))


class KireGaugeModel(QObject):
    changed = pyqtSignal()
    MAX_VALUE = 500

    def __init__(self, red=0, orange=0, yellow=0, green=0, blue=0, white=0,
                 purple=0, parent=None):
        super().__init__(parent)
        self.red = red
        self.orange = orange
        self.yellow = yellow
        self.green = green
        self.blue = blue
        self.white = white
        self.purple = purple

    def set_value(self, color_attr, value):
        setattr(self, color_attr, value)
        self.changed.emit()

    def get_value(self, color_attr):
        return getattr(self, color_attr, 0)

    def get_percent(self, color_attr):
        return self.get_value(color_attr) / self.MAX_VALUE

    def set_red(self, value):
        """setter for signal binding"""
        self.set_value("red", value)

    def set_orange(self, value):
        """setter for signal binding"""
        self.set_value("orange", value)

    def set_yellow(self, value):
        """setter for signal binding"""
        self.set_value("yellow", value)

    def set_green(self, value):
        """setter for signal binding"""
        self.set_value("green", value)

    def set_blue(self, value):
        """setter for signal binding"""
        self.set_value("blue", value)

    def set_white(self, value):
        """setter for signal binding"""
        self.set_value("white", value)

    def set_purple(self, value):
        """setter for signal binding"""
        self.set_value("purple", value)


class KireGaugeModelEntryAdapter(KireGaugeModel):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entry = None

    def set_entry(self, entry):
        self.entry = entry
        self.changed.emit()

    def set_value(self, color_attr, value):
        setattr(self.entry, color_attr, value)
        self.changed.emit()

    def get_value(self, color_attr):
        return getattr(self.entry, color_attr, 0)


def _gradient(height, color1, color2):
    grad = QLinearGradient(0, 0, 0, height)
    grad.setColorAt(0.0, color1)
    grad.setColorAt(1.0, color2)
    return grad


def _rounded_rect_clip(rect, roundness):
    cp = QPainterPath()
    cp.addRoundedRect(QRectF(rect), roundness, roundness)
    return cp


class KireGauge(QWidget):
    MARGIN = 2
    colors = KireGaugeColors(
        QColor(220, 60, 60),
        QColor(220, 180, 60),
        QColor(220, 220, 60),
        QColor(60, 220, 60),
        QColor(60, 80, 220),
        QColor(240, 240, 240),
        QColor(140, 60, 220)
    )
    bg_dark = QColor(40, 40, 40)
    bg_light = QColor(80, 80, 80)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 24)
        self.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.model: KireGaugeModel = None

    def handle_model_updated(self):
        self.repaint()

    def set_model(self, model):
        if self.model:
            self.model.changed.disconnect(self.handle_model_updated)
        self.model = model
        self.model.changed.connect(self.handle_model_updated)

    def paintEvent(self, paint_event: QPaintEvent):
        super().paintEvent(paint_event)
        p = QPainter()
        p.begin(self)
        self.draw(p)
        p.end()

    def draw(self, p: QPainter):
        p.setRenderHint(QPainter.Antialiasing)
        crect = self.contentsRect()
        p.setClipPath(_rounded_rect_clip(self.rect(), self.MARGIN * 2))
        p.fillRect(self.rect(),
                   _gradient(self.height(), self.bg_dark, self.bg_light))
        if self.model is None:
            return
        for attr in reversed(KireGaugeColors._fields):
            value = self.model.get_percent(attr)
            if value == 0:
                continue
            color = getattr(self.colors, attr)
            p.setClipPath(_rounded_rect_clip(crect, self.MARGIN))
            p.fillRect(crect.x(), crect.y(),
                       crect.width() * value, crect.height(),
                       _gradient(crect.height(), color.lighter(), color))


class KireWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout(self)
        self.setLayout(layout)
        self.gauge = KireGauge(self)
        self.connections = {}
        layout.addRow("Gauge", self.gauge)
        for color_attr in KireGaugeColors._fields:
            slider = QSlider(self)
            slider.setProperty("color", color_attr)
            slider.setOrientation(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(500)
            slider.setTickInterval(50)
            slider.setTickPosition(QSlider.TicksBelow)
            layout.addRow(color_attr.capitalize(), slider)

    @pyqtProperty(KireEntry, user=True)
    def value(self):
        """pyqtProperty for data widget mapper bindings"""
        try:
            return self.gauge.model.entry
        except AttributeError:
            return None

    @value.setter
    def value(self, value):
        """pyqtProperty for data widget mapper bindings"""
        self.gauge.model.set_entry(value)
        for slider in self.findChildren(QSlider):
            color_attr = slider.property("color")
            slider.setValue(self.gauge.model.get_value(color_attr))

    def set_model(self, model):
        self.gauge.set_model(model)
        for slider in self.findChildren(QSlider):
            color_attr = slider.property("color")
            value_setter = getattr(model, f"set_{color_attr}")
            if self.connections.get(color_attr):
                slider.valueChanged.disconnect(self.connections[color_attr])
            self.connections[color_attr] = \
                slider.valueChanged.connect(value_setter)
            slider.setValue(model.get_value(color_attr))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 300, 50)
        self.setWindowTitle("Kire Widget Test")
        kire_widget = KireWidget(self)
        kire_widget.set_model(KireGaugeModel(
            200, 250, 300, 350, 400, 450, 500
        ))
        self.setCentralWidget(kire_widget)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
