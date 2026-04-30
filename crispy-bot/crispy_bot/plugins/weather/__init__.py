from nonebot import (
    get_plugin_config,
    on_command,
    logger
)
from nonebot.exception import FinishedException, RejectedException
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import (
    CommandArg,
    ArgPlainText
)
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message as OneBotMessage
from requests import RequestException

from utils import get_error

from .config import Config
from .data_fetch import fetch_from_url
from .llm import read_real_weather, read_weather_forecast

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
    "testWeatherCommand",
    priority=2,
    block=True
)
weather_command = on_command(
    "weather",
    priority=1,
    block=True
)
forecast_command = on_command(
    "forecast",
    priority=1,
    block=True
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
async def weather_process(state:T_State, matcher: Matcher, args: Message = CommandArg()):
    try:
        if location := args.extract_plain_text():
            logger.info("Start fetching city data")
            result = await fetch_from_url(
                private_key=private_key,
                key_id=config.key_id,
                project_id=config.project_id,
                url=f"https://{config.api_host}/geo/v2/city/lookup?location={location}"
            )
            # Store the data fetched
            if "location" not in result.keys():
                await matcher.finish(f"对不起喵，Crispy没找到地点{location}")
            data = result["location"]
            if len(data) == 0:
                await matcher.finish(f"对不起喵，Crispy没找到地点{location}")
            elif len(data) == 1:
                await matcher.send(f"查询{data[0]["name"]}的数据")
                state["data"] = data
                state["selected_idx"] = OneBotMessage("0")
            else:
                await matcher.send(
f"""Crispy根据你的输入找到了多个可能的位置喵，输入你想要查询的位置的编号: \n\n{
"".join([f"编号: {idx}\n位置: {i["name"]}, {i["adm2"]}, {i["adm1"]}, {i["country"]}\n\n" for idx, i in enumerate(data)])
}"""
                )
                state["data"] = data
        else:
            await matcher.finish("请输入要查询天气的地点")
    except FinishedException:
        raise
    except RejectedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# Post processing
@weather_command.got("selected_idx", prompt="输入你想要的查询天气的位置的编号")
async def weather_process_post(state: T_State, matcher: Matcher, selected_idx: str=ArgPlainText()):
    try:
        # Pre-test checks
        try_count = state.get("try_count", 0)
        if try_count >= 3:
            await matcher.finish("不要浪费Crispy的时间！😡")
        data = state.get("data", [])
        if len(data) == 0:
            raise Exception("Data loss")
        # Test the selected idx
        if not selected_idx.isdigit():
            try_count += 1
            state["try_count"] = try_count
            await matcher.reject("baka，编号至少要是数字吧")
        elif int(selected_idx) < 0 or int(selected_idx) >= len(data):
            try_count += 1
            state["try_count"] = try_count
            await matcher.reject("你输入的编号不在合法编号范围内")
        else:
            # Get the weather data
            location_data = data[int(selected_idx)]
            location_id = location_data["id"]
            logger.info("Start fetching weather data")
            result = await fetch_from_url(
                private_key=private_key,
                key_id=config.key_id,
                project_id=config.project_id,
                url=f"https://{config.api_host}/v7/weather/now?location={location_id}"
            )
            if "now" not in result.keys():
                await matcher.finish("对不起，Crispy没有获取到合适的天气信息")
            else:
                weather_result = await read_real_weather(
                    weather_result=result,
                    position=f"{location_data["name"]}, {location_data["adm2"]}, {location_data["adm1"]}, {location_data["country"]}",
                    llm_api_key=config.llm_api_key,
                    llm_base_url=config.llm_base_url,
                    llm_model_name=config.llm_model_name,
                    llm_provider=config.llm_provider
                )
                await matcher.finish(weather_result)
    except FinishedException:
        raise
    except RejectedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# When the forecast command is started
@forecast_command.handle()
async def forecast_process(state:T_State, matcher: Matcher, args: Message = CommandArg()):
    try:
        if location := args.extract_plain_text():
            logger.info("Start fetching city data")
            result = await fetch_from_url(
                private_key=private_key,
                key_id=config.key_id,
                project_id=config.project_id,
                url=f"https://{config.api_host}/geo/v2/city/lookup?location={location}"
            )
            # Store the data fetched
            if "location" not in result.keys():
                await matcher.finish(f"对不起喵，Crispy没找到地点{location}")
            data = result["location"]
            if len(data) == 0:
                await matcher.finish(f"对不起喵，Crispy没找到地点{location}")
            elif len(data) == 1:
                await matcher.send(f"查询{data[0]["name"]}的数据")
                state["data"] = data
                state["selected_idx"] = OneBotMessage("0")
            else:
                await matcher.send(
f"""Crispy根据你的输入找到了多个可能的位置喵，输入你想要查询的位置的编号: \n\n{
"".join([f"编号: {idx}\n位置: {i["name"]}, {i["adm2"]}, {i["adm1"]}, {i["country"]}\n\n" for idx, i in enumerate(data)])
}"""
                )
                state["data"] = data
        else:
            await matcher.finish("请输入要查询天气的地点")
    except FinishedException:
        raise
    except RejectedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# Forecast: Get the actual position
@forecast_command.got("selected_idx", prompt="输入你想要的查询天气的位置的编号")
async def weather_process_get_position(state: T_State, matcher: Matcher, selected_idx: str=ArgPlainText()):
    try:
        # Pre-test checks
        try_count = state.get("try_count", 0)
        if try_count >= 3:
            await matcher.finish("不要浪费Crispy的时间！😡")
        data = state.get("data", [])
        if len(data) == 0:
            raise Exception("Data loss")
        # Test the selected idx
        if not selected_idx.isdigit():
            try_count += 1
            state["try_count"] = try_count
            await matcher.reject("baka，编号至少要是数字吧")
        elif int(selected_idx) < 0 or int(selected_idx) >= len(data):
            try_count += 1
            state["try_count"] = try_count
            await matcher.reject("你输入的编号不在合法编号范围内")
        else:
            state["selected_idx_int"] = int(selected_idx)
            await matcher.send(f"已获取用户想要查询的地址: {data[int(selected_idx)]['name']}")
    except FinishedException:
        raise
    except RejectedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# Forecast get weather forecast
@forecast_command.got("forecast_times", prompt="请输入要进行天气预报的未来天数(支持天数: 3, 7, 10, 15, 30)")
async def weather_forecast(state: T_State, matcher: Matcher, forecast_times: str=ArgPlainText()):
    try:
        # If the try count for forecasting is over 3
        forecast_try_count = state.get("forecast_try_count", 0)
        if forecast_try_count >= 3:
            await matcher.finish("不要浪费Crispy的时间！😡")
        # Data checking
        if not forecast_times.isdigit():
            await matcher.reject("baka，进行天气预报的天数要是数字吧!")
        if not forecast_times in ["3", "7", "10", "15", "30"]:
            await matcher.reject("你输入的预测天数不在支持天数中(3, 7, 10, 15, 30)")
        else:
            # Forecast result fetching
            data = state.get("data", [])
            if len(data) == 0:
                raise Exception("Data loss")
            selected_idx_int = state.get("selected_idx_int", 0)
            location_data = data[selected_idx_int]
            location_id = location_data["id"]
            # Start fetching
            logger.info("Start fetching weather forecast result")
            url = f"https://{config.api_host}/v7/weather/{forecast_times}d?location={location_id}"
            result = await fetch_from_url(
                private_key=private_key,
                key_id=config.key_id,
                project_id=config.project_id,
                url=url
            )
            if "daily" not in result.keys():
                await matcher.finish("对不起喵，Crispy没有找到合适的天气数据")
            else:
                weather_result = await read_weather_forecast(
                    weather_result=result,
                    position=f"{location_data["name"]}, {location_data["adm2"]}, {location_data["adm1"]}, {location_data["country"]}",
                    llm_api_key=config.llm_api_key,
                    llm_base_url=config.llm_base_url,
                    llm_model_name=config.llm_model_name,
                    llm_provider=config.llm_provider
                )
                await matcher.finish(weather_result)
    except FinishedException:
        raise
    except RejectedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))
