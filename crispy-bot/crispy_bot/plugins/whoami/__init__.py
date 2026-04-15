from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config
from .command import introduction_cmd

__plugin_meta__ = PluginMetadata(
    name="whoami",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
introduction = introduction_cmd()

