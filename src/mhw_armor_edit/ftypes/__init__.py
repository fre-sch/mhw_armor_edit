# coding: utf-8
import struct
from collections import Sequence


class StructField:
    def __init__(self, index, offset, fmt, multi=False):
        self.index = index
        self.offset = offset
        self.fmt = fmt
        self._name = None
        self.multi = multi

    def __set_name__(self, owner, name):
        self._name = name

    @property
    def size(self):
        return struct.calcsize(self.fmt)

    @property
    def after(self):
        return self.offset + self.size

    def __get__(self, instance, owner):
        if instance is None:
            return self
        result = struct.unpack_from(self.fmt,
                                    instance.data,
                                    instance.offset + self.offset)
        return result[0] if not self.multi else result

    def __set__(self, instance, value):
        if instance is None:
            return self
        if value is None:
            return
        struct.pack_into(self.fmt,
                         instance.data,
                         instance.offset + self.offset,
                         value)

    def __lt__(self, other):
        return self.offset < other.offset


class Struct(type):
    @staticmethod
    def fields(cls):
        fields = (
            getattr(cls, attr)
            for attr, _ in cls.STRUCT_FIELDS
        )
        return [it._name for it in sorted(fields)]

    @staticmethod
    def as_dict(instance):
        return {
            attr: getattr(instance, attr)
            for attr, fmt in instance.STRUCT_FIELDS
        }

    @staticmethod
    def values(instance):
        return tuple(
            getattr(instance, attr)
            for attr, fmt in instance.STRUCT_FIELDS
        )

    @staticmethod
    def repr(instance):
        class_name = instance.__class__.__name__
        return f"<{class_name} {instance.as_dict()!r}>"

    @staticmethod
    def after(instance):
        return instance.offset + instance.STRUCT_SIZE

    def __new__(cls, name, bases, namespace, **kwds):
        assert "STRUCT_SIZE" in namespace, "missinng expected STRUCT_SIZE class attr"
        assert "STRUCT_FIELDS" in namespace, "missing expected STRUCT_FIELDS class attr"
        assert isinstance(namespace["STRUCT_FIELDS"], Sequence)
        offset = 0
        struct_size = namespace["STRUCT_SIZE"]
        for i, it in enumerate(namespace["STRUCT_FIELDS"]):
            if len(it) == 3:
                field_name, fmt, multi = it
                namespace[field_name] = StructField(i, offset, fmt, multi)
            else:
                field_name, fmt = it
                namespace[field_name] = StructField(i, offset, fmt)
            offset += namespace[field_name].size
        assert offset == struct_size, \
            f"invalid struct size for {name}. " \
            f"expected {struct_size}, got {offset}"
        namespace["fields"] = classmethod(Struct.fields)
        namespace["as_dict"] = Struct.as_dict
        namespace["values"] = Struct.values
        namespace.setdefault("__repr__", Struct.repr)
        namespace.setdefault("after", property(Struct.after))
        return type.__new__(cls, name, bases, dict(namespace))


class InvalidDataError(Exception):
    pass
