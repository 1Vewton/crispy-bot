from nonebot import get_plugin_config, on_command, logger
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from utils import get_error

from .config import Config
from .data_fetch import fetch_from_url

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
weather_command = on_command(
    "weather"
)


# Test whether the private key presents
@weather_test.handle()
async def weather_test_process():
    result = "私钥已被读取，允许进行天气信息获取"
    if not private_key_ready:
        result = "私钥读取失败，天气信息调取无法成功"
    await weather_test.finish(result)


# When the weather command is started
@weather_command.handle()
async def weather_command(state:T_State, matcher: Matcher, args: Message = CommandArg()):
    try:
        if location := args.extract_plain_text():
            result = await fetch_from_url(
                private_key=private_key,
                key_id=config.key_id,
                project_id=config.project_id,
                url=f"https://{config.api_host}/geo/v2/city/lookup?location={location}"
            )
            # Store the data fetched
            data = result["location"]
            if len(data) == 0:
                await matcher.finish(f"对不起喵，Crispy没找到地点{location}")
            elif len(data) == 1:
                await matcher.send(f"查询{data[0]["name"]}的数据")
                state["data"] = data
            else:
                await matcher.send("Crispy发现了多个可能的位置喵，输入你想要查询的位置的编号: ")
                for idx, i in enumerate(data):
                    await matcher.send(f"编号: {idx}\n位置: {i["name"]}, {i["adm2"]}, {i["adm1"]}, {i["country"]}")
                state["data"] = data
        else:
            await matcher.finish("请输入要查询天气的地点")
    except Exception as e:
        await matcher.finish(get_error(e))

