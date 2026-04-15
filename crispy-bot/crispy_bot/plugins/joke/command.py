from nonebot import on_command
import random

# command
joke_cmd = on_command(
    "约吗"
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
