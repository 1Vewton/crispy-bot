from nonebot import get_plugin_config, on_command
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="weather",
    description="",
    usage="",
    config=Config,
)

# Config
config = get_plugin_config(Config)
private_key_ready = False
try:
    with open(config.private_key_qweather_path, "r") as f:
        private_key_ready = True
        private_key = f.read()
except FileNotFoundError:
    private_key = "No key exists."

# Commands
weather_test = on_command(
    "testWeatherCommand"
)


# Test whether the private key presents
@weather_test.handle()
async def weather_test_process():
    result = "私钥已被读取，允许进行天气信息获取"
    if not private_key_ready:
        result = "私钥读取失败，天气信息调取无法成功"
    await weather_test.finish(result)

