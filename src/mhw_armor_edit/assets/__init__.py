# coding: utf-8
import json
import pkgutil


class Definitions:
    equip_slot = []
    gem_slot = []
    rarity = []
    set = []
    skill = []
    variant = []

    @classmethod
    def lookup(cls, key, value):
        for it in getattr(cls, key, []):
            if it["value"] == value:
                return it["name"]
        return f"Unknown {key}"

    @classmethod
    def load_asset(cls, resource):
        return json.loads(
            pkgutil.get_data("mhw_armor_edit.assets", resource).decode("UTF-8")
        )

    @classmethod
    def load(cls):
        cls.equip_slot = cls.load_asset("equip_slot.json")
        cls.gem_slot = cls.load_asset("gem_slot.json")
        cls.rarity = cls.load_asset("rarity.json")
        cls.set = cls.load_asset("set.json")
        cls.skill = cls.load_asset("skill.json")
        cls.variant = cls.load_asset("variant.json")
