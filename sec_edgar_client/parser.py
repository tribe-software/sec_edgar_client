from datetime import date
from typing import Iterable, Mapping

import attr

from .entities import Balance, Income, Reports, Year

__all__ = (
    "SECResponseParser",
)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SECResponseParser:
    response: Mapping

    def parse_reports(self) -> Reports:
        return Reports(
            balance=self._parse_balance(),
            income=self._parse_income(),
        )

    def _parse_balance(self) -> Balance:
        return Balance(
            assets=self._get_statements(key="Assets"),
            equity=self._get_statements(key="StockholdersEquity"),
        )

    def _parse_income(self) -> Income:
        revenue = self._get_statements(key="Revenues")
        revenue_from_contracts = self._get_statements(
            key="RevenueFromContractWithCustomerExcludingAssessedTax",
        )
        return Income(
            revenue=revenue_from_contracts | revenue,
            gross_profit=self._get_statements(key="GrossProfit"),
            operating_income=self._get_statements(key="OperatingIncomeLoss"),
            net_income=self._get_statements(key="NetIncomeLoss"),
            research_and_development=self._get_statements(
                key="ResearchAndDevelopmentExpense",
            ),
            selling_and_marketing=self._get_statements(
                key="SellingAndMarketingExpense",
            ),
            general_and_administrative=self._get_statements(
                key="GeneralAndAdministrativeExpense",
            ),
        )

    def _get_statements(self, key: str) -> dict[Year, int]:
        statements = self.response["facts"]["us-gaap"][key]["units"]["USD"]
        annual_statements = _get_annual_statements(statements)
        sorted_annual_statements = _get_sorted_statements_by_actuality(
            annual_statements,
        )
        year_to_statement = _get_separated_year_and_value(
            sorted_annual_statements,
        )
        return {
            key: year_to_statement[key]
            for key in sorted(year_to_statement)
        }


def _get_annual_statements(statements: Iterable[Mapping]) -> Iterable[dict]:
    for statement in statements:
        if statement["form"] == "10-K":
            frame = statement.get("frame")
            if frame is None or _is_year_frame(frame):
                yield statement


def _get_separated_year_and_value(
    statements: Iterable[Mapping],
) -> dict[Year, int]:
    year_to_value = {}

    for statement in statements:
        frame = statement.get("frame")
        value = statement["val"]
        if frame is None:
            year = statement["fy"]
        else:
            year = _get_year_from_frame(statement["frame"])

        if year not in year_to_value:
            year_to_value[year] = value

    return year_to_value


def _is_year_frame(value: str) -> bool:
    without_prefix = value.removeprefix("CY")
    frame = without_prefix[4:]  # remove year
    return frame in {"", "Q4I"}


def _get_year_from_frame(frame_value: str) -> Year:
    return int(frame_value.removeprefix("CY")[:4])


def _get_sorted_statements_by_actuality(
    statements: Iterable[Mapping],
) -> Iterable[Mapping]:
    return sorted(statements, key=_sort_actuality_key, reverse=True)


def _sort_actuality_key(statement: Mapping) -> tuple[date, date]:
    period_end = date.fromisoformat(statement["end"])
    filled_at = date.fromisoformat(statement["filed"])
    return filled_at, period_end
