from nonebot import get_plugin_config, on_command, logger
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters import Message
from utils import get_error

from .config import Config
from .command import joke_cmd, mom_command
from .llm import joke_generation

__plugin_meta__ = PluginMetadata(
    name="joke",
    description="",
    usage="",
    config=Config,
)

# Commands
config = get_plugin_config(Config)
joke = joke_cmd()
mom = mom_command()
joke_generation_cmd = on_command(
    "joke"
)


# Joke generation
@joke_generation_cmd.handle()
async def generate_joke(args: Message = CommandArg()):
    try:
        logger.info("Start joke generation")
        if topic := args.extract_plain_text():
            result = await joke_generation(
                topic=topic,
                llm_provider=config.llm_provider,
                llm_api_key=config.llm_api_key,
                llm_model_name=config.llm_model_name,
                llm_base_url=config.llm_base_url
            )
        else:
            result = "请输入主题"
    except Exception as e:
        result = get_error(e)
    await joke_generation_cmd.finish(result)
