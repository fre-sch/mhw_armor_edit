# coding: utf-8

from mhw_armor_edit.ftypes import StructFile, Struct, short


class ArmUpEntry(Struct):
    STRUCT_SIZE = 22
    unk1: short()
    unk2: short()
    unk3: short()
    unk4: short()
    unk5: short()
    unk6: short()
    unk7: short()
    unk8: short()
    unk9: short()
    unk10: short()
    unk11: short()


class ArmUp(StructFile):
    EntryFactory = ArmUpEntry
    MAGIC = 0x0097
