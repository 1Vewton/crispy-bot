import litellm
import asyncio


# Translation
async def translate(fact: str,
                    llm_provider: str,
                    llm_model_name: str,
                    llm_base_url: str,
                    llm_api_key: str) -> str:
    response = await litellm.acompletion(
        model=f"{llm_provider}/{llm_model_name}",
        base_url=llm_base_url,
        api_key=llm_api_key,
        messages=[
            {
                "role": "user",
                "content": f"翻译以下内容{fact}到自然连贯的中文且只返回翻译的结果，**不要返回除了翻译后的文本以外的其他任何内容!!!**"
            }
        ]
    )
    return response.choices[0].message.content

