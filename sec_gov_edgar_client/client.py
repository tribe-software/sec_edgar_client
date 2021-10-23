from functools import cached_property
from typing import Optional

import attr
import ujson
from aiohttp import ClientSession
from yarl import URL

from .central_index_key import CIKRepositoryInterface
from .parser import Reports, SECResponseParser

__all__ = (
    "SECGovEDGARClient",
    "UserAgent",
)


@attr.s(auto_attribs=True, frozen=True)
class UserAgent:
    company: str
    user: str
    email: str

    @cached_property
    def view(self) -> str:
        return f"{self.company} {self.user} <{self.email}>"


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SECGovEDGARClient:
    _session: ClientSession
    _url: URL
    _CIKs: CIKRepositoryInterface
    _user_agent: UserAgent = UserAgent(
        "Tribe.invest",
        "Danila Korobkov",
        "korobkov.danila.yurevich@gmail.com",
    )

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
        url = self._url / f"xbrl/companyfacts/CIK{cik}.json"
        async with self._session.get(
            url,
            headers=self._get_headers(),
        ) as response:
            data = await response.json(loads=ujson.loads)
            return SECResponseParser(data).parse_reports()

    def _get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": self._user_agent.view,
        }
