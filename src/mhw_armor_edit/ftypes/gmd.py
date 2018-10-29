# coding: utf-8
import logging
from collections import namedtuple

from mhw_armor_edit.ftypes import InvalidDataError, Struct

log = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
class GmdHeader(metaclass=Struct):
    STRUCT_SIZE = 40
    magic: "<I"
    version: "<I"
    language: "<I"
    unknown1: "<I"
    unknown2: "<I"
    key_count: "<I"
    string_count: "<I"
    key_block_size: "<I"
    string_block_size: "<I"
    name_size: "<I"

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


# noinspection PyUnresolvedReferences
class GmdInfoItem(metaclass=Struct):
    STRUCT_SIZE = 32
    string_index: "<I"
    unknown1a: "<B"
    unknown1b: "<B"
    unknown1c: "<B"
    unknown1d: "<B"
    unknown2a: "<B"
    unknown2b: "<B"
    unknown2c: "<B"
    unknown2d: "<B"
    unknown3: "<H"
    unknown4: "<H"
    key_offset: "<I"
    unknown5: "<I"
    unknown6: "<I"
    unknown7: "<I"

    def __init__(self, index, data, offset):
        self.index = index
        self.data = data
        self.offset = offset


class GmdInfoItemKeyless:
    def __init__(self, parent, index):
        self.__dict__.update(parent)
        self.index = index
        self.string_index = index
        self.key_offset = -1


class GmdInfoTable:
    def __init__(self, data, offset, key_count, string_count):
        self.data = data
        self.offset = offset
        self.key_count = key_count
        self.string_count = string_count
        self.items = tuple(self._read_items(data))

    def _read_items(self, data):
        prev_string_index = 0
        for key_index in range(self.key_count):
            item = GmdInfoItem(
                key_index, data,
                self.offset + key_index * GmdInfoItem.STRUCT_SIZE)
            for missing_string_index in range(prev_string_index + 1, item.string_index):
                yield GmdInfoItemKeyless(item.as_dict(), missing_string_index)
            prev_string_index = item.string_index
            yield item
        for key_index in range(prev_string_index + 1, self.string_count):
            yield GmdInfoItemKeyless(key_index)

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

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key):
        if key == -1:
            return ""
        return self.items[key]

    def __len__(self):
        return len(self.items)

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


GmdItem = namedtuple("GmdItem", GmdInfoItem.fields() + ("key", "value"))


class Gmd:
    MAGIC = 0x00444d47

    def __init__(self, data):
        self.data = data
        self.header = GmdHeader(data, 0)
        self.info_table = GmdInfoTable(data, self.header.total_size,
                                       self.header.key_count,
                                       self.header.string_count)
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
            GmdItem(*(
                info.values()
                + (
                    self.key_table[info.key_offset],
                    self.string_table[info.string_index],
                )
            ))
            for info in self.info_table
        ]

    def get_string(self, index, default=None):
        try:
            value = self.string_table[index]
            return f"{value}({index})"
        except IndexError:
            return default

    @classmethod
    def check_header(cls, data):
        header = GmdHeader(data, 0)
        if header.magic != cls.MAGIC:
            raise InvalidDataError(
                f"magic byte invalid: expected {cls.MAGIC:04X}, found {header.magic:04X}")
        log.debug("key_count: %s, string_count: %s",
                  header.key_count,
                  header.string_count)

    @classmethod
    def load(cls, fp):
        data = bytearray(fp.read())
        cls.check_header(data)
        return cls(data)
