import asyncio
from functools import wraps
from langchain_core.tools import BaseTool
from nonebot import logger


# Timeout
def add_timeout_to_tool(tool: BaseTool, timeout_seconds: int = 30) -> BaseTool:
    # _arun
    original_arun = tool._arun

    @wraps(original_arun)
    async def arun_with_timeout(*args, **kwargs):
        try:
            return await asyncio.wait_for(
                original_arun(*args, **kwargs),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.error("Time out Error")
            return (
                f"⏰ 工具 '{tool.name}' 调用超时（超过 {timeout_seconds} 秒），"
                "建议稍后重试或使用已有知识回答。"
            )
        except Exception as e:
            logger.error(e)
            return f"❌ 工具 '{tool.name}' 调用失败: {str(e)[:200]}"
    tool._arun = arun_with_timeout
    return tool
