# coding: utf-8
from mhw_armor_edit.ftypes import Struct, TableFile


# noinspection PyUnresolvedReferences
class BbtblEntry(metaclass=Struct):
    STRUCT_SIZE = 6
    close_range: "<B"
    power: "<B"
    paralysis: "<B"
    poison: "<B"
    sleep: "<B"
    blast: "<B"

    def __init__(self, index, data, offset):
        self.id = index
        self.data = data
        self.offset = offset


class Bbtbl(TableFile):
    EntryFactory = BbtblEntry
    MAGIC = 0x01A6

    def _load_entries(self):
        for i in range(0, self.num_entries):
            offset = self.ENTRY_OFFSET + i * self.EntryFactory.STRUCT_SIZE
            yield self.EntryFactory(i, self.data, offset)
