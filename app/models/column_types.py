from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.types import TypeDecorator


class BitBoolean(TypeDecorator):
    impl = BIT(1)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return 1 if value else 0

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, bytes):
            return int.from_bytes(value, byteorder="big") == 1
        if isinstance(value, bytearray):
            return int.from_bytes(bytes(value), byteorder="big") == 1
        return bool(value)

    def result_processor(self, dialect, coltype):
        impl_processor = self.impl_instance.result_processor(dialect, coltype)

        def process(value):
            if value is None:
                return None
            if isinstance(value, (int, bool)):
                return bool(value)
            if impl_processor:
                value = impl_processor(value)
            return self.process_result_value(value, dialect)

        return process
