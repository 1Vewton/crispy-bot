import litellm


# Translation
async def joke_generation(
                    topic: str,
                    llm_provider: str,
                    llm_model_name: str,
                    llm_base_url: str,
                    llm_api_key: str,
                    prompt: str) -> str:
    response = await litellm.acompletion(
        model=f"{llm_provider}/{llm_model_name}",
        base_url=llm_base_url,
        api_key=llm_api_key,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content