# coding: utf-8
import struct
from enum import Enum

from mhw_armor_edit.ftypes import Struct, InvalidDataError


class ItmFlag(Enum):
    IsDefault = 2 ** 0
    IsQuestOnly = 2 ** 1
    Unknown1 = 2 ** 2
    IsConsumable = 2 ** 3
    IsAppraisal = 2 ** 4
    Unknown2 = 2 ** 5
    IsMega = 2 ** 6
    IsLevelOne = 2 ** 7
    IsLevelTwo = 2 ** 8
    IsLevelThree = 2 ** 9
    IsGlitter = 2 ** 10
    IsDeliverable = 2 ** 11
    IsNotShown = 2 ** 12


# noinspection PyUnresolvedReferences
class ItmEntry(metaclass=Struct):
    STRUCT_SIZE = 32
    id: "<I"
    sub_type: "<B"
    type: "<I"
    rarity: "<B"
    carry_limit: "<B"
    unk_limit: "<B"
    order: "<H"
    flags: "<I"
    icon_id: "<I"
    icon_color: "<B"
    carry_item: "<B"
    sell_price: "<I"
    buy_price: "<I"

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class Itm:
    MAGIC = 0x00AE
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
            offset = self.ENTRY_OFFSET + i * ItmEntry.STRUCT_SIZE
            yield ItmEntry(self.data, offset)

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
                f"magic byte invalid: expected {cls.MAGIC:04X}, found {result[0]:04X}")
        result = struct.unpack_from("<I", data, cls.NUM_ENTRY_OFFSET)
        num_entries = result[0]
        entries_size = num_entries * ItmEntry.STRUCT_SIZE
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
