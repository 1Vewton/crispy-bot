from nonebot import on_command
from .commands_info import info

# help command
help_command = on_command(
    "help"
)

@help_command.handle()
async def help_function():
    text = (
f"""以下为可以让Crispy执行的命令:{"".join([f"\n\n命令: {i["title"]}\n功能: {i["description"]}\n使用方法: {i["usage"]}" for i in info])}
"""
    )
    await help_command.finish(text)
