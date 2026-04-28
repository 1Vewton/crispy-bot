# utilities
from uuid import uuid4
# nonebot dependencies
from nonebot import get_plugin_config, on_command, logger
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.exception import FinishedException
from nonebot.adapters import Event
# project dependencies
from .config import Config
from utils import get_error
from .agent import agent

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
    "ask"
)


# Process
@ask.handle()
async def process_ask(event:Event, matcher: Matcher, args: Message = CommandArg()):
    logger.info("Start process user's ask")
    try:
        question = args.extract_plain_text()
        if question:
            # Generate context id
            context_id = str(uuid4())
            user_id = event.get_user_id()
            await matcher.send(f"正在处理{user_id}的请求，context编号{context_id}")
            await agent.initialize(
                mcp_url=config.exa_url,
                api_key=config.exa_api_key
            )
            async for chunk in agent.streaming(question, context_id):
                if chunk.step == "finish":
                    await matcher.finish(chunk.content)
                elif chunk.step == "error":
                    await matcher.finish(get_error(Exception(chunk.content)))
                else:
                    await matcher.send(f"🤔🤔🤔Crispy正在思考中...🤔🤔🤔:\n{chunk.content}")
        else:
            await matcher.finish("请输入问题")
    except FinishedException:
        raise
    except Exception as e:
        # Error display
        await matcher.finish(get_error(e))

