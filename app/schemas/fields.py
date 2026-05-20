from marshmallow import fields


def normalize_bit_bool(value):
    if value is None:
        return None

    if isinstance(value, bytes):
        return int.from_bytes(value, byteorder="big") == 1

    if isinstance(value, bytearray):
        return int.from_bytes(bytes(value), byteorder="big") == 1

    return bool(value)


class BitBool(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return normalize_bit_bool(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return normalize_bit_bool(value)
