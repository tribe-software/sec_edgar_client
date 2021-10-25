from abc import ABC, abstractmethod
from datetime import date
from functools import reduce
from typing import Iterable, Mapping

import attr

from .entities import Balance, Income, Reports, Year

__all__ = (
    "SECResponseParser",
)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class StatementParser(ABC):

    @abstractmethod
    def __call__(self, sec_response: Mapping) -> Mapping:
        pass


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SingleKeyStatementParser(StatementParser):
    key: str = attr.ib(kw_only=True)
    required: bool = attr.ib(kw_only=True, default=True)

    def __call__(self, sec_response: Mapping) -> Mapping:
        try:
            statements = (
                sec_response["facts"]["us-gaap"][self.key]["units"]["USD"]
            )
        except KeyError as e:
            if not self.required:
                return {}
            raise RuntimeError(f"Missing required key: {self.key}") from e

        annual_statements = _get_sorted_statements_by_actuality(
            _get_annual_statements(statements),
        )
        year_to_statement_value = _get_separated_year_and_value(
            annual_statements,
        )
        return {
            key: year_to_statement_value[key]
            for key in sorted(year_to_statement_value)
        }


@attr.s(auto_attribs=True, slots=True, frozen=True)
class JoinStatementParser(StatementParser):
    parsers: tuple[StatementParser, ...]

    def __call__(self, sec_response: Mapping) -> Mapping:
        statements = tuple(parser(sec_response) for parser in self.parsers)
        joined_statements = reduce(dict.__or__, reversed(statements), {})
        return joined_statements


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
            self._parse_assets(),
            self._parse_equity(),
        )

    def _parse_income(self) -> Income:
        return Income(
            self._parse_revenue(),
            self._parse_gross_profit(),
            self._parse_operating_income(),
            self._parse_net_income(),
            self._parse_research_and_development(),
            self._parse_selling_and_marketing(),
            self._parse_general_and_administrative(),
        )

    def _parse_assets(self) -> Mapping:
        parser = SingleKeyStatementParser(key="Assets")
        return parser(self.response)

    def _parse_equity(self) -> Mapping:
        parser = SingleKeyStatementParser(key="StockholdersEquity")
        return parser(self.response)

    def _parse_revenue(self) -> Mapping:
        parser = JoinStatementParser(
            (
                SingleKeyStatementParser(key="Revenues", required=False),
                SingleKeyStatementParser(
                    key="RevenueFromContractWithCustomerExcludingAssessedTax",
                    required=False,  # TODO,
                ),
            ),
        )
        return parser(self.response)

    def _parse_gross_profit(self) -> Mapping:
        parser = SingleKeyStatementParser(key="GrossProfit", required=False)
        return parser(self.response)

    def _parse_operating_income(self) -> Mapping:
        parser = SingleKeyStatementParser(key="OperatingIncomeLoss")
        return parser(self.response)

    def _parse_net_income(self) -> Mapping:
        parser = SingleKeyStatementParser(key="NetIncomeLoss")
        return parser(self.response)

    def _parse_research_and_development(self) -> Mapping:
        parser = SingleKeyStatementParser(
            key="ResearchAndDevelopmentExpense",
            required=False,
        )
        return parser(self.response)

    def _parse_selling_and_marketing(self) -> Mapping:
        parser = SingleKeyStatementParser(
            key="SellingAndMarketingExpense",
            required=False,
        )
        return parser(self.response)

    def _parse_general_and_administrative(self) -> Mapping:
        parser = SingleKeyStatementParser(
            key="GeneralAndAdministrativeExpense",
            required=False,
        )
        return parser(self.response)


def _get_annual_statements(statements: Iterable[Mapping]) -> Iterable[dict]:
    for statement in statements:
        if statement["form"] == "10-K":
            frame = statement.get("frame")
            if frame is None or _is_year_frame(frame):
                yield statement


def _get_sorted_statements_by_actuality(
    statements: Iterable[Mapping],
) -> Iterable[Mapping]:
    return sorted(statements, key=_sort_actuality_key, reverse=True)


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


def _sort_actuality_key(statement: Mapping) -> tuple[date, date]:
    period_end = date.fromisoformat(statement["end"])
    filled_at = date.fromisoformat(statement["filed"])
    return filled_at, period_end
