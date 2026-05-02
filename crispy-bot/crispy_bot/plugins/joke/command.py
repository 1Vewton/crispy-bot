from nonebot import on_command
from nonebot.rule import to_me
import random

# command
joke_cmd = on_command(
    "约吗",
    rule=to_me()
)
mom_command = on_command(
    "妈妈",
    rule=to_me()
)


# Event process
@joke_cmd.handle()
async def joke_handle():
    responses = [
        "好的宝宝🥰",
        "齁哦哦哦哦哦🥵",
        "约",
        "不约",
        "滚😠",
        "恶心🤮"
    ]
    await joke_cmd.finish(random.choice(responses))


# mom process
@mom_command.handle()
async def mom_handle():
    responses = [
        "宝宝...",
        "滚😠",
        "恶心🤮",
        "😓",
        "😰"
    ]
    await mom_command.finish(random.choice(responses))
