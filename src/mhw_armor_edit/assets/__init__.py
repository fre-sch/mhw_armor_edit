# coding: utf-8
import json
import pkgutil
from io import BytesIO


class Assets:
    @classmethod
    def load_asset_json(cls, resource):
        return json.loads(cls.load_asset(resource))

    @classmethod
    def load_asset(cls, resource):
        return pkgutil.get_data("mhw_armor_edit.assets", resource).decode("UTF-8")

    @classmethod
    def load_asset_file(cls, resource):
        return BytesIO(pkgutil.get_data("mhw_armor_edit.assets", resource))

    @classmethod
    def load(cls):
        cls.item_editor_ui = cls.load_asset("item_editor.ui")
