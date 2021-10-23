from datetime import date
from typing import Iterable, Mapping

import attr

from .utils import get_trimmed_to_same_len

__all__ = (
    "SECResponseParser",

    "Reports",
    "BalanceSnapshot",
)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class BalanceSnapshot:
    assets: int
    equity: int


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Reports:
    balance: tuple[BalanceSnapshot, ...]
    reported_at: tuple[date, ...]


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SECResponseParser:
    response: Mapping

    def parse_reports(self) -> Reports:
        # pylint: disable=unbalanced-tuple-unpacking
        assets, equity = get_trimmed_to_same_len(
            _get_statements(self.response, key="Assets"),
            _get_statements(self.response, key="StockholdersEquity"),
        )

        balance = tuple(
            BalanceSnapshot(asset_value, equity_value)
            for asset_value, equity_value in zip(
                assets.values(),
                equity.values(),
            )
        )
        return Reports(
            balance,
            reported_at=tuple(assets.keys()),
        )


def _get_statements(data: Mapping, key: str) -> Mapping[date, int]:
    statements = data["facts"]["us-gaap"][key]["units"]["USD"]
    annual_statements = _get_annual_statements(statements)
    sorted_annual_statements = _get_sorted_by_date(annual_statements)
    return _get_separated_date_and_value(sorted_annual_statements)


def _get_sorted_by_date(statements: Iterable[Mapping]) -> Iterable[Mapping]:
    return sorted(
        statements,
        key=lambda statement: (
            date.fromisoformat(statement["end"]), statement["fy"],
        ),
    )


def _get_annual_statements(statements: Iterable[Mapping]) -> Iterable[Mapping]:
    return (
        statement
        for statement in statements
        if statement["form"] == "10-K" and "frame" not in statement
    )


def _get_separated_date_and_value(
    statements: Iterable[Mapping],
) -> dict[date, int]:
    date_to_statement_value = {}

    for statement in statements:
        period_end = date.fromisoformat(statement["end"])

        if period_end not in date_to_statement_value:
            date_to_statement_value[period_end] = statement["val"]

    return date_to_statement_value
