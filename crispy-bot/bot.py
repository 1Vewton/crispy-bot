import nonebot
from pathlib import Path
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

from nonebot.adapters.onebot.v12 import Adapter as ONEBOT_V12Adapter

from nonebot.adapters.console import Adapter as CONSOLEAdapter



nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

driver.register_adapter(ONEBOT_V12Adapter)

driver.register_adapter(CONSOLEAdapter)

nonebot.load_builtin_plugins('echo')


nonebot.load_from_toml("pyproject.toml")

# load plugin
nonebot.load_plugins("./crispy_bot/plugins")

if __name__ == "__main__":
    nonebot.run()