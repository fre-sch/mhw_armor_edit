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


class TableFile:
    EntryFactory = None
    MAGIC = None
    NUM_ENTRY_OFFSET = 2
    ENTRY_OFFSET = 6

    def __init__(self, data):
        self.data = data
        self.num_entries = self._read_num_entries()
        self.entries = list(self._load_entries())

    def _read_num_entries(self):
        result = struct.unpack_from("<I", self.data, self.NUM_ENTRY_OFFSET)
        return result[0]

    def _load_entries(self):
        for i in range(0, self.num_entries):
            offset = self.ENTRY_OFFSET + i * self.EntryFactory.STRUCT_SIZE
            yield self.EntryFactory(self.data, offset)

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
        if result[0] != cls.MAGIC:
            raise InvalidDataError(
                f"magic byte invalid: expected {cls.MAGIC:04X}, "
                f"found {result[0]:04X}")
        result = struct.unpack_from("<I", data, cls.NUM_ENTRY_OFFSET)
        num_entries = result[0]
        entries_size = num_entries * cls.EntryFactory.STRUCT_SIZE
        data_entries_size = len(data) - cls.ENTRY_OFFSET
        if data_entries_size != entries_size:
            raise InvalidDataError(f"total size invalid: "
                                   f"expected {entries_size} bytes, "
                                   f"found {data_entries_size}")
        return True

    @classmethod
    def load(cls, fp):
        data = bytearray(fp.read())
        cls.check_header(data)
        return cls(data)

    def save(self, fp):
        fp.write(self.data)


class InvalidDataError(Exception):
    pass
