# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import StructFile, Struct


class LbmSkillEntry(Struct):
    STRUCT_SIZE = 10
    rarity: ft.ubyte()
    augment_type: ft.ubyte()
    item_id: ft.ushort()
    item_qty: ft.ushort()
    unk3: ft.ubyte()
    unk4: ft.ubyte()
    unk5: ft.ubyte()
    unk6: ft.ubyte()


class LbmSkill(StructFile):
    EntryFactory = LbmSkillEntry
    MAGIC = 0x0046
