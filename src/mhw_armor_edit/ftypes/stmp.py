# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class StmpEntry(Struct):
    STRUCT_SIZE = 40
    id: ft.uint()
    unk1: ft.ushort()
    unk3: ft.ushort()
    unk4: ft.ushort()
    unk6: ft.ushort()
    client_id: ft.int()
    unk7: ft.uint()
    rp_cost: ft.uint()
    item1_id: ft.uint()
    item2_id: ft.uint()
    item1_qty: ft.uint()
    item2_qty: ft.uint()


class Stmp(StructFile):
    EntryFactory = StmpEntry
    MAGIC = 0x0066
