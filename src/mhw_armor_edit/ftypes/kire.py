# coding: utf-8

from mhw_armor_edit.ftypes import Struct, TableFile


# noinspection PyUnresolvedReferences
class KireEntry(metaclass=Struct):
    STRUCT_SIZE = 18
    id: "<I"
    red: "<H"
    orange: "<H"
    yellow: "<H"
    green: "<H"
    blue: "<H"
    white: "<H"
    purple: "<H"

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class Kire(TableFile):
    EntryFactory = KireEntry
    MAGIC = 0x0177
