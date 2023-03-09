import time

from pynng.exceptions import Timeout

from wechatferry_client.config import Config
from wechatferry_client.grpc.model import Request as GrpcRequest
from wechatferry_client.log import logger
from wechatferry_client.model import HttpRequest, HttpResponse, Request, Response

from .api_manager import Action, ApiManager


class WeChatManager:
    """
    微信客户端管理
    """

    config: Config
    """
    应用设置
    """
    api_manager: ApiManager
    """
    api管理模块
    """
    self_id: str
    """自身微信id"""

    def __init__(self) -> None:
        self.config = None
        self.api_manager = ApiManager()
        self.self_id = None

    def init(self, config: Config) -> None:
        """
        初始化wechat管理端，需要在uvicorn.run之前执行
        """
        self.config = config
        self.api_manager.init()

        logger.debug("<y>开始获取wxid...</y>")
        self.self_id = self.api_manager.get_wxid()
        logger.debug("<g>微信id获取成功...</g>")

    def wait_for_login(self) -> bool:
        """
        等待微信登录完成
        """
        while True:
            try:
                result = self.api_manager.check_is_login()
                if result:
                    return True
                time.sleep(1)
            except KeyboardInterrupt:
                return False
            except Timeout:
                return False

    def connect_msg_socket(self) -> bool:
        """
        连接到接收socket
        """
        return self.api_manager.connect_msg_socket()

    def close(self) -> None:
        """
        管理微信管理模块
        """
        self.api_manager.close()

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
