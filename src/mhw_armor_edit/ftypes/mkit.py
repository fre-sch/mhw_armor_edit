# coding: utf-8

from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class MkitEntry(Struct):
    STRUCT_SIZE = 20
    result_item_id: ft.uint()
    research_points: ft.uint()
    melding_points: ft.uint()
    category: ft.uint()
    unk1: ft.uint()


class Mkit(StructFile):
    EntryFactory = MkitEntry
    MAGIC = 0x00B4
