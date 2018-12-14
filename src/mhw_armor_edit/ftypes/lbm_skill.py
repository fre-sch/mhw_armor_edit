# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class LbmSkillEntry(Struct):
    STRUCT_SIZE = 10
    unk1: "<B"
    unk2: "<B"
    item_id: "<H"
    item_qty: "<H"
    unk3: ("<4B", True)


class LbmSkill(StructFile):
    EntryFactory = LbmSkillEntry
    MAGIC = 0x0046
