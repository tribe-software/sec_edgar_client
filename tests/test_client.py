# pylint: disable=no-self-use
# pylint: disable=too-many-arguments

from datetime import date
from typing import Final
from unittest import mock

import pytest
from aiohttp import web

from sec_gov_edgar_client import (
    BalanceSnapshot,
    CIKRepositoryInterface,
    Reports,
)
from sec_gov_edgar_client.test_utils import Handler, sec_client_factory

from .example_data import (
    MNST_RESPONSE_DATA,
    VEEV_RESPONSE_DATA,
    Z_RESPONSE_DATA,
)

VEEVA: Final = Reports(
    reported_at=(
        date(2014, 1, 31),
        date(2015, 1, 31),
        date(2016, 1, 31),
        date(2017, 1, 31),
        date(2018, 1, 31),
        date(2019, 1, 31),
        date(2020, 1, 31),
        date(2021, 1, 31),
    ),
    balance=(
        BalanceSnapshot(assets=370_308_000, equity=280_096_000),
        BalanceSnapshot(assets=544_890_000, equity=406_833_000),
        BalanceSnapshot(assets=705_799_000, equity=505_249_000),
        BalanceSnapshot(assets=917_700_000, equity=652_978_000),
        BalanceSnapshot(assets=1_197_008_000, equity=871_527_000),
        BalanceSnapshot(assets=1_653_766_000, equity=1_237_749_000),
        BalanceSnapshot(assets=2_271_777_000, equity=1_665_594_000),
        BalanceSnapshot(assets=3_046_067_000, equity=2_266_320_000),
    ),
)


ZILLOW: Final = Reports(
    reported_at=(
        date(2015, 12, 31),
        date(2016, 12, 31),
        date(2017, 12, 31),
        date(2018, 12, 31),
        date(2019, 12, 31),
        date(2020, 12, 31),
    ),
    balance=(
        BalanceSnapshot(assets=3_135_700_000, equity=2_679_053_000),
        BalanceSnapshot(assets=3_149_677_000, equity=2_533_587_000),
        BalanceSnapshot(assets=3_230_517_000, equity=2_660_823_000),
        BalanceSnapshot(assets=4_291_116_000, equity=3_267_179_000),
        BalanceSnapshot(assets=6_131_973_000, equity=3_435_421_000),
        BalanceSnapshot(assets=7_486_560_000, equity=4_741_816_000),
    ),
)

MONSTER_BEVERAGE: Final = Reports(
    reported_at=(
        date(2010, 12, 31),
        date(2011, 12, 31),
        date(2012, 12, 31),
        date(2013, 12, 31),
        date(2014, 12, 31),
        date(2015, 12, 31),
        date(2016, 12, 31),
        date(2017, 12, 31),
        date(2018, 12, 31),
        date(2019, 12, 31),
        date(2020, 12, 31),
    ),
    balance=(
        BalanceSnapshot(assets=1_082_131_000, equity=828_398_000),
        BalanceSnapshot(assets=1_362_399_000, equity=979_158_000),
        BalanceSnapshot(assets=1_043_325_000, equity=644_397_000),
        BalanceSnapshot(assets=1_420_509_000, equity=992_279_000),
        BalanceSnapshot(assets=1_938_875_000, equity=1_515_150_000),
        BalanceSnapshot(assets=5_675_189_000, equity=4_809_410_000),
        BalanceSnapshot(assets=4_153_471_000, equity=3_329_709_000),
        BalanceSnapshot(assets=4_791_012_000, equity=3_895_212_000),
        BalanceSnapshot(assets=4_526_891_000, equity=3_610_901_000),
        BalanceSnapshot(assets=5_150_352_000, equity=4_171_281_000),
        BalanceSnapshot(assets=6_202_716_000, equity=5_160_860_000),
    ),
)


class TestSECGovEDGARClient:

    @pytest.mark.parametrize(
        ("ticker", "cik", "sec_response", "expected_reports"),
        [
            ("VEEV", "0001393052", VEEV_RESPONSE_DATA, VEEVA),
            ("Z", "0001617640", Z_RESPONSE_DATA, ZILLOW),
            ("MNST", "0000865752", MNST_RESPONSE_DATA, MONSTER_BEVERAGE),
        ],
    )
    async def test__get_reports__hit(
        self,
        ticker: str,
        cik: str,
        sec_response: dict,
        expected_reports: Reports,
    ) -> None:
        ciks = mock.create_autospec(CIKRepositoryInterface)
        ciks.find.return_value = cik

        async def _handler(request: web.Request) -> web.Response:
            assert request.path == f"/xbrl/companyfacts/CIK{cik}.json"
            return web.json_response(sec_response)

        handler = mock.AsyncMock(wraps=_handler, spec=Handler)

        async with sec_client_factory(ciks, handler) as sec:
            reports = await sec.get_reports(ticker)

        assert reports == expected_reports
        handler.assert_awaited_once()

    async def test__get_reports__missing_ticker__return_none(self) -> None:
        ciks = mock.create_autospec(CIKRepositoryInterface)
        ciks.find.return_value = None

        handler = mock.AsyncMock(spec=Handler)

        async with sec_client_factory(ciks, handler) as sec:
            reports = await sec.get_reports(ticker="missing")

        assert reports is None
        handler.assert_not_awaited()
