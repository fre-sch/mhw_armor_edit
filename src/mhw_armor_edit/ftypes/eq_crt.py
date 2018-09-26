# coding: utf-8
import struct

from mhw_armor_edit.assets import Definitions
from mhw_armor_edit.ftypes import Struct, InvalidDataError


def item_lookup(value):
    return Definitions.lookup("item", value)


class EqCrtEntryView():
    FIELDS = dict([
        ("equip_type", None),
        ("equip_id", None),
        ("key_item", None),
        ("pad1", None),
        ("pad2", None),
        ("pad3", None),
        ("pad4", None),
        ("pad5", None),
        ("pad6", None),
        ("pad7", None),
        ("pad8", None),
        ("rank", None),
        ("item1_id", item_lookup),
        ("item1_qty", None),
        ("item2_id", item_lookup),
        ("item2_qty", None),
        ("item3_id", item_lookup),
        ("item3_qty", None),
        ("item4_id", item_lookup),
        ("item4_qty", None),
        ("pad9", None),
        ("pad10", None),
        ("pad11", None),
        ("pad12", None),
    ])

    def __init__(self, defs, cls, entry):
        self.defs = defs
        self.fields = cls.fields()
        self.entry = entry

    def __getattr__(self, key):
        value = getattr(self.entry, key)
        _lookup = self.FIELDS.get(key)
        if _lookup:
            lvalue = _lookup(value)
            return f"{lvalue} ({value})"
        return value


class EqCrtEntry(metaclass=Struct):
    STRUCT_SIZE = 33
    STRUCT_FIELDS = (
        ("equip_type", "<B"),
        ("equip_id", "<H"),
        ("key_item", "<H"),
        ("pad1", "<B"),
        ("pad2", "<B"),
        ("pad3", "<B"),
        ("pad4", "<B"),
        ("pad5", "<B"),
        ("pad6", "<B"),
        ("pad7", "<B"),
        ("pad8", "<B"),
        ("rank", "<I"),
        ("item1_id", "<H"),
        ("item1_qty", "<B"),
        ("item2_id", "<H"),
        ("item2_qty", "<B"),
        ("item3_id", "<H"),
        ("item3_qty", "<B"),
        ("item4_id", "<H"),
        ("item4_qty", "<B"),
        ("pad9", "<B"),
        ("pad10", "<B"),
        ("pad11", "<B"),
        ("pad12", "<B"),
    )

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class EqCrt:
    MAGIC = 0x0051
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
            offset = self.ENTRY_OFFSET + i * EqCrtEntry.STRUCT_SIZE
            yield EqCrtEntry(self.data, offset)

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
        entries_size = num_entries * EqCrtEntry.STRUCT_SIZE
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
