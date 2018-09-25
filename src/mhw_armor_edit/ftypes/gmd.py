# coding: utf-8
import logging

from mhw_armor_edit.ftypes import InvalidDataError, Struct


log = logging.getLogger(__name__)

class GmdHeader(metaclass=Struct):
    STRUCT_SIZE = 40
    STRUCT_FIELDS = (
        ("magic", "<I"),
        ("version", "<I"),
        ("language", "<I"),
        ("unknown1", "<I"),
        ("unknown2", "<I"),
        ("key_count", "<I"),
        ("string_count", "<I"),
        ("key_block_size", "<I"),
        ("string_block_size", "<I"),
        ("name_size", "<I")
    )

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset
        self.name = self.read_name()

    def read_name(self):
        bstring = self.data[
                  GmdHeader.name_size.after
                  :GmdHeader.name_size.after + self.name_size]
        try:
            return bstring.decode("UTF-8")
        except Exception:
            return ""

    @property
    def total_size(self):
        return GmdHeader.name_size.after + self.name_size + 1


class GmdInfoItem(metaclass=Struct):
    STRUCT_SIZE = 32
    STRUCT_FIELDS = (
        ("string_index", "<I"),
        ("unknown1a", "<B"),
        ("unknown1b", "<B"),
        ("unknown1c", "<B"),
        ("unknown1d", "<B"),
        ("unknown2", "<I"),
        ("unknown3", "<H"),
        ("unknown4", "<H"),
        ("key_offset", "<I"),
        ("unknown5", "<I"),
        ("unknown6", "<I"),
        ("unknown7", "<I"),
    )

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class GmdInfoTable:
    def __init__(self, data, offset, key_count):
        self.data = data
        self.offset = offset
        self.key_count = key_count
        self.items = tuple(
            GmdInfoItem(data, self.offset + i * GmdInfoItem.STRUCT_SIZE)
            for i in range(self.key_count)
        )

    @property
    def after(self):
        return self.offset + (self.key_count * GmdInfoItem.STRUCT_SIZE)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, index):
        return self.items[index]


class GmdUnknownBlock(metaclass=Struct):
    """Always 2048 bytes, purpose yet unknown."""
    STRUCT_SIZE = 2048
    STRUCT_FIELDS = (
        ("value", "<2048c", True),
    )

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class GmdStringTable:
    def __init__(self, data, offset, block_size, count):
        self.data = data
        self.offset = offset
        self.block_size = block_size
        self.count = count
        self.items = self._read_items()
        if len(self.items) != self.count:
            raise InvalidDataError(
                f"expected {self.count} keys, read {len(self.items)}.")

    def __getitem__(self, key):
        return self.items[key]

    @property
    def after(self):
        return self.offset + self.block_size

    def _read_items(self):
        return [
            it.decode("UTF-8")
            for it in self.data[self.offset:-1].split(b"\x00")
        ]


class GmdKeyTable(GmdStringTable):
    def _read_items(self):
        i = 0
        offset = 0
        items = {}
        val = bytearray()
        while i < self.block_size:
            ch = self.data[self.offset + i]
            i += 1
            if ch == 0:
                items[offset] = val.decode("UTF-8")
                val = bytearray()
                offset = i
            else:
                val.append(ch)
        return items


class Gmd:
    MAGIC = 0x00444d47

    def __init__(self, data):
        self.data = data
        self.header = GmdHeader(data, 0)
        self.info_table = GmdInfoTable(data, self.header.total_size,
                                       self.header.key_count)
        self.unknown_block = GmdUnknownBlock(data,
                                             self.info_table.after)
        self.key_table = GmdKeyTable(self.data,
                                     self.unknown_block.after,
                                     self.header.key_block_size,
                                     self.header.key_count)
        self.string_table = GmdStringTable(self.data,
                                           self.key_table.after,
                                           self.header.string_block_size,
                                           self.header.string_count)
        self.items = [
            {
                "info": info,
                "key": self.key_table[info.key_offset],
                "value": self.string_table[info.string_index]
            }
            for info in self.info_table
        ]

    @classmethod
    def check_header(cls, data):
        header = GmdHeader(data, 0)
        if header.magic != cls.MAGIC:
            raise InvalidDataError(
                f"magic byte invalid: expected {cls.MAGIC:04X}, found {header.magic:04X}")

    @classmethod
    def load(cls, fp):
        data = bytearray(fp.read())
        cls.check_header(data)
        return cls(data)
