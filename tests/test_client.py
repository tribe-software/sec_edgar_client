# pylint: disable=too-many-statements

from datetime import date
from typing import Final
from unittest import mock

import pytest
from aiohttp import ClientSession, web
from yarl import URL

from sec_gov_edgar_client import (
    BalanceSnapshot,
    CIKRepositoryInterface,
    Report,
    Reports,
    SECGovEDGARClient,
)
from sec_gov_edgar_client.test_utils import Handler, fake_sec_server_factory

from .example_data import VEEV_RESPONSE_DATA, Z_RESPONSE_DATA

VEEVA: Final = Reports(
    annual=Report(
        balance={
            date(2014, 1, 31): BalanceSnapshot(
                assets=370_308_000,
                stockholders_equity=280_096_000,
            ),
            date(2015, 1, 31): BalanceSnapshot(
                assets=544_890_000,
                stockholders_equity=406_833_000,
            ),
            date(2016, 1, 31): BalanceSnapshot(
                assets=705_799_000,
                stockholders_equity=505_249_000,
            ),
            date(2017, 1, 31): BalanceSnapshot(
                assets=917_700_000,
                stockholders_equity=652_978_000,
            ),
            date(2018, 1, 31): BalanceSnapshot(
                assets=1_197_008_000,
                stockholders_equity=871_527_000,
            ),
            date(2019, 1, 31): BalanceSnapshot(
                assets=1_653_766_000,
                stockholders_equity=1_237_749_000,
            ),
            date(2020, 1, 31): BalanceSnapshot(
                assets=2_271_777_000,
                stockholders_equity=1_665_594_000,
            ),
            date(2021, 1, 31): BalanceSnapshot(
                assets=3_046_067_000,
                stockholders_equity=2_266_320_000,
            ),
        },
    ),
)


ZILLOW: Final = Reports(
    annual=Report(
        balance={
            date(2015, 12, 31): BalanceSnapshot(
                assets=3_135_700_000,
                stockholders_equity=2_679_053_000,
            ),
            date(2016, 12, 31): BalanceSnapshot(
                assets=3_149_677_000,
                stockholders_equity=2_533_587_000,
            ),
            date(2017, 12, 31): BalanceSnapshot(
                assets=3_230_517_000,
                stockholders_equity=2_660_823_000,
            ),
            date(2018, 12, 31): BalanceSnapshot(
                assets=4_291_116_000,
                stockholders_equity=3_267_179_000,
            ),
            date(2019, 12, 31): BalanceSnapshot(
                assets=6_131_973_000,
                stockholders_equity=3_435_421_000,
            ),
            date(2020, 12, 31): BalanceSnapshot(
                assets=7_486_560_000,
                stockholders_equity=4_741_816_000,
            ),
        },
    ),
)


@pytest.mark.parametrize(
    ("ticker", "cik", "response", "expected_reports"),
    [
        ("VEEV", "0001393052", VEEV_RESPONSE_DATA, VEEVA),
        ("Z", "0001617640", Z_RESPONSE_DATA, ZILLOW),
    ],
)
async def test__get_reports__match(
    ticker: str,
    cik: str,
    response: dict,
    expected_reports: Reports,
) -> None:
    ciks = mock.create_autospec(CIKRepositoryInterface)
    ciks.find.return_value = cik

    async def handler(request: web.Request) -> web.Response:
        assert request.path == f"/xbrl/companyfacts/CIK{cik}.json"
        return web.json_response(response)

    handler_proxy = mock.AsyncMock(wraps=handler, spec=Handler)

    async with ClientSession() as session:
        async with fake_sec_server_factory(handler_proxy) as url:
            client = SECGovEDGARClient(session, url, ciks)
            reports = await client.get_reports(ticker)

    assert reports == expected_reports
    handler_proxy.assert_awaited_once()


async def test__get_reports__missing_ticker__return_none() -> None:
    ciks = mock.create_autospec(CIKRepositoryInterface)
    ciks.find.return_value = None

    async with ClientSession() as session:
        sec = SECGovEDGARClient(session, URL(), ciks)
        reports = await sec.get_reports(ticker="missing")

    assert reports is None
