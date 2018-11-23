# coding: utf-8

from mhw_armor_edit.ftypes import Struct, StructFile


# noinspection PyUnresolvedReferences
class AmDatEntry(Struct):
    STRUCT_SIZE = 60
    id: "<I"
    pad3: "<B"
    pad4: "<B"
    variant: "<B"
    set_id: "<B"
    pad5: "<B"
    pad6: "<B"
    equip_slot: "<B"
    defense: "<H"
    main_id: "<H"
    secondary_id: "<H"
    pad7: "<B"
    pad8: "<B"
    pad9: "<B"
    rarity: "<B"
    cost: "<I"
    fire_res: "<b"
    water_res: "<b"
    ice_res: "<b"
    thunder_res: "<b"
    dragon_res: "<b"
    num_gem_slots: "<B"
    gem_slot1_lvl: "<B"
    gem_slot2_lvl: "<B"
    gem_slot3_lvl: "<B"
    set_skill1: "<h"
    set_skill1_lvl: "<B"
    set_skill2: "<h"
    set_skill2_lvl: "<B"
    skill1: "<h"
    skill1_lvl: "<B"
    skill2: "<h"
    skill2_lvl: "<B"
    skill3: "<h"
    skill3_lvl: "<B"
    pad10: "<B"
    pad11: "<B"
    pad12: "<B"
    pad13: "<B"
    pad14: "<B"
    pad15: "<B"
    gmd_name_index: "<H"
    gmd_desc_index: "<H"
    pad19: "<B"


class AmDat(StructFile):
    MAGIC = 0x005d
    EntryFactory = AmDatEntry
