# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct


class ArmUpEntry(Struct):
    STRUCT_SIZE = 22
    unk1: "<h"
    unk2: "<h"
    unk3: "<h"
    unk4: "<h"
    unk5: "<h"
    unk6: "<h"
    unk7: "<h"
    unk8: "<h"
    unk9: "<h"
    unk10: "<h"
    unk11: "<h"


class ArmUp(StructFile):
    EntryFactory = ArmUpEntry
    MAGIC = 0x0097
