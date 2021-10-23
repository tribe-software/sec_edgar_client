import asyncio
from pathlib import Path

from aiohttp import ClientSession
from yarl import URL

from sec_edgar_client import LocalFileCIKRepository, SECClient, UserAgent

ROOT_DIR = Path(__file__).parents[1]
CIKS_FILE_FROM_TEST = (
    ROOT_DIR / "tests" / "example_data" / "ticker_to_cik_mapping.txt"
)


async def main() -> None:
    url = URL("https://data.sec.gov/api")
    ciks = LocalFileCIKRepository(file=CIKS_FILE_FROM_TEST)
    user_agent = UserAgent(
        company="Example company",
        user="Danila Korobkov",
        email="example.mail@gmail.com",
    )
    async with ClientSession() as session:
        sec = SECClient(session, url, ciks, user_agent)
        reports = await sec.get_reports(ticker="VEEV")
        print(reports)

if __name__ == "__main__":
    asyncio.run(main())
