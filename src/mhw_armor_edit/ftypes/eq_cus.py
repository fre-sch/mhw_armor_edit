# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


# noinspection PyUnresolvedReferences
class EqCusEntry(Struct):
    STRUCT_SIZE = 41
    equip_type: "<B"
    equip_id: "<H"
    key_item_id: "<H"
    unk1: "<i"
    unk2: "<I"
    unk3: "<I"
    item1_id: "<H"
    item1_qty: "<B"
    item2_id: "<H"
    item2_qty: "<B"
    item3_id: "<H"
    item3_qty: "<B"
    item4_id: "<H"
    item4_qty: "<B"
    unk4: "<H"
    unk5: ("<7B", True)
    unk6: "<B"
    unk7: "<H"


class EqCus(StructFile):
    EntryFactory = EqCusEntry
    MAGIC = 0x0051
