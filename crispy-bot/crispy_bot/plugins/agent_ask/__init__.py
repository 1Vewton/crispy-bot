from nonebot import require
require("crispy_bot.plugins.data_manager")
require("nonebot_plugin_session")
require("nonebot_plugin_chatrecorder")
# utilities
from uuid import uuid4
import json
from datetime import datetime, timedelta
import random
# Sqlalchemy
from sqlalchemy import select, update
# nonebot dependencies
from nonebot import (
    get_plugin_config,
    on_command,
    logger,
    on_message
)
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.exception import FinishedException, RejectedException
from nonebot.internal.params import ArgPlainText
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageEvent,
    GROUP,
    Bot,
    MessageSegment,
    Event
)
# other plugins
from crispy_bot.plugins.data_manager import UserModel, GroupModel
from nonebot_plugin_orm import get_session
from nonebot_plugin_chatrecorder import get_messages
from nonebot_plugin_session import extract_session
# project dependencies
from .config import Config
from utils import get_error
from .agent import agent
from .prompt import process_prompt_test, process_prompt_answer
from .llm import invoke_agent

__plugin_meta__ = PluginMetadata(
    name="agent_ask",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

# agent
agent = agent(
    llm_model_name=config.llm_model_name,
    llm_api_key=config.llm_api_key,
    llm_base_url=config.llm_base_url
)

# Commands
ask = on_command(
    "ask",
    aliases={
        "询问"
    },
    priority=1,
    block=True
)
thinking_mode_setting = on_command(
    "thinkingModeSetting",
    aliases={
        "思考设置"
    },
    priority=1,
    block=True
)
group_thinking_mode_setting = on_command(
    "groupThinkingModeSetting",
    aliases={
        "群思考设置"
    },
    priority=1,
    block=True
)
auto_answer_setting = on_command(
    "autoAnswerSetting",
    aliases={
        "自动回答设置"
    },
    priority=1,
    block=True
)

# Message checking
quick_answer = on_message(
    permission=GROUP,
    block=True,
    priority=10,
)


# Process
@ask.handle()
async def process_ask(
        event:GroupMessageEvent,
        matcher: Matcher,
        args: Message = CommandArg()):
    logger.info("Start process user's ask")
    try:
        question = args.extract_plain_text()
        if question:
            # Generate context id
            context_id = str(uuid4())
            # Find user info
            user_id = event.user_id
            group_id = event.group_id
            is_thinking_shown = True
            # Start session process
            session = get_session()
            async with session.begin():
                user = await session.get(UserModel, user_id)
                if not user:
                    new_user = UserModel(
                        id=user_id
                    )
                    await session.merge(new_user)
                    await session.commit()
                else:
                    is_thinking_shown = user.show_agent_thinking
            session = get_session()
            async with session.begin():
                group = await session.get(GroupModel, group_id)
                if not group:
                    new_group = GroupModel(
                        id=group_id
                    )
                    await session.merge(new_group)
                    await session.commit()
                else:
                    if is_thinking_shown:
                        is_thinking_shown = group.show_agent_thinking
            # Show info
            if is_thinking_shown:
                await matcher.send(f"正在处理{user_id}的请求，context编号{context_id}")
            # Start agent initialization
            await agent.initialize(
                mcp_url=config.exa_url,
                api_key=config.exa_api_key,
                tool_timeout_seconds=config.tool_timeout
            )
            async for chunk in agent.streaming(question, context_id):
                if chunk.step == "finish":
                    await matcher.finish(chunk.content)
                elif chunk.step == "error":
                    await matcher.finish(get_error(Exception(chunk.content)))
                elif chunk.step == "model":
                    if is_thinking_shown:
                        await matcher.send(f"🤔🤔🤔Crispy正在思考中...🤔🤔🤔:\n{chunk.content}")
        else:
            await matcher.finish("请输入问题")
    except FinishedException:
        raise
    except Exception as e:
        # Error display
        await matcher.finish(get_error(e))


# On message process
@quick_answer.handle()
async def process_quick_answer(bot: Bot,
                               event: MessageEvent,
                               group_event: GroupMessageEvent,
                               matcher: Matcher):
    # Check whether the bot is speaking
    if event.get_user_id() == bot.self_id:
        await matcher.finish()
    # Get possibility
    session = get_session()
    possibility = 0.0
    async with session.begin():
        group_id = group_event.group_id
        group = await session.get(GroupModel, group_id)
        if not group:
            new_group = GroupModel(
                id=group_id
            )
            await session.merge(new_group)
            await session.commit()
        else:
            possibility = group.auto_answer_possibility
    # Start the main process
    logger.info("Finish checking")
    if random.random() > possibility:
        logger.info("The bot would not answer the question")
        await matcher.finish()
    try:
        # Get message
        message = event.get_plaintext()
        message_id = event.message_id
        # Get message records
        records = await get_messages(
            user_ids=[str(event.user_id)],
            scene_ids=[str(group_event.group_id)],
            time_start=datetime.utcnow() - timedelta(hours=1)
        )
        # Find whether the user need answer
        test_prompt = process_prompt_test(message, records)
        result = await invoke_agent(
            llm_provider=config.llm_provider,
            llm_api_key=config.llm_api_key,
            llm_base_url=config.llm_base_url,
            llm_model_name=config.llm_model_name,
            prompt=test_prompt
        )
        logger.info(result)
        json_res = json.loads(result)
        if json_res["need_answer"]:
            answer_prompt = process_prompt_answer(
                user_message=message,
                question=json_res["question"],
                records=records,
            )
            logger.info(answer_prompt)
            answer_result = await invoke_agent(
                llm_provider=config.llm_provider,
                llm_api_key=config.llm_api_key,
                llm_base_url=config.llm_base_url,
                llm_model_name=config.llm_model_name,
                prompt=answer_prompt
            )
            result_message = MessageSegment.reply(message_id) + MessageSegment.text(f"{answer_result}\n[提示]本消息为Crispy自动回答生成，不保障其时效性以及准确性，请使用ask命令来进行专业化的问答(输入help命令来获取更多信息)")
            await matcher.finish(result_message)
        else:
            await matcher.finish()
    except FinishedException:
        raise
    except Exception as e:
        logger.error(e)


# Thinking mode setting
@thinking_mode_setting.handle()
async def setting_thinking_mode(
        state: T_State,
        event: GroupMessageEvent,
        matcher: Matcher
):
    try:
        # Get basic user id
        user_id = event.user_id
        session = get_session()
        # Read data from the db
        show_thinking_mode = True
        async with session.begin():
            user = await session.get(UserModel, user_id)
            if not user:
                new_user = UserModel(
                    id=user_id
                )
                await session.merge(new_user)
                await session.commit()
            else:
                show_thinking_mode = user.show_agent_thinking
        state["show_thinking_mode"] = show_thinking_mode
        # Show it to user
        readable_word = "显示"
        readable_word_inverse = "隐藏"
        if not show_thinking_mode:
            readable_word = "隐藏"
            readable_word_inverse = "显示"
        info = f"当前思维链设置: {readable_word}，是否将设置更改为{readable_word_inverse}"
        await matcher.send(info)
    except FinishedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# Thinking mode asking
@thinking_mode_setting.got("yes_no", "请输入'是/否'或者'yes/no'")
async def setting_thinking_mode_final(
        state: T_State,
        event: GroupMessageEvent,
        matcher: Matcher,
        yes_no: str = ArgPlainText()
):
    try:
        # Checking input
        maximum_try_count = state.get("maximum_try_count", 0)
        if maximum_try_count >= 3:
            await matcher.finish("不要浪费Crispy的时间！😡")
        if yes_no not in ["yes", "no", "是", "否"]:
            maximum_try_count += 1
            state["maximum_try_count"] = maximum_try_count
            await matcher.reject("请输入'yes/no/是/否'中的一个")
        else:
            if yes_no == "yes" or yes_no == "是":
                user_id = event.user_id
                show_thinking_mode = state.get("show_thinking_mode", True)
                session = get_session()
                async with session.begin():
                    user = await session.get(UserModel, user_id)
                    if not user:
                        new_user = UserModel(
                            id=user_id,
                            show_agent_thinking=(not show_thinking_mode)
                        )
                        await session.merge(new_user)
                    else:
                        await session.execute(
                            update(UserModel)
                            .where(UserModel.id == user_id)
                            .values(show_agent_thinking=(not show_thinking_mode))
                        )
                await matcher.finish("设置完成")
            else:
                await matcher.finish("按照用户要求不更改设置")
    except RejectedException:
        raise
    except FinishedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# Group thinking mode setting
@group_thinking_mode_setting.handle()
async def group_setting_thinking_mode(
        state: T_State,
        event: GroupMessageEvent,
        matcher: Matcher
):
    try:
        # Get basic group id
        group_id = event.group_id
        user_role = event.sender.role
        user_id = event.user_id
        if user_role == "owner":
            await matcher.send("用户为群主，允许进行设置")
        elif user_role == "admin":
            await matcher.send("用户为群主，允许进行设置")
        elif user_id == config.administrator_id:
            await matcher.send("用户为开发者，允许进行设置，遵循svm的指令🫡")
        else:
            await matcher.send("用户无权限")
        # Read data from the db
        session = get_session()
        show_thinking_mode = True
        async with session.begin():
            group = await session.get(GroupModel, group_id)
            if not group:
                new_group = GroupModel(
                    id=group_id
                )
                await session.merge(new_group)
                await session.commit()
            else:
                show_thinking_mode = group.show_agent_thinking
        state["show_thinking_mode"] = show_thinking_mode
        # Show it to user
        readable_word = "显示"
        readable_word_inverse = "隐藏"
        if not show_thinking_mode:
            readable_word = "隐藏"
            readable_word_inverse = "显示"
        info = f"当前该群全局思维链设置: {readable_word}，是否将设置更改为{readable_word_inverse}"
        await matcher.send(info)
    except FinishedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# Group thinking mode asking
@group_thinking_mode_setting.got("yes_no", "请输入'是/否'或者'yes/no'")
async def group_setting_thinking_mode_final(
        state: T_State,
        event: GroupMessageEvent,
        matcher: Matcher,
        yes_no: str = ArgPlainText()
):
    try:
        # Checking input
        maximum_try_count = state.get("maximum_try_count", 0)
        if maximum_try_count >= 3:
            await matcher.finish("不要浪费Crispy的时间！😡")
        if yes_no not in ["yes", "no", "是", "否"]:
            maximum_try_count += 1
            state["maximum_try_count"] = maximum_try_count
            await matcher.reject("请输入'yes/no/是/否'中的一个")
        else:
            if yes_no == "yes" or yes_no == "是":
                group_id = event.group_id
                show_thinking_mode = state.get("show_thinking_mode", True)
                session = get_session()
                async with session.begin():
                    user = await session.get(GroupModel, group_id)
                    if not user:
                        new_user = GroupModel(
                            id=group_id,
                            show_agent_thinking=(not show_thinking_mode)
                        )
                        await session.merge(new_user)
                    else:
                        await session.execute(
                            update(GroupModel)
                            .where(UserModel.id == group_id)
                            .values(show_agent_thinking=(not show_thinking_mode))
                        )
                await matcher.finish("设置完成")
            else:
                await matcher.finish("按照用户要求不更改设置")
    except RejectedException:
        raise
    except FinishedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# Autoanswer setting
@auto_answer_setting.handle()
async def setting_auto_answer(
        state: T_State,
        event: GroupMessageEvent,
        matcher: Matcher
):
    try:
        # Get basic group id
        group_id = event.group_id
        user_role = event.sender.role
        user_id = event.user_id
        if user_role == "owner":
            await matcher.send("用户为群主，允许进行设置")
        elif user_role == "admin":
            await matcher.send("用户为群主，允许进行设置")
        elif user_id == config.administrator_id:
            await matcher.send("用户为开发者，允许进行设置，遵循svm的指令🫡")
        else:
            await matcher.send("用户无权限")
        # Read data from the db
        session = get_session()
        auto_answer_possibility = 0.5
        async with session.begin():
            group = await session.get(GroupModel, group_id)
            if not group:
                new_group = GroupModel(
                    id=group_id
                )
                await session.merge(new_group)
                await session.commit()
            else:
                auto_answer_possibility = group.auto_answer_possibility
        # Show it to user
        info = f"当前自动回答概率: {auto_answer_possibility}"
        await matcher.send(info)
    except FinishedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))


