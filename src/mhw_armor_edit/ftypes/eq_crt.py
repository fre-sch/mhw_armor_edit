# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class EqCrtEntry(Struct):
    STRUCT_SIZE = 33
    equip_type: "<B"
    equip_id: "<H"
    key_item: "<H"
    unknown1: "<i"
    unknown2: "<I"
    rank: "<I"
    item1_id: "<H"
    item1_qty: "<B"
    item2_id: "<H"
    item2_qty: "<B"
    item3_id: "<H"
    item3_qty: "<B"
    item4_id: "<H"
    item4_qty: "<B"
    pad9: "<B"
    pad10: "<B"
    pad11: "<B"
    pad12: "<B"


class EqCrt(StructFile):
    EntryFactory = EqCrtEntry
    MAGIC = 0x0051
