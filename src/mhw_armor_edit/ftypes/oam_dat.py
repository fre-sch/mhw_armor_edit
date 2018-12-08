# coding: utf-8

from mhw_armor_edit.ftypes import Struct, StructFile


# noinspection PyUnresolvedReferences
class OAmDatEntry(Struct):
    STRUCT_SIZE = 42
    id: "<I"
    set_id: "<H"
    equip_slot: "<B"
    unk1_byte: "<B"
    defense: "<I"
    rarity: "<B"
    list_order: "<H"
    model_id: "<I"
    crafting_cost: "<I"
    unk2_int: "<I"
    fire_res: "<b"
    water_res: "<b"
    ice_res: "<b"
    thunder_res: "<b"
    dragon_res: "<b"
    unk6_int: "<I"
    set_group: "<H"
    gmd_name_index: "<H"
    gmd_desc_index: "<H"


class OAmDat(StructFile):
    MAGIC = 0x0060
    EntryFactory = OAmDatEntry
