from functools import partial

from fastapi import FastAPI

from wechatferry_client.cmd import install, uninstall
from wechatferry_client.config import Config, Env
from wechatferry_client.driver import Driver
from wechatferry_client.grpc import GrpcManager
from wechatferry_client.log import default_filter, log_init, logger

_Driver: Driver = None
"""全局后端驱动器"""
_Grpc: GrpcManager = None
"""grpc管理器"""


def init() -> None:
    """
    初始化client
    """
    global _Driver
    global _Grpc

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
    _Grpc = GrpcManager()
    init_grpc()
    _Driver.on_startup(_Grpc.connect_msg_socket)
    _Driver.on_shutdown(_Grpc.close)
    _Driver.on_shutdown(partial(uninstall, "./wcf.exe"))


def run() -> None:
    """
    启动
    """

    _Driver.run()


def init_grpc() -> None:
    """初始化grpc"""
    _Grpc.init()
    if not _Grpc.check_is_login():
        logger.info("<r>微信未登录，请登陆后操作</r>")
        result = _Grpc.wait_for_login()
        if not result:
            logger.info("<g>进程退出...</g>")
            _Grpc.close()
            uninstall("./wcf.exe")
            exit(0)

    logger.info("<g>微信已登录，出发...</g>")


def get_grpc() -> GrpcManager:
    """
    获取grpc管理器
    """
    if _Grpc is None:
        raise ValueError("grpc尚未初始化...")
    return _Grpc


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
