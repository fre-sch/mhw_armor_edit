# coding: utf-8
from typing import Sequence

from PyQt5.QtWidgets import QComboBox, QSpinBox, QLabel
import attr
import logging


log = logging.getLogger(__name__)


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

    def connect(self):
        raise NotImplementedError()


class ComboBoxWidgetCtrl(WidgetCtrl):
    def __init__(self, items: Sequence, completer=False):
        self.items = items
        self.completer = completer
        super().__init__()

    def set_value(self, value):
        index = self.get_index(value)
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
        self.widget.setEditable(self.completer)
        return self.widget

    def connect(self, fn):
        self.widget.currentIndexChanged.connect(
            lambda: fn(self.get_value())
        )


class SpinBoxWidgetCtrl(WidgetCtrl):
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
        super().__init__()

    def set_value(self, value):
        self.widget.setValue(value)

    def get_value(self):
        return self.widget.value()

    def create_widget(self):
        widget = QSpinBox()
        widget.setRange(self.minimum, self.maximum)
        return widget

    def connect(self, fn):
        self.widget.valueChanged.connect(
            lambda value: fn(value)
        )


class LabelWidgetCtrl(WidgetCtrl):
    def __init__(self, items=None):
        self.items = {it["value"]: it["name"] for it in items}
        super().__init__()

    def set_value(self, value):
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

    def connect(self, fn):
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


class NameViewCtrl(ViewAttrCtrl):
    def __init__(self):
        super().__init__(None)

    def set_ctrl_value(self):
        if self._ctrl is None:
            return
        value = {
            "main_id": self.model.main_id,
            "secondary_id": self.model.secondary_id,
            "variant": self.model.variant
        }
        self._ctrl.set_value(value)


@attr.s
class PieceViewCtrl:
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

    def update(self, model):
        for field in attr.fields(PieceViewCtrl):
            getattr(self, field.name).update(model)

