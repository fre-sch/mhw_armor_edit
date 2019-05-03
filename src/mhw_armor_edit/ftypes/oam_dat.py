# coding: utf-8
from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import Struct, StructFile


# noinspection PyUnresolvedReferences
class OAmDatEntry(Struct):
    STRUCT_SIZE = 42
    id: ft.uint()
    set_id: ft.ushort()
    equip_slot: ft.ubyte()
    unk1: ft.ubyte()
    defense: ft.uint()
    rarity: ft.ubyte()
    list_order: ft.ushort()
    model_id: ft.uint()
    crafting_cost: ft.uint()
    variant: ft.ubyte()
    unk2: ft.ubyte()
    unk3: ft.ubyte()
    unk4: ft.ubyte()
    fire_res: ft.byte()
    water_res: ft.byte()
    ice_res: ft.byte()
    thunder_res: ft.byte()
    dragon_res: ft.byte()
    unk5: ft.uint()
    set_group: ft.ushort()
    gmd_name_index: ft.ushort()
    gmd_desc_index: ft.ushort()


class OAmDat(StructFile):
    MAGIC = 0x0060
    EntryFactory = OAmDatEntry
