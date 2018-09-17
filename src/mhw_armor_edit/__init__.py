# coding: utf-8
import struct


class Field:
    def __init__(self, offset, fmt):
        self.offset = offset
        self.fmt = fmt
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name

    @property
    def size(self):
        return struct.calcsize(self.fmt)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        result = struct.unpack_from(self.fmt,
                                    instance.data,
                                    instance.offset + self.offset)
        return result[0]

    def __set__(self, instance, value):
        if instance is None:
            return
        if value is None:
            return
        struct.pack_into(self.fmt,
                         instance.data,
                         instance.offset + self.offset,
                         value)


class AmDatEntry:
    SIZE = 60

    index = Field(0, "<H")
    # pad 4 bytes
    pad1 = Field(2, "<B")
    pad2 = Field(3, "<B")
    pad3 = Field(4, "<B")
    pad4 = Field(5, "<B")
    # end pad
    variant = Field(6, "<B")
    set_id = Field(7, "<B")
    pad5 = Field(8, "<B")
    pad6 = Field(9, "<B")
    # end pad
    equip_slot = Field(10, "<B")
    defense = Field(11, "<H")
    main_id = Field(13, "<H")
    secondary_id = Field(15, "<H")
    pad7 = Field(17, "<B")
    pad8 = Field(18, "<B")
    pad9 = Field(19, "<B")
    rarity = Field(20, "<B")
    cost = Field(21, "<I")
    fire_res = Field(25, "<b")
    water_res = Field(26, "<b")
    ice_res = Field(27, "<b")
    thunder_res = Field(28, "<b")
    dragon_res = Field(29, "<b")
    num_gem_slots = Field(30, "<B")
    gem_slot1_lvl = Field(31, "<B")
    gem_slot2_lvl = Field(32, "<B")
    gem_slot3_lvl = Field(33, "<B")
    set_skill1 = Field(34, "<h")
    set_skill1_lvl = Field(36, "<B")
    set_skill2 = Field(37, "<h")
    set_skill2_lvl = Field(39, "<B")
    skill1 = Field(40, "<h")
    skill1_lvl = Field(42, "<B")
    skill2 = Field(43, "<h")
    skill2_lvl = Field(45, "<B")
    skill3 = Field(46, "<h")
    skill3_lvl = Field(48, "<B")
    # pad
    pad10 = Field(49, "<B")
    pad11 = Field(50, "<B")
    pad12 = Field(51, "<B")
    pad13 = Field(52, "<B")
    pad14 = Field(53, "<B")
    pad15 = Field(54, "<B")
    pad16 = Field(55, "<B")
    pad17 = Field(56, "<B")
    pad18 = Field(57, "<B")
    pad19 = Field(58, "<B")
    pad20 = Field(59, "<B")

    # end pad

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset

    @classmethod
    def fields(cls):
        fields = (
            getattr(cls, attr)
            for attr in dir(cls)
            if isinstance(getattr(cls, attr), Field)
        )
        return [it._name for it in sorted(fields, key=lambda it: it.offset)]

    def as_dict(self):
        return {
            field: getattr(self, field)
            for field in self.fields()
        }


class InvalidDataError(Exception):
    pass


class AmDat:
    NUM_ENTRY_OFFSET = 2
    ENTRY_OFFSET = 6

    def __init__(self, data):
        self.data = data
        self.num_records = self.read_num_entries()
        self.entries = list(self.load_entries())

    def read_num_entries(self):
        result = struct.unpack_from("<I", self.data, self.NUM_ENTRY_OFFSET)
        return result[0]

    def load_entries(self):
        for i in range(0, self.num_records):
            offset = self.ENTRY_OFFSET + i * AmDatEntry.SIZE
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

    @classmethod
    def check_header(cls, data):
        result = struct.unpack_from("<H", data, 0)
        if result[0] != 0x005d:
            raise InvalidDataError("magic byte invalid")
        result = struct.unpack_from("<I", data, cls.NUM_ENTRY_OFFSET)
        num_entries = result[0]
        entries_size = num_entries * AmDatEntry.SIZE
        data_entries_size = len(data) - cls.ENTRY_OFFSET
        if data_entries_size != entries_size:
            raise InvalidDataError(f"total size invalid: "
                                   f"expected {entries_size} bytes, "
                                   f"found {data_entries_size}")
        return True

    @classmethod
    def make(cls, fp):
        data = bytearray(fp.read())
        cls.check_header(data)
        return cls(data)


