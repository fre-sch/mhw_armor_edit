# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct, uint


class AmrsEntry(Struct):
    STRUCT_SIZE = 4
    id: uint()


class Amrs(StructFile):
    EntryFactory = AmrsEntry
    MAGIC = 0x000C
