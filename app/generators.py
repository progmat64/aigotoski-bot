# Asynchronous Example
import asyncio
from mistralai import Mistral
import os
from config import AI_TOKEN


async def generate(content):
    async with Mistral(
        api_key=AI_TOKEN,
    ) as mistral:
        # model можно менять
        res = await mistral.chat.complete_async(model="mistral-small-latest", messages=[
            {
                "content": content,
                "role": "user",
            },
        ])

        assert res is not None
        return res
