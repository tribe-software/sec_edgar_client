# pylint: disable=no-self-use
# pylint: disable=too-many-arguments

from typing import Final
from unittest import mock

import pytest
from aiohttp import web

from sec_edgar_client import Balance, CIKRepositoryInterface, Income, Reports
from sec_edgar_client.test_utils import Handler, sec_client_factory

from .example_data import VEEV_RESPONSE_DATA

VEEVA: Final = Reports(
    Balance(
        assets={
            2012: 89_820_000,
            2013: 370_308_000,
            2014: 544_890_000,
            2015: 705_799_000,
            2016: 917_376_000,
            2017: 1_230_333_000,
            2018: 1_653_766_000,
            2019: 2_271_777_000,
            2020: 3_046_067_000,
        },
        equity={
            2010: 9173000,
            2011: 14103000,
            2012: 33966000,
            2013: 280096000,
            2014: 406833000,
            2015: 521980000,
            2016: 678154000,
            2017: 906238000,
            2018: 1237749000,
            2019: 1665594000,
            2020: 2266320000,
        },
    ),
    Income(
        revenue={
            2011: 61_262_000,
            2012: 129_548_000,
            2013: 210_151_000,
            2014: 313_222_000,
            2015: 409_221_000,
            2016: 550_542_000,
            2017: 690_559_000,
            2018: 862_210_000,
            2019: 1_104_081_000,
            2020: 1_465_069_000,
        },
        gross_profit={
            2011: 32_206_000,
            2012: 72_532_000,
            2013: 127_549_000,
            2014: 197_564_000,
            2015: 267_007_000,
            2016: 376_861_000,
            2017: 479_137_000,
            2018: 616_929_000,
            2019: 800_712_000,
            2020: 1_056_141_000,
        },
        operating_income={
            2011: 6_638_000,
            2012: 30_033_000,
            2013: 39_304_000,
            2014: 69_966_000,
            2015: 78_589_000,
            2016: 120_688_000,
            2017: 157_929_000,
            2018: 222_866_000,
            2019: 286_219_000,
            2020: 377_794_000,
        },
        net_income={
            2011: 4_230_000,
            2012: 18_783_000,
            2013: 23_615_000,
            2014: 40_383_000,
            2015: 54_460_000,
            2016: 77_572_000,
            2017: 151_177_000,
            2018: 229_832_000,
            2019: 301_118_000,
            2020: 379_998_000,
        },
        research_and_development={
            2011: 7_750_000,
            2012: 14_638_000,
            2013: 26_327_000,
            2014: 41_156_000,
            2015: 65_976_000,
            2016: 96_743_000,
            2017: 132_017_000,
            2018: 158_783_000,
            2019: 209_895_000,
            2020: 294_220_000,
        },
        selling_and_marketing={
            2011: 12_279_000,
            2012: 19_490_000,
            2013: 41_507_000,
            2014: 56_203_000,
            2015: 80_984_000,
            2016: 110_634_000,
            2017: 128_781_000,
            2018: 148_867_000,
            2019: 190_331_000,
            2020: 235_014_000,
        },
        general_and_administrative={
            2011: 5_539_000,
            2012: 8_371_000,
            2013: 20_411_000,
            2014: 30_239_000,
            2015: 41_458_000,
            2016: 48_796_000,
            2017: 60_410_000,
            2018: 86_413_000,
            2019: 114_267_000,
            2020: 149_113_000,
        },
    ),
)


class TestSECClient:

    @pytest.mark.parametrize(
        ("ticker", "cik", "sec_response", "expected_reports"),
        [
            ("VEEV", "0001393052", VEEV_RESPONSE_DATA, VEEVA),
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
