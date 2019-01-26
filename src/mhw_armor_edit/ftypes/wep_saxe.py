# coding: utf-8

from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class WepSaxeEntry(Struct):
    STRUCT_SIZE = 7
    id: ft.uint()
    unk1: ft.ubyte()
    unk2: ft.ubyte()
    unk3: ft.ubyte()


class WepSaxe(StructFile):
    EntryFactory = WepSaxeEntry
    MAGIC = 0x0177
