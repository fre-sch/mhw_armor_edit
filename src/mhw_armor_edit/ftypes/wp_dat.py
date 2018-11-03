# coding: utf-8
import struct

from mhw_armor_edit.ftypes import Struct, InvalidDataError


class WpDatEntry(metaclass=Struct):
    STRUCT_SIZE = 65
    index: "<I"
    unk1: "<B"
    unk2: "<B"
    base_model_id: "<H"
    part1_id: "<H"
    part2_id: "<H"
    color: "<B"
    tree_id: "<B"
    is_fixed_upgrade: "<B"
    crafting_cost: "<I"
    rarity: "<B"
    kire_id: "<B"
    handicraft: "<B"
    raw_damage: "<H"
    defense: "<H"
    affinity: "<b"
    element_id: "<B"
    element_damage: "<H"
    hidden_element_id: "<B"
    hidden_element_damage: "<H"
    elderseal: "<B"
    num_gem_slots: "<B"
    gem_slot1_lvl: "<B"
    gem_slot2_lvl: "<B"
    gem_slot3_lvl: "<B"
    unk3: "<B"
    unk4: "<B"
    unk5: "<B"
    unk6: "<B"
    unk7: "<I"
    unk8: "<I"
    unk9: "<I"
    tree_position: "<B"
    order: "<H"
    gmd_name_index: "<H"
    gmd_description_index: "<H"
    skill_id: "<H"
    unk10: "<H"

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class WpDat:
    MAGIC = 0x0186
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
            offset = self.ENTRY_OFFSET + i * WpDatEntry.STRUCT_SIZE
            yield WpDatEntry(self.data, offset)

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
        entries_size = num_entries * WpDatEntry.STRUCT_SIZE
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
