from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .command import help_command
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
help_command = help_command()
