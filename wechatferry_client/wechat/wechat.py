from enum import Enum

from wechatferry_client.cmd import uninstall
from wechatferry_client.config import Config
from wechatferry_client.grpc import GrpcManager
from wechatferry_client.grpc.model import Functions
from wechatferry_client.grpc.model import Request as GrpcRequest
from wechatferry_client.log import logger
from wechatferry_client.model import HttpRequest, HttpResponse, Request, Response


class Action(str, Enum):
    """
    api调用枚举，对应proto的Functions
    """

    FUNC_GET_CONTACTS = "get_contacts"
    """获取联系人"""
    FUNC_GET_DB_NAMES = "get_db_names"
    """获取数据库名称"""
    FUNC_GET_DB_TABLES = "get_db_tables"
    """获取数据库表"""
    FUNC_SEND_TXT = "send_text"
    """发送文本消息"""
    FUNC_SEND_IMG = "send_image"
    """发送图片消息"""
    FUNC_SEND_FILE = "send_file"
    """发送文件"""
    FUNC_SEND_XML = "send_xml"
    """发送xml"""
    FUNC_ACCEPT_FRIEND = "accept_friend"
    """接受好友请求"""
    FUNC_ADD_ROOM_MEMBERS = "add_room_members"
    """拉好友进群"""

    def action_to_function(self) -> Functions:
        """
        action转换为function
        """
        for func in Functions:
            if func.name == self.name:
                return func


class WeChatManager:
    """
    微信客户端管理
    """

    config: Config
    """应用设置"""
    grpc: GrpcManager
    """
    grpc通信管理器
    """
    self_id: str
    """自身微信id"""

    def __init__(self) -> None:
        self.config = None
        self.grpc = GrpcManager()
        self.self_id = None

    def init(self, config: Config) -> None:
        """
        初始化wechat管理端，需要在uvicorn.run之前执行
        """
        self.config = config
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

    async def _handle_api(self, request: Request) -> Response:
        """
        处理api调用请求
        """
        # 确认action
        try:
            action = Action(request.action)
        except ValueError:
            logger.error("调用api出错：<r>功能未实现</r>")
            return Response(status=404, msg=f"{request.action} :该功能未实现", data={})
        # 调用action
        try:
            request.params["func"] = action.action_to_function()
            grpc_request = GrpcRequest.parse_obj(request.params)
        except Exception as e:
            logger.error(f"调用api出错：<r>{e}</r>")
            return Response(status=500, msg="请求参数错误", data={})
        try:
            result = await self.grpc.request(grpc_request)
        except Exception as e:
            logger.error(f"调用api出错：<r>{e}</r>")
            return Response(status=500, msg="响应错误", data={})
        data = result.dict(exclude_defaults=True)
        del data["func"]
        return Response(status=200, msg="请求成功", data=data)

    async def handle_http_api(self, request: HttpRequest) -> HttpResponse:
        """
        说明:
            处理http_api请求

        参数:
            * `request`：http请求

        返回:
            * `HttpResponse`：http响应
        """
        request = Request(action=request.action, params=request.params)
        response = await self._handle_api(request)
        return HttpResponse(
            status=response.status, msg=response.msg, data=response.data
        )
