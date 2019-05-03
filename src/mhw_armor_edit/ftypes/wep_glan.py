# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class WepGlanEntry(Struct):
    STRUCT_SIZE = 8
    id: ft.uint()
    type: ft.ushort()
    level: ft.ushort()


class WepGlan(StructFile):
    EntryFactory = WepGlanEntry
    MAGIC = 0x0177
