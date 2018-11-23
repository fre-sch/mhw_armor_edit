# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class KireEntry(Struct):
    STRUCT_SIZE = 18
    id: "<I"
    red: "<H"
    orange: "<H"
    yellow: "<H"
    green: "<H"
    blue: "<H"
    white: "<H"
    purple: "<H"


class Kire(StructFile):
    EntryFactory = KireEntry
    MAGIC = 0x0177
