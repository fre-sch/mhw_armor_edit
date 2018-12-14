# coding: utf-8

from mhw_armor_edit.ftypes import Struct, StructFile, uint, ushort, ubyte, short, byte


class AmDatEntry(Struct):
    STRUCT_SIZE = 60
    id: uint()
    order: ushort()
    variant: ubyte()
    set_id: ushort()
    type: ubyte()
    equip_slot: ubyte()
    defense: ushort()
    mdl_main_id: ushort()
    mdl_secondary_id: ushort()
    icon_color: ubyte()
    pad8: ubyte()
    icon_effect: ubyte()
    rarity: ubyte()
    cost: uint()
    fire_res: byte()
    water_res: byte()
    ice_res: byte()
    thunder_res: byte()
    dragon_res: byte()
    num_gem_slots: ubyte()
    gem_slot1_lvl: ubyte()
    gem_slot2_lvl: ubyte()
    gem_slot3_lvl: ubyte()
    set_skill1: short()
    set_skill1_lvl: ubyte()
    set_skill2: short()
    set_skill2_lvl: ubyte()
    skill1: short()
    skill1_lvl: ubyte()
    skill2: short()
    skill2_lvl: ubyte()
    skill3: short()
    skill3_lvl: ubyte()
    gender: ubyte()
    pad11: ubyte()
    pad12: ubyte()
    pad13: ubyte()
    set_group: ushort()
    gmd_name_index: ushort()
    gmd_desc_index: ushort()
    is_permanent: ubyte()


class AmDat(StructFile):
    MAGIC = 0x005d
    EntryFactory = AmDatEntry
