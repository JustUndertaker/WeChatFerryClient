from wechatferry_client.cmd import uninstall
from wechatferry_client.grpc import GrpcManager
from wechatferry_client.log import logger


class WeChatManager:
    """
    微信客户端管理
    """

    grpc: GrpcManager
    """
    grpc通信管理器
    """
    self_id: str
    """自身微信id"""

    def __init__(self) -> None:
        self.grpc = GrpcManager()
        self.self_id = None

    def init(self) -> None:
        """
        初始化wechat管理端，需要在uvicorn.run之前执行
        """
        self.grpc.init()
        if not self.grpc.check_is_login():
            logger.info("<r>微信未登录，请登陆后操作</r>")
            result = self.grpc.wait_for_login()
            if not result:
                logger.info("<g>进程退出...</g>")
                self.grpc.close()
                uninstall("./wcf.exe")
                exit(0)
        logger.info("<g>微信已登录，出发...</g>")
        logger.debug("<y>开始获取wxid...</y>")
        self.self_id = self.grpc.get_wxid()
        logger.debug("<g>微信id获取成功...</g>")

    def connect_msg_socket(self) -> bool:
        """
        连接到接收socket
        """
        return self.grpc.connect_msg_socket()

    def close(self) -> None:
        """
        管理微信管理模块
        """
        self.grpc.close()
        uninstall("./wcf.exe")
