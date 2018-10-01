# coding: utf-8
import struct

from mhw_armor_edit.ftypes import Struct, InvalidDataError


def ammo(name):
    return (
        (f"{name}_count", "<B"),
        (f"{name}_recoil", "<B"),
        (f"{name}_reload", "<B"),
    )


class ShellTableEntry(metaclass=Struct):
    STRUCT_SIZE = 111
    STRUCT_FIELDS = (
        ammo("normal1")
        + ammo("normal2")
        + ammo("normal3")
        + ammo("pierce1")
        + ammo("pierce2")
        + ammo("pierce3")
        + ammo("spread1")
        + ammo("spread2")
        + ammo("spread3")
        + ammo("cluster1")
        + ammo("cluster2")
        + ammo("cluster3")
        + ammo("wyvern")
        + ammo("sticky1")
        + ammo("sticky2")
        + ammo("sticky3")
        + ammo("slicing")
        + ammo("flaming")
        + ammo("water")
        + ammo("freeze")
        + ammo("thunder")
        + ammo("dragon")
        + ammo("poison1")
        + ammo("poison2")
        + ammo("paralysis1")
        + ammo("paralysis2")
        + ammo("sleep1")
        + ammo("sleep2")
        + ammo("exhaust1")
        + ammo("exhaust2")
        + ammo("recover1")
        + ammo("recover2")
        + ammo("demon")
        + ammo("armor")
        + ammo("unknown1")
        + ammo("unknown2")
        + ammo("tranq")
    )

    def __init__(self, index, data, offset):
        self.index = index
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
            yield ShellTableEntry(i, self.data, offset)

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

    def save(self, fp):
        fp.write(self.data)
