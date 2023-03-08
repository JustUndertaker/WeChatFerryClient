from functools import partial

from wechatferry_client.cmd import install, uninstall
from wechatferry_client.config import Config, Env
from wechatferry_client.driver import Driver
from wechatferry_client.log import default_filter, log_init, logger

_Driver: Driver = None
"""全局驱动器"""


def init():
    """
    初始化client
    """
    global _Driver

    env = Env()
    config = Config(_common_config=env.dict())
    default_filter.level = config.log_level
    log_init(config.log_days)
    logger.info(f"Current <y><b>Env: {env.environment}</b></y>")
    logger.debug(f"Loaded <y><b>Config</b></y>: {str(config.dict())}")

    logger.info("<y>正在注入微信...</y>")
    if not install(cmd_path="./wcf.exe", debug=False):
        logger.info("<r>注入微信失败...</r>")
        exit(-1)
    logger.info("<g>微信注入成功...</g>")

    _Driver = Driver(config)
    _Driver.on_shutdown(partial(uninstall, "./wcf.exe"))
    # 启动进程
    _Driver.run()