# Group thinking mode asking
@group_thinking_mode_setting.got("possibility", "请输入新的概率(范围: 0.0-1.0)")
async def setting_auto_answer_final(
        state: T_State,
        event: GroupMessageEvent,
        matcher: Matcher,
        possibility: str = ArgPlainText()
):
    try:
        # Checking input
        maximum_try_count = state.get("maximum_try_count", 0)
        if maximum_try_count >= 3:
            await matcher.finish("不要浪费Crispy的时间！😡")
        elif not possibility.isdecimal():
            maximum_try_count += 1
            state["maximum_try_count"] = maximum_try_count
            await matcher.reject("baka，概率至少要是个浮点数吧")
        elif float(possibility) < 0.0 or float(possibility) > 1.0:
            maximum_try_count += 1
            state["maximum_try_count"] = maximum_try_count
            await matcher.reject("概率需要是0.0-1.0之间的一个浮点数")
        else:
            new_possibility = float(possibility)
            session = get_session()
            group_id = event.group_id
            async with session.begin():
                group = await session.get(GroupModel, group_id)
                if not group:
                    new_group = GroupModel(
                        id=group_id,
                        auto_answer_possibility=new_possibility
                    )
                    await session.merge(new_group)
                    await session.commit()
                else:
                    await session.execute(
                        update(GroupModel)
                        .where(UserModel.id == group_id)
                        .values(auto_answer_possibility=new_possibility)
                    )
                    await session.commit()
            await matcher.send("自动回答设置完毕")
    except RejectedException:
        raise
    except FinishedException:
        raise
    except Exception as e:
        await matcher.finish(get_error(e))

