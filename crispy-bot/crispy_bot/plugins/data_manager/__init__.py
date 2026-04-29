from nonebot import require
require("nonebot_plugin_localstore")
# Nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot_plugin_orm import Model
# Sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column
# Project dependencies
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="data_manager",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


# User model
class UserModel(Model):
    __tablename__ = "Users"
    id: Mapped[str] = mapped_column(primary_key=True)
    show_agent_thinking: Mapped[bool] = mapped_column(default=True)

# User model
class GroupModel(Model):
    __tablename__ = "Groups"
    id: Mapped[str] = mapped_column(primary_key=True)
    show_agent_thinking: Mapped[bool] = mapped_column(default=True)
