# coding: utf-8
import struct

from mhw_armor_edit.ftypes import Struct, InvalidDataError


class ShellTableEntry(metaclass=Struct):
    STRUCT_SIZE = 111
    STRUCT_FIELDS = (
        ("normal1_count", "<B"),
        ("normal1_type", "<B"),
        ("normal1_reload", "<b"),
        ("normal2_count", "<B"),
        ("normal2_type", "<B"),
        ("normal2_reload", "<b"),
        ("normal3_count", "<B"),
        ("normal3_type", "<B"),
        ("normal3_reload", "<b"),
        ("pierce1_count", "<B"),
        ("pierce1_type", "<B"),
        ("pierce1_reload", "<b"),
        ("pierce2_count", "<B"),
        ("pierce2_type", "<B"),
        ("pierce2_reload", "<b"),
        ("pierce3_count", "<B"),
        ("pierce3_type", "<B"),
        ("pierce3_reload", "<b"),
        ("spread1_count", "<B"),
        ("spread1_type", "<B"),
        ("spread1_reload", "<b"),
        ("spread2_count", "<B"),
        ("spread2_type", "<B"),
        ("spread2_reload", "<b"),
        ("spread3_count", "<B"),
        ("spread3_type", "<B"),
        ("spread3_reload", "<b"),
    ) + tuple(
        (t[0].format(i), t[1])
        for i in range(37 - 9)
        for t in (
            ("ammo{}_count", "<B"),
            ("ammo{}_type", "<B"),
            ("ammo{}_reload", "<b"),
        )
    )

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class ShellTable:
    MAGIC = 0x01A6
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
            offset = self.ENTRY_OFFSET + i * ShellTableEntry.STRUCT_SIZE
            yield ShellTableEntry(self.data, offset)

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
        entries_size = num_entries * ShellTableEntry.STRUCT_SIZE
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
