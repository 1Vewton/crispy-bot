from utils import get_encoding_jwt
import httpx


# Fetch from the url-qweather
async def fetch_from_url(
        private_key: str,
        project_id: str,
        key_id: str,
        url: str,
):
    # Get jwt
    jwt = get_encoding_jwt(
        private_key=private_key,
        project_id=project_id,
        kid=key_id
    )
    headers = {
        "Authorization": f"Bearer {jwt}",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url)
    return response.json()
