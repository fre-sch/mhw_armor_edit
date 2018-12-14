# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class LbmBaseEntry(Struct):
    STRUCT_SIZE = 14
    rarity: "<B"
    equip_type: "<B"
    crafting_cost: "<I"
    item1_id: "<H"
    item1_qty: "<H"
    item2_id: "<H"
    item2_qty: "<H"


class LbmBase(StructFile):
    EntryFactory = LbmBaseEntry
    MAGIC = 0x0046
