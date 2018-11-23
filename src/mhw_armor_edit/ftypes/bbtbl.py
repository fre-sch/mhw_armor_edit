# coding: utf-8
from mhw_armor_edit.ftypes import StructFile, Struct


class BbtblEntry(Struct):
    STRUCT_SIZE = 6
    close_range: "<B"
    power: "<B"
    paralysis: "<B"
    poison: "<B"
    sleep: "<B"
    blast: "<B"


class Bbtbl(StructFile):
    EntryFactory = BbtblEntry
    MAGIC = 0x01A6
