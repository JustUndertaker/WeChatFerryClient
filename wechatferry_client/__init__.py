from functools import partial

from wechatferry_client.cmd import install, uninstall
from wechatferry_client.config import Config, Env
from wechatferry_client.driver import Driver
from wechatferry_client.grpc import GrpcManager
from wechatferry_client.log import default_filter, log_init, logger

_Driver: Driver = None
"""全局后端驱动器"""
_Grpc: GrpcManager = None
"""grpc管理器"""


def init():
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
    _Driver.on_startup(init_grpc)
    _Driver.on_shutdown(_Grpc.close)
    _Driver.on_shutdown(partial(uninstall, "./wcf.exe"))


def run() -> None:
    """
    启动
    """
    _Driver.run()


def init_grpc():
    """初始化grpc"""
    result = _Grpc.init()
    if not result:
        _Driver.server_app.router.shutdown()
