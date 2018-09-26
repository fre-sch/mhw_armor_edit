# coding: utf-8
import logging
from contextlib import contextmanager
from typing import Sequence

import attr
from PyQt5.QtWidgets import QComboBox, QSpinBox, QLabel

log = logging.getLogger(__name__)


@contextmanager
def block_widget_signals(widget):
    try:
        widget.blockSignals(True)
        yield
    finally:
        widget.blockSignals(False)


class WidgetCtrl:
    def __init__(self):
        self.widget = self.create_widget()

    def set_disabled(self, value):
        self.widget.setDisabled(value)

    def set_value(self, value):
        raise NotImplementedError()

    def get_value(self):
        raise NotImplementedError()

    def create_widget(self):
        raise NotImplementedError()

    def connect(self, value_setter):
        raise NotImplementedError()


class ComboBoxWidgetCtrl(WidgetCtrl):
    def __init__(self, items: Sequence, completion_enabled=False):
        self.items = items
        self.completion_enabled = completion_enabled
        super().__init__()

    def set_value(self, value):
        with block_widget_signals(self.widget):
            index = self.get_index(value)
            if index is None:  # custom value not in items
                self.widget.setCurrentText(str(value))
            else:
                self.widget.setCurrentIndex(index)

    def get_index(self, value):
        for i, it in enumerate(self.items):
            if it["value"] == value:
                return i

    def get_value(self):
        return self.widget.currentData()

    def create_widget(self):
        self.widget = QComboBox()
        for item in self.items:
            self.widget.addItem(item["name"], item["value"])
        self.widget.setEditable(self.completion_enabled)
        return self.widget

    def connect(self, value_setter):
        self.widget.currentIndexChanged.connect(
            self.handle_current_index_changed(value_setter))
        self.widget.editTextChanged.connect(
            self.handle_edit_text_changed(value_setter))

    def handle_current_index_changed(self, value_setter):
        def inner(index):
            log.debug("currentIndexChanged: %s", index)
            value_setter(self.get_value())
        return inner

    def handle_edit_text_changed(self, value_setter):
        def inner(text):
            log.debug("editTextChanged: %s", text)
            try:
                value_setter(int(text))
            except ValueError:
                pass
        return inner


class SpinBoxWidgetCtrl(WidgetCtrl):
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
        super().__init__()

    def set_value(self, value):
        with block_widget_signals(self.widget):
            self.widget.setValue(value)

    def get_value(self):
        return self.widget.value()

    def create_widget(self):
        widget = QSpinBox()
        widget.setRange(self.minimum, self.maximum)
        return widget

    def connect(self, value_setter):
        self.widget.valueChanged.connect(
            lambda value: value_setter(value)
        )


class LabelWidgetCtrl(WidgetCtrl):
    def __init__(self, items=None):
        self.items = {it["value"]: it["name"] for it in items} if items else None
        super().__init__()

    def set_value(self, value):
        with block_widget_signals(self.widget):
            text = self.get_text(value)
            self.widget.setText(text)

    def get_text(self, value):
        if self.items is None:
            return str(value)
        try:
            return self.items[value]
        except KeyError:
            return repr(value)

    def get_value(self):
        return self.widget.text()

    def create_widget(self):
        return QLabel()

    def connect(self, value_setter):
        pass


class ViewAttrCtrl:
    def __init__(self, model_attr):
        self.model = None
        self.attr = model_attr
        self._ctrl = None

    def update(self, model):
        self.model = model
        self.set_ctrl_value()

    def set_ctrl_value(self):
        if self._ctrl is None:
            return
        self._ctrl.set_disabled(self.model is None)
        if self.model is None:
            return
        value = getattr(self.model, self.attr, None)
        self._ctrl.set_value(value)

    def set_model_value(self, value):
        if self.model is None:
            return
        setattr(self.model, self.attr, value)

    @property
    def ctrl(self):
        return self._ctrl

    @ctrl.setter
    def ctrl(self, ctrl):
        self._ctrl = ctrl
        self._ctrl.connect(self.set_model_value)


@attr.s
class ArmorPieceViewCtrl:
    set_name = attr.ib(ViewAttrCtrl("set_id"))
    set_id = attr.ib(ViewAttrCtrl("set_id"))
    index = attr.ib(ViewAttrCtrl("index"))
    main_id = attr.ib(ViewAttrCtrl("main_id"))
    secondary_id = attr.ib(ViewAttrCtrl("secondary_id"))
    variant = attr.ib(ViewAttrCtrl("variant"))
    equip_slot = attr.ib(ViewAttrCtrl("equip_slot"))
    defense = attr.ib(ViewAttrCtrl("defense"))
    rarity = attr.ib(ViewAttrCtrl("rarity"))
    cost = attr.ib(ViewAttrCtrl("cost"))
    fire_res = attr.ib(ViewAttrCtrl("fire_res"))
    water_res = attr.ib(ViewAttrCtrl("water_res"))
    ice_res = attr.ib(ViewAttrCtrl("ice_res"))
    thunder_res = attr.ib(ViewAttrCtrl("thunder_res"))
    dragon_res = attr.ib(ViewAttrCtrl("dragon_res"))
    num_gem_slots = attr.ib(ViewAttrCtrl("num_gem_slots"))
    gem_slot1_lvl = attr.ib(ViewAttrCtrl("gem_slot1_lvl"))
    gem_slot2_lvl = attr.ib(ViewAttrCtrl("gem_slot2_lvl"))
    gem_slot3_lvl = attr.ib(ViewAttrCtrl("gem_slot3_lvl"))
    set_skill1 = attr.ib(ViewAttrCtrl("set_skill1"))
    set_skill1_lvl = attr.ib(ViewAttrCtrl("set_skill1_lvl"))
    set_skill2 = attr.ib(ViewAttrCtrl("set_skill2"))
    set_skill2_lvl = attr.ib(ViewAttrCtrl("set_skill2_lvl"))
    skill1 = attr.ib(ViewAttrCtrl("skill1"))
    skill1_lvl = attr.ib(ViewAttrCtrl("skill1_lvl"))
    skill2 = attr.ib(ViewAttrCtrl("skill2"))
    skill2_lvl = attr.ib(ViewAttrCtrl("skill2_lvl"))
    skill3 = attr.ib(ViewAttrCtrl("skill3"))
    skill3_lvl = attr.ib(ViewAttrCtrl("skill3_lvl"))
    gmd_string_index = attr.ib(ViewAttrCtrl("gmd_string_index"))

    def update(self, model):
        for field in attr.fields(ArmorPieceViewCtrl):
            getattr(self, field.name).update(model)

