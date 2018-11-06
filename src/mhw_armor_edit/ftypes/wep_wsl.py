# coding: utf-8

from mhw_armor_edit.ftypes import Struct, TableFile


class WepWslEntry(metaclass=Struct):
    STRUCT_SIZE = 7
    id: "<I"
    note1: "<B"
    note2: "<B"
    note3: "<B"

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class WepWsl(TableFile):
    EntryFactory = WepWslEntry
    MAGIC = 0x0177
