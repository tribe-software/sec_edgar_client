from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import attr

__all__ = (
    "CIKRepositoryInterface",
    "LocalFileCIKRepository",
)


class CIKRepositoryInterface(ABC):
    """
    The Central Index Key (CIK) is used on the SEC's computer systems
    to identify corporations and individual people who have filed disclosure
    with the SEC.
    """

    @abstractmethod
    async def find(self, ticker: str) -> Optional[str]:
        pass


@attr.s(auto_attribs=True, slots=True, frozen=True)
class LocalFileCIKRepository(CIKRepositoryInterface):
    """
    The ticker-CIK mapping file
    is downloaded from https://www.sec.gov/include/ticker.txt.
    """
    _file: Path

    async def find(self, ticker: str) -> Optional[str]:
        with self._file.open(encoding="utf-8") as stream:
            for line in stream:
                ticker_, cik = line.split()
                if ticker_ == ticker.lower():
                    return _expand_cik_to_10_digits(cik)
        return None


def _expand_cik_to_10_digits(cik: str) -> str:
    zeros = "0" * (10 - len(cik))
    return zeros + cik
