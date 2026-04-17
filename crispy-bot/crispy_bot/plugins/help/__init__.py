from nonebot import get_plugin_config, on_command
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
# Version command
version_command = on_command(
    "version"
)


@version_command.handle()
async def version_proces():
    return config.version
