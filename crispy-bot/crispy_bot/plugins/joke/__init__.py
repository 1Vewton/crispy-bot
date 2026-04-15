from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from .command import joke_cmd

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="joke",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
joke = joke_cmd()

