# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class WepWslEntry(Struct):
    STRUCT_SIZE = 7
    id: ft.uint()
    note1: ft.ubyte()
    note2: ft.ubyte()
    note3: ft.ubyte()


class WepWsl(StructFile):
    EntryFactory = WepWslEntry
    MAGIC = 0x0177
