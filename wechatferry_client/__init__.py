from fastapi import FastAPI

from wechatferry_client.cmd import install, uninstall
from wechatferry_client.config import Config, Env
from wechatferry_client.driver import Driver
from wechatferry_client.http import router
from wechatferry_client.log import default_filter, log_init, logger
from wechatferry_client.wechat import WeChatManager

_Driver: Driver = None
"""全局后端驱动器"""
_WeChat: WeChatManager = None
"""微信管理器"""


def init() -> None:
    """
    初始化client
    """
    global _Driver
    global _WeChat

    env = Env()
    config = Config(_common_config=env.dict())
    default_filter.level = config.log_level
    log_init(config.log_days)
    logger.info(f"Current <y><b>Env: {env.environment}</b></y>")
    logger.debug(f"Loaded <y><b>Config</b></y>: {str(config.dict())}")

    uninstall("./wcf.exe")
    logger.info("<y>正在注入微信...</y>")
    if not install(cmd_path="./wcf.exe", debug=True):
        logger.error("<r>注入微信失败...</r>")
        exit(-1)
    logger.success("<g>微信注入成功...</g>")

    _Driver = Driver(config)
    _WeChat = WeChatManager(config)
    _WeChat.init()

    app = _Driver.server_app
    app.include_router(router)
    logger.success("<g>http api已开启...</g>")
    _Driver.on_startup(_WeChat.connect_msg_socket)
    _Driver.on_shutdown(_WeChat.close)


def run() -> None:
    """
    启动
    """

    _Driver.run()


def get_wechat() -> WeChatManager:
    """
    获取wechat管理器
    """
    if _WeChat is None:
        raise ValueError("wechat管理端尚未初始化...")
    return _WeChat


def get_driver() -> Driver:
    """
    获取后端驱动器
    """
    if _Driver is None:
        raise ValueError("驱动器尚未初始化...")
    return _Driver


def get_app() -> FastAPI:
    """获取 Server App 对象。

    返回:
        Server App 对象

    异常:
        ValueError: 全局 `Driver` 对象尚未初始化 (`wechatferry_client.init` 尚未调用)
    """
    driver = get_driver()
    return driver.server_app
