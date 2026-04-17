import litellm
import asyncio


# Translation
async def joke_generation(topic: str,
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
                "content": f"""
你是一个幽默风趣、擅长创作黑色幽默笑话的AI。请根据用户给出的主题，生成一个笑话。
你可以通过荒诞、讽刺、轻微冒犯性(对某件事物的批评或者刻板印象，但避免不好笑的纯冒犯)或反常规的角度制造笑点。

用户给出的主题是：{topic}

请直接输出笑话，不要额外解释。
"""
            }
        ]
    )
    return response.choices[0].message.content

