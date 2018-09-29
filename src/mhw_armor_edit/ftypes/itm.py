# coding: utf-8
import struct

from mhw_armor_edit.ftypes import Struct, InvalidDataError


class ItmEntry(metaclass=Struct):
    STRUCT_SIZE = 32
    STRUCT_FIELDS = (
        ("index", "<H"),
        ("pad2", "<B"),
        ("pad3", "<B"),
        ("pad4", "<B"),
        ("pad5", "<B"),
        ("pad6", "<B"),
        ("pad7", "<B"),
        ("pad8", "<B"),
        ("rarity", "<B"),
        ("stack_limit", "<B"),
        ("carry_limit", "<B"),
        ("pad12", "<B"),
        ("pad13", "<B"),
        ("pad14", "<B"),
        ("pad15", "<B"),
        ("pad16", "<B"),
        ("pad17", "<B"),
        ("pad18", "<B"),
        ("pad19", "<B"),
        ("pad20", "<B"),
        ("pad21", "<B"),
        ("pad22", "<B"),
        ("pad23", "<B"),
        ("sell_price", "<I"),
        ("buy_price", "<I"),
    )

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
