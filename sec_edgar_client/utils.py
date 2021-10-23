from typing import Mapping, TypeVar

__all__ = (
    "get_trimmed_to_same_len",
)


KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")
TypedMapping = Mapping[KeyT, ValueT]


def get_trimmed_to_same_len(
    *mappings: TypedMapping,
) -> tuple[TypedMapping, ...]:
    common_keys = min(mappings, key=len).keys()

    res = []
    for mapping in mappings:
        data = {
            key: value
            for key, value in mapping.items()
            if key in common_keys
        }
        res.append(data)

    return tuple(res)
