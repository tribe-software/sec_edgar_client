from typing import Mapping

import attr

__all__ = (
    "Reports",
    "Balance",
    "Income",
    "Year",
)

Year = int


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Balance:
    assets: Mapping[Year, int]
    equity: Mapping[Year, int]


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Income:
    revenue: Mapping[Year, int]
    gross_profit: Mapping[Year, int]
    operating_income: Mapping[Year, int]
    net_income: Mapping[Year, int]
    research_and_development: Mapping[Year, int]
    selling_and_marketing: Mapping[Year, int]
    general_and_administrative: Mapping[Year, int]


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Reports:
    balance: Balance
    income: Income
