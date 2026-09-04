from services.sources import SourceService

class ContentFetcher:
    def __init__(self):
        self.service = SourceService()

    async def fetch(self, url: str) -> str:
        try:
            return await self.service.process_source(url, None)
        except Exception as e:
            return ""
