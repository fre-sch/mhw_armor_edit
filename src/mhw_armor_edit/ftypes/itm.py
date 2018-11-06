# coding: utf-8
from enum import Enum

from mhw_armor_edit.ftypes import Struct, TableFile


class ItmFlag(Enum):
    IsDefault = 2 ** 0
    IsQuestOnly = 2 ** 1
    Unknown1 = 2 ** 2
    IsConsumable = 2 ** 3
    IsAppraisal = 2 ** 4
    Unknown2 = 2 ** 5
    IsMega = 2 ** 6
    IsLevelOne = 2 ** 7
    IsLevelTwo = 2 ** 8
    IsLevelThree = 2 ** 9
    IsGlitter = 2 ** 10
    IsDeliverable = 2 ** 11
    IsNotShown = 2 ** 12


# noinspection PyUnresolvedReferences
class ItmEntry(metaclass=Struct):
    STRUCT_SIZE = 32
    id: "<I"
    sub_type: "<B"
    type: "<I"
    rarity: "<B"
    carry_limit: "<B"
    unk_limit: "<B"
    order: "<H"
    flags: "<I"
    icon_id: "<I"
    icon_color: "<B"
    carry_item: "<B"
    sell_price: "<I"
    buy_price: "<I"

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


class Itm(TableFile):
    EntryFactory = ItmEntry
    MAGIC = 0x00AE
