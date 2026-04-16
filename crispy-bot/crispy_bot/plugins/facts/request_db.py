import httpx


#fetch from api
async def fetch(facts_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url=facts_url)
        result = response.json()
        return result["text"]
