from nonebot import get_plugin_config, on_notice
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import PokeNotifyEvent
from utils import get_random_sentence

from .config import Config
from .command import introduction_cmd

__plugin_meta__ = PluginMetadata(
    name="whoami",
    description="",
    usage="",
    config=Config,
)

# Commands
config = get_plugin_config(Config)
introduction = introduction_cmd()
# on_notice
poke_handler = on_notice()


# When poked, show it to user
@poke_handler.handle()
async def handle_poke(event: PokeNotifyEvent):
    if event.is_tome():
        await poke_handler.finish(get_random_sentence())
