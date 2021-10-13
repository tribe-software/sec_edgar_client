from contextlib import asynccontextmanager
from typing import AsyncIterator, Awaitable, Callable

from aiohttp import web
from aiohttp.test_utils import RawTestServer
from yarl import URL

__all__ = (
    "Handler",

    "fake_sec_server_factory",
)

Handler = Callable[[web.BaseRequest], Awaitable[web.Response]]


@asynccontextmanager
async def fake_sec_server_factory(
    handler: Handler,
) -> AsyncIterator[URL]:
    async with RawTestServer(handler) as server:
        yield server.make_url("/")
