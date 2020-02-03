# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class SklDatEntry(Struct):
    STRUCT_SIZE = 19
    skill_id: ft.ushort()
    level: ft.ubyte()
    param1: ft.ushort()
    param2: ft.ushort()
    param3: ft.ushort()
    param4: ft.ushort()
    param5: ft.ushort()
    param6: ft.ushort()
    param7: ft.ushort()
    param8: ft.ushort()


class SklDat(StructFile):
    EntryFactory = SklDatEntry
    MAGIC = 0x0087
