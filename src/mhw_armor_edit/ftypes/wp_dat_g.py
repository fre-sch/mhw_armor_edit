# coding: utf-8
import struct

from mhw_armor_edit.ftypes import Struct, InvalidDataError


class WpDatGEntry(metaclass=Struct):
    STRUCT_SIZE = 68
    index: "<I"
    byte1: "<B"
    byte2: "<B"
    short3: "<h"
    short4: "<h"
    short5: "<h"
    byte6: "<B"
    tree_id: "<B"
    byte8: "<B"
    byte9: "<B"
    byte10: "<B"
    byte11: "<B"
    byte12: "<B"
    cost: "<I"
    rarity: "<B"
    true_damage: "<H"
    defense: "<H"
    affinity: "<b"
    unknown23: "<B"
    unknown24: "<B"
    unknown25: "<B"
    unknown26: "<B"
    unknown27: "<B"
    unknown28: "<B"
    unknown29: "<B"
    shell_table_id: "<H"
    unknown30: "<B"
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


class WpDatG:
    MAGIC = 0x01B1
    NUM_ENTRY_OFFSET = 2
    ENTRY_OFFSET = 6

    def __init__(self, data):
        self.data = data
        self.num_entries = self._read_num_entries()
        self.entries = list(self._load_entries())

    def _read_num_entries(self):
        result = struct.unpack_from("<I", self.data, self.NUM_ENTRY_OFFSET)
        return result[0]

    def _load_entries(self):
        for i in range(0, self.num_entries):
            offset = self.ENTRY_OFFSET + i * WpDatGEntry.STRUCT_SIZE
            yield WpDatGEntry(self.data, offset)

    def __getitem__(self, item):
        return self.entries[item]

    def __len__(self):
        return len(self.entries)

    def find(self, **attrs):
        for item in self.entries:
            attrs_match = all(
                getattr(item, key, None) == value
                for key, value in attrs.items()
            )
            if attrs_match:
                yield item

    def find_first(self, **attrs):
        for item in self.find(**attrs):
            return item

    @classmethod
    def check_header(cls, data):
        result = struct.unpack_from("<H", data, 0)
        if result[0] != cls.MAGIC:
            raise InvalidDataError(
                f"magic byte invalid: expected {cls.MAGIC:04X}, "
                f"found {result[0]:04X}")
        result = struct.unpack_from("<I", data, cls.NUM_ENTRY_OFFSET)
        num_entries = result[0]
        entries_size = num_entries * WpDatGEntry.STRUCT_SIZE
        data_entries_size = len(data) - cls.ENTRY_OFFSET
        if data_entries_size != entries_size:
            raise InvalidDataError(f"total size invalid: "
                                   f"expected {entries_size} bytes, "
                                   f"found {data_entries_size}")
        return True

    @classmethod
    def load(cls, fp):
        data = bytearray(fp.read())
        cls.check_header(data)
        return cls(data)

    def save(self, fp):
        fp.write(self.data)
