# pylint: disable=no-self-use

import pytest

from sec_edgar_client import LocalFileCIKRepository

from .example_data import TICKER_TO_CIK_MAPPING_FILE


class TestLocalFileCIKRepository:

    @pytest.mark.parametrize(
        ("ticker", "cik"),
        [
            ("TTD", "0001671933"),
            ("Ttd", "0001671933"),
            ("ttd", "0001671933"),

            ("VEEV", "0001393052"),
            ("VEev", "0001393052"),
            ("veev", "0001393052"),
        ],
    )
    async def test__find__match__return_cik(
        self,
        ticker: str,
        cik: str,
    ) -> None:
        ciks = LocalFileCIKRepository(TICKER_TO_CIK_MAPPING_FILE)
        assert await ciks.find(ticker) == cik

    async def test__find__missing__return_none(self) -> None:
        ciks = LocalFileCIKRepository(TICKER_TO_CIK_MAPPING_FILE)
        assert await ciks.find(ticker="missing") is None
