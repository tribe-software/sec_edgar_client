from pathlib import Path
from typing import Final

import ujson

__all__ = (
    "TICKER_TO_CIK_MAPPING_FILE",

    "VEEV_RESPONSE_FILE",
    "VEEV_RESPONSE_DATA",

    "Z_RESPONSE_FILE",
    "Z_RESPONSE_DATA",

)

_CURRENT_DIR = Path(__file__).parent

TICKER_TO_CIK_MAPPING_FILE: Final = _CURRENT_DIR / "ticker_to_cik_mapping.txt"

VEEV_RESPONSE_FILE: Final = _CURRENT_DIR / "veev_response.json"
with VEEV_RESPONSE_FILE.open(encoding="utf-8") as stream:
    VEEV_RESPONSE_DATA: Final = ujson.load(stream)

Z_RESPONSE_FILE: Final = _CURRENT_DIR / "z_response.json"
with Z_RESPONSE_FILE.open(encoding="utf-8") as stream:
    Z_RESPONSE_DATA: Final = ujson.load(stream)
