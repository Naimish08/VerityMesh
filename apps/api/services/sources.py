import httpx
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("veritymesh.sources")

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

class SourceService:
    async def fetch_url(self, url: str) -> str:
        async with httpx.AsyncClient(
            headers=DEFAULT_HEADERS,
            timeout=15.0,
            follow_redirects=True,
            verify=False,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def parse_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            script.extract()
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean = '\n'.join(chunk for chunk in chunks if chunk)
        return clean

    async def process_source(self, url: str, research_run_id: str | None = None) -> str:
        html = await self.fetch_url(url)
        clean_text = self.parse_html(html)
        return clean_text
