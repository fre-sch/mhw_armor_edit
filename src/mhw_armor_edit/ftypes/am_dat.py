# coding: utf-8
import struct

from mhw_armor_edit.ftypes import Struct, InvalidDataError


# noinspection PyUnresolvedReferences
class AmDatEntry(metaclass=Struct):
    STRUCT_SIZE = 60
    index: "<I"
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

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class AmDat:
    MAGIC = 0x005d
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
            offset = self.ENTRY_OFFSET + i * AmDatEntry.STRUCT_SIZE
            yield AmDatEntry(self.data, offset)

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

    def save(self, fp):
        fp.write(self.data)

    @classmethod
    def check_header(cls, data):
        result = struct.unpack_from("<H", data, 0)
        if result[0] != cls.MAGIC:
            raise InvalidDataError(
                f"magic byte invalid: expected {cls.MAGIC:04X}, found {result[0]:04X}")
        result = struct.unpack_from("<I", data, cls.NUM_ENTRY_OFFSET)
        num_entries = result[0]
        entries_size = num_entries * AmDatEntry.STRUCT_SIZE
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
