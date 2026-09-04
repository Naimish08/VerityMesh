from tavily import AsyncTavilyClient
from config import settings

class TavilySearchTool:
    def __init__(self):
        self.client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)

    async def search(self, query: str, max_results: int = 5):
        try:
            response = await self.client.search(query=query, max_results=max_results, search_depth="basic")
            return response.get("results", [])
        except Exception as e:
            return []
