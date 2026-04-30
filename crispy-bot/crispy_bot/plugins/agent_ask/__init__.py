from nonebot import require
require("crispy_bot.plugins.data_manager")
require("nonebot_plugin_session")
require("nonebot_plugin_chatrecorder")
# utilities
from uuid import uuid4
import json
from datetime import datetime, timedelta
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
from nonebot.exception import FinishedException
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
from nonebot_plugin_chatrecorder import get_message_records
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
thingking_mode_setting = on_command(
    "thinkingModeSetting",
    aliases={
        "思考设置"
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
                    if is_thinking_shown:
                        await matcher.finish(get_error(Exception(chunk.content)))
                elif chunk.step == "model":
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
async def process_quick_answer(bot: Bot, event: MessageEvent, group_event: Event, matcher: Matcher):
    if event.get_user_id() == bot.self_id:
        await matcher.finish()
    try:
        # Get message
        message = event.get_plaintext()
        message_id = event.message_id
        # Find whether the user need answer
        test_prompt = process_prompt_test(message)
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
                question=json_res["question"]
            )
            session = extract_session(bot, group_event)
            records = await get_message_records(
                session=session,
                time_start=datetime.utcnow() - timedelta(hours=1),
            )
            answer_prompt += f"""

# 用户的对话背景
你需要根据用户的对话的上下文来了解为什么他们会有这种疑问，如果前面的判断模块的理解出问题了(**当然你不能提到判断模块的存在**)你就根据他们说的内容开个玩笑打个哈哈过去
当然也有可能没有上下文
{
"".join(
    [
        f"\n\n内容: {record.message}\n\n"
        for record in records
    ]
)
}
"""
            logger.info(answer_prompt)
            answer_result = await invoke_agent(
                llm_provider=config.llm_provider,
                llm_api_key=config.llm_api_key,
                llm_base_url=config.llm_base_url,
                llm_model_name=config.llm_model_name,
                prompt=answer_prompt
            )
            result_message = MessageSegment.reply(message_id) + MessageSegment.text(answer_result)
            await matcher.finish(result_message)
        else:
            await matcher.finish()
    except FinishedException:
        raise
    except Exception as e:
        logger.error(e)

