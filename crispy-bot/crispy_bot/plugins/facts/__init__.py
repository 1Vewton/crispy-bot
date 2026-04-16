from nonebot import (
    get_plugin_config,
    on_command,
    logger
)
from nonebot.plugin import PluginMetadata
from utils import get_error

from .config import Config
from .request_db import fetch
from .llm import translate

__plugin_meta__ = PluginMetadata(
    name="facts",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

# fact command
fact = on_command(
    "fact"
)


# Fact process
@fact.handle()
async def fact_function():
    try:
        # Get info add translate
        logger.info("Starting to fetch fact")
        fact_info = await fetch(config.random_fact_url)
        logger.info("Start translation")
        translation = await translate(
            fact=fact_info,
            llm_provider=config.llm_provider,
            llm_api_key=config.llm_api_key,
            llm_model_name=config.llm_model_name,
            llm_base_url=config.llm_base_url
        )
        result = translation
    except Exception as e:
        result = get_error(e)
    await fact.finish(result)
