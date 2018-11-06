# coding: utf-8

from mhw_armor_edit.ftypes import Struct, TableFile


class WpDatGEntry(metaclass=Struct):
    STRUCT_SIZE = 68
    id: "<I"
    byte1: "<B"
    byte2: "<B"
    base_model_id: "<h"
    part1_id: "<h"
    part2_id: "<h"
    color: "<B"
    tree_id: "<B"
    is_fixed_upgrade: "<B"
    byte9: "<B"
    byte10: "<B"
    byte11: "<B"
    byte12: "<B"
    cost: "<I"
    rarity: "<B"
    true_damage: "<H"
    defense: "<H"
    affinity: "<b"
    element_id: "<B"
    element_damage: "<H"
    hidden_element_id: "<B"
    hidden_element_damage: "<H"
    elderseal: "<B"
    shell_table_id: "<H"
    deviation: "<B"
    num_gem_slots: "<B"
    gem_slot1_lvl: "<B"
    gem_slot2_lvl: "<B"
    gem_slot3_lvl: "<B"
    unknown31: "<B"
    unknown32: "<B"
    unknown33: "<B"
    unknown34: "<B"
    unknown35: "<B"
    unknown36: "<B"
    unknown37: "<B"
    unknown38: "<B"
    unknown39: "<B"
    unknown40: "<B"
    unknown41: "<B"
    unknown42: "<B"
    unknown43: "<B"
    special_ammo_type: "<B"
    tree_position: "<B"
    order: "<H"
    gmd_name_index: "<H"
    gmd_description_index: "<H"
    skill_id: "<H"
    unknown51: "<B"
    unknown52: "<B"

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class WpDatG(TableFile):
    EntryFactory = WpDatGEntry
    MAGIC = 0x01B1
