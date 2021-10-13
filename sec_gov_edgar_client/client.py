from datetime import date
from typing import Iterable, Mapping, Optional

import attr
import ujson
from aiohttp import ClientSession
from yarl import URL

from .central_index_key import CIKRepositoryInterface

__all__ = (
    "Reports",
    "Report",
    "BalanceSnapshot",
    "SECGovEDGARClient",
)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class BalanceSnapshot:
    assets: int
    stockholders_equity: int


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Report:
    balance: Mapping[date, BalanceSnapshot]


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Reports:
    annual: Report


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SECGovEDGARClient:
    _session: ClientSession
    _url: URL
    _CIKs: CIKRepositoryInterface

    async def get_reports(
        self,
        ticker: str,
    ) -> Optional[Reports]:
        cik = await self._CIKs.find(ticker)
        if cik is None:
            return None
        return await self._get_reports(cik)

    async def _get_reports(
        self,
        cik: str,
    ) -> Reports:
        url = self._url.with_path(f"xbrl/companyfacts/CIK{cik}.json")
        async with self._session.get(url) as response:
            data = await response.json(loads=ujson.loads)

            assets = _get_statements(data, key="Assets")
            stockholders_equity = _get_statements(
                data,
                key="StockholdersEquity",
            )
            stockholders_equity = {
                key: value
                for key, value in stockholders_equity.items()
                if key in assets
            }

            balance = {
                reported_at: BalanceSnapshot(
                    asset,
                    stockholders_equity[reported_at],
                )
                for reported_at, asset in assets.items()
            }
            return Reports(
                annual=Report(balance),
            )


def _get_statements(data: dict, key: str) -> dict[date, int]:
    statements = data["facts"]["us-gaap"][key]["units"]["USD"]
    sorted_statements = _sort_by_period_end(statements)
    annual_statements = list(_filter_annual_statements(sorted_statements))
    return _get_date_value(annual_statements)


def _sort_by_period_end(statements: Iterable[dict]) -> Iterable[dict]:
    return sorted(
        statements,
        key=lambda statement: (
            date.fromisoformat(statement["end"]), statement["fy"],
        ),
    )


def _filter_annual_statements(statements: Iterable[dict]) -> Iterable[dict]:
    return (
        statement
        for statement in statements
        if statement["form"] == "10-K" and "frame" not in statement
    )


def _get_date_value(statements: Iterable[dict]) -> dict[date, int]:
    res = {}
    for statement in statements:
        end = date.fromisoformat(statement["end"])
        if end not in res:
            res[end] = statement["val"]
    return res
