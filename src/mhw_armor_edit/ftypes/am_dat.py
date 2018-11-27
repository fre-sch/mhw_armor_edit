# coding: utf-8

from mhw_armor_edit.ftypes import Struct, StructFile


# noinspection PyUnresolvedReferences
class AmDatEntry(Struct):
    STRUCT_SIZE = 60
    id: "<I"
    order: "<H"
    variant: "<B"
    set_id: "<H"
    type: "<B"
    equip_slot: "<B"
    defense: "<H"
    mdl_main_id: "<H"
    mdl_secondary_id: "<H"
    icon_color: "<B"
    pad8: "<B"
    icon_effect: "<B"
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
    gender: "<B"
    pad11: "<B"
    pad12: "<B"
    pad13: "<B"
    set_group: "<H"
    gmd_name_index: "<H"
    gmd_desc_index: "<H"
    is_permanent: "<B"


class AmDat(StructFile):
    MAGIC = 0x005d
    EntryFactory = AmDatEntry
