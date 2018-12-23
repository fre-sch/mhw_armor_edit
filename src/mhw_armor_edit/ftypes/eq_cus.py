# coding: utf-8

from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class EqCusEntry(Struct):
    STRUCT_SIZE = 41
    equip_type: ft.ubyte()
    equip_id: ft.ushort()
    key_item_id: ft.ushort()
    unk1: ft.int()
    unk2: ft.uint()
    unk3: ft.uint()
    item1_id: ft.ushort()
    item1_qty: ft.ubyte()
    item2_id: ft.ushort()
    item2_qty: ft.ubyte()
    item3_id: ft.ushort()
    item3_qty: ft.ubyte()
    item4_id: ft.ushort()
    item4_qty: ft.ubyte()
    unk4: ft.ushort()
    unk5: ft.pad(7)
    unk6: ft.ubyte()
    unk7: ft.ushort()


class EqCus(StructFile):
    EntryFactory = EqCusEntry
    MAGIC = 0x0051
