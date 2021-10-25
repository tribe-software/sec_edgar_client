from typing import Mapping

import attr

__all__ = (
    "Reports",
    "Balance",
    "Income",
    "Year",
)

Year = int
YearToValueMapping = Mapping[Year, int]


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Balance:
    assets: YearToValueMapping
    equity: YearToValueMapping


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Income:
    revenue: YearToValueMapping
    gross_profit: YearToValueMapping
    operating_income: YearToValueMapping
    net_income: YearToValueMapping
    research_and_development: YearToValueMapping
    selling_and_marketing: YearToValueMapping
    general_and_administrative: YearToValueMapping


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Reports:
    balance: Balance
    income: Income
