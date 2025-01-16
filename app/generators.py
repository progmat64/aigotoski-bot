from mistralai import Mistral

from config import AI_TOKEN


async def generate(content):
    async with Mistral(api_key=AI_TOKEN) as mistral:
        response = await mistral.chat.complete_async(
            model="mistral-small-latest", messages=[{"content": content, "role": "user"}]
        )
        return response
