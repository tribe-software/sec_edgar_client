import asyncio
from pathlib import Path

from aiohttp import ClientSession
from yarl import URL

from sec_gov_edgar_client import LocalFileCIKRepository, SECGovEDGARClient


async def main() -> None:
    sec_url = URL("https://data.sec.gov/api")
    ciks = LocalFileCIKRepository(
        Path(
            "/Users/dkorobkov/tribe/sec_gov_edgar_client/"
            "tests/example_data/ticker_to_cik_mapping.txt",
        ),
    )
    async with ClientSession() as session:
        sec = SECGovEDGARClient(
            session,
            sec_url,
            ciks,
        )
        for ticker in "ABBV", "MNST", "QTWO", "AAPL":
            res = await sec.get_reports(ticker)
            print(res)

if __name__ == "__main__":
    asyncio.run(main())
