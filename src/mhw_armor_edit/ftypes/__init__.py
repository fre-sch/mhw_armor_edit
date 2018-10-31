# coding: utf-8
import struct


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
    def fields_from_fields_attr(namespace):
        offset = 0
        fields = namespace["STRUCT_FIELDS"]
        namespace["__fields__"] = list()
        for i, fields_spec in enumerate(fields):
            try:
                if len(fields_spec) == 2:
                    field_name, fmt = fields_spec
                    namespace[field_name] = StructField(i, offset, fmt)
                    offset += namespace[field_name].size
                    namespace["__fields__"].append(field_name)
                elif len(fields_spec) == 3:
                    field_name, fmt, multi = fields_spec
                    namespace[field_name] = StructField(i, offset, fmt, multi)
                    offset += namespace[field_name].size
                    namespace["__fields__"].append(field_name)
            except Exception:
                pass
        return offset

    @staticmethod
    def fields_from_annotations(namespace):
        offset = 0
        namespace["__fields__"] = list()
        fields = namespace["__annotations__"]
        for i, it in enumerate(fields.items()):
            try:
                field_name, field_spec = it
                if isinstance(field_spec, str):
                    namespace[field_name] = StructField(i, offset, field_spec)
                else:
                    fmt, multi = field_spec
                    namespace[field_name] = StructField(i, offset, fmt, multi)
                offset += namespace[field_name].size
                namespace["__fields__"].append(field_name)
            except Exception:
                pass
        return offset

    @staticmethod
    def fields(cls):
        return tuple(cls.__fields__)

    @staticmethod
    def as_dict(instance):
        return {
            attr: getattr(instance, attr)
            for attr in instance.__fields__
        }

    @staticmethod
    def values(instance):
        return tuple(
            getattr(instance, attr)
            for attr in instance.__fields__
        )

    @staticmethod
    def repr(instance):
        class_name = instance.__class__.__name__
        return f"<{class_name} {instance.as_dict()!r}>"

    @staticmethod
    def after(instance):
        return instance.offset + instance.STRUCT_SIZE

    def __new__(cls, name, bases, namespace, **kwds):
        assert "STRUCT_SIZE" in namespace, "missing expected STRUCT_SIZE class attr"
        offset = 0
        struct_size = namespace["STRUCT_SIZE"]
        if "STRUCT_FIELDS" in namespace:
            offset = Struct.fields_from_fields_attr(namespace)
        else:
            offset = Struct.fields_from_annotations(namespace)
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
