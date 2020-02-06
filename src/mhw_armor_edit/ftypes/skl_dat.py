# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class SklDatEntry(Struct):
    STRUCT_SIZE = 27
    skill_id: ft.ushort()
    level: ft.ubyte()
    param01: ft.ushort()
    param02: ft.ushort()
    param03: ft.ushort()
    param04: ft.ushort()
    param05: ft.ushort()
    param06: ft.ushort()
    param07: ft.ushort()
    param08: ft.ushort()
    param09: ft.ushort()
    param10: ft.ushort()
    param11: ft.ushort()
    param12: ft.ushort()


class SklDat(StructFile):
    EntryFactory = SklDatEntry
    MAGIC = 0x00BB
