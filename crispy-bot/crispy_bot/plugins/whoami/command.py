from nonebot import on_command
from .introductions import get_introduction_normal

# Introduction command
introduction_cmd = on_command(
    "你是谁"
)

# Process event
@introduction_cmd.handle()
async def introduction_function():
    text = get_introduction_normal()
    await introduction_cmd.finish(text)
