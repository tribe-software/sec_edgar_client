from contextlib import asynccontextmanager
from typing import AsyncIterator, Awaitable, Callable

from aiohttp import ClientSession, web
from aiohttp.test_utils import RawTestServer
from yarl import URL

from .central_index_key import CIKRepositoryInterface
from .client import SECGovEDGARClient, UserAgent

__all__ = (
    "Handler",

    "fake_sec_server_factory",
    "sec_client_factory",
)

Handler = Callable[[web.BaseRequest], Awaitable[web.Response]]


@asynccontextmanager
async def fake_sec_server_factory(
    handler: Handler,
) -> AsyncIterator[URL]:
    async with RawTestServer(handler) as server:
        yield server.make_url("/")


@asynccontextmanager
async def sec_client_factory(
    ciks: CIKRepositoryInterface,
    handler: Handler,
) -> AsyncIterator[URL]:
    async with ClientSession() as session:
        async with fake_sec_server_factory(handler) as url:
            user_agent = UserAgent(
                company="test company",
                user="test_user",
                email="user@gmail.com",
            )
            yield SECGovEDGARClient(session, url, ciks, user_agent)
