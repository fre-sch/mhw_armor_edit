# coding: utf-8
from mhw_armor_edit import AmDat, Field


def test_am_dat_loading():
    with open("./test/data/armor.am_dat", "rb") as fp:
        am_dat = AmDat.make(fp)
        assert 1305 == am_dat.num_records


def test_am_dat_entry_size():
    class Thing:
        first = Field(0, "<H")
        second = Field(12, "<I")
        def __init__(self, offset):
            self.offset = offset

    assert 2 == Thing.first.size
    assert 4 == Thing.second.size


def test_am_dat_loading_entries():
    with open("./test/data/armor.am_dat", "rb") as fp:
        am_dat = AmDat.make(fp)
        entries = list(am_dat.load_entries())
        assert 1305 == len(entries)


def test_am_dat_loading_entries_data():
    with open("./test/data/armor.am_dat", "rb") as fp:
        am_dat = AmDat.make(fp)
        entries = list(am_dat.load_entries())

        assert 4 == entries[0].offset
        assert 0 == entries[0].category
        assert 0 == entries[0].index
        assert 0 == entries[0].variant
        assert 0 == entries[0].equip_slot
        assert 2 == entries[0].defense
        assert 1 == entries[0].main_id
        assert 0 == entries[0].secondary_id
        assert 0 == entries[0].rarity
        assert 100 == entries[0].cost

        assert 40504 == entries[675].offset
        assert 3 == entries[675].category
        assert 675 == entries[675].index
        assert 2 == entries[675].variant
        assert 3 == entries[675].equip_slot
        assert 32 == entries[675].defense
        assert 14 == entries[675].main_id
        assert 0 == entries[675].secondary_id
        assert 4 == entries[675].rarity
        assert 4000 == entries[675].cost

        assert 78244 == entries[1304].offset
        assert 0 == entries[1304].category
        assert 1304 == entries[1304].index
        assert 0 == entries[1304].variant
        assert 5 == entries[1304].equip_slot
        assert 0 == entries[1304].defense
        assert 0 == entries[1304].main_id
        assert 0 == entries[1304].secondary_id
        assert 2 == entries[1304].rarity
        assert 1500 == entries[1304].cost
