# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class SedEntry(Struct):
    STRUCT_SIZE = 12
    equip_type: ft.uint()
    equip_id: ft.uint()
    cost: ft.uint()


class Sed(StructFile):
    EntryFactory = SedEntry
    MAGIC = 0x0035
