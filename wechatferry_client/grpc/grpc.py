import asyncio

from google.protobuf.message import Message
from pynng import Pair1
from pynng.exceptions import Closed, NNGException, Timeout

from wechatferry_client.log import logger
from wechatferry_client.utils import escape_tag

from . import wcf_pb2
from .model import Functions, Request, Response


def handle_msg(message: Response) -> None:
    logger.debug(f"收到消息 - {escape_tag(message.json(skip_defaults=True))}")


class GrpcManager:
    """
    grpc管理
    """

    api_socket: Pair1
    """调用api的socket"""
    msg_socket: Pair1
    """接收消息的socket"""

    def __init__(self) -> None:
        self.api_socket = Pair1(send_timeout=2000, recv_timeout=2000)
        self.msg_socket = Pair1(send_timeout=2000, recv_timeout=2000)

    def init(self) -> bool:
        """
        初始化grpc连接
        """
        logger.info("<y>正在连接到grpc...</y>")
        self.api_socket.dial("tcp://127.0.0.1:10086", block=True)
        logger.debug("<g>grpc连接成功...</g>")
        logger.debug("<y>发送接收消息请求...</y>")
        if not self.enable_receiving_msg():
            logger.error("<r>请求通信出错...</r>")
            return False
        logger.debug("<g>请求接收消息成功...</g>")
        logger.debug("<y>正在连接消息推送grpc...</y>")
        self.msg_socket.dial("tcp://127.0.0.1:10087", block=True)
        logger.success("<g>连接grpc成功...</g>")
        asyncio.create_task(self.recv_msg())
        return True

    def close(self) -> None:
        """
        关闭grpc连接
        """
        logger.info("<y>正在关闭grpc...</y>")
        self.api_socket.close()
        self.msg_socket.close()
        logger.success("<g>grpc关闭成功...</g>")

    async def recv_msg(self) -> None:
        """
        接收数据，上报事件
        """
        while True:
            try:
                data = await self.msg_socket.arecv_msg()
                rsp: Message = wcf_pb2.Response()
                rsp.ParseFromString(data.bytes)
                msg = Response.parse_protobuf(rsp)
                handle_msg(msg)
            except Timeout:
                continue
            except Closed:
                logger.debug("<g>grpc连接已关闭...</g>")
                return
            except NNGException as e:
                logger.error(f"<r>连接出错:{e}</r>")
                return
            except Exception as e:
                logger.error(f"<r>消息出错:{e}</r>")
                continue

    async def request(self, request: Request) -> Response:
        """
        发送请求
        """
        await self.api_socket.asend(request.get_request_data())
        res = await self.api_socket.arecv_msg()
        rsp: Message = wcf_pb2.Response()
        rsp.ParseFromString(res.bytes)
        msg = Response.parse_protobuf(rsp)
        return msg

    def enable_receiving_msg(self) -> bool:
        """
        说明:
            允许接收信息
        """
        request = Request(func=Functions.FUNC_ENABLE_RECV_TXT)
        self.api_socket.send(request.get_request_data())
        rsp = self.api_socket.recv_msg(block=True)
        reponse: Message = wcf_pb2.Response()
        reponse.ParseFromString(rsp.bytes)
        msg = Response.parse_protobuf(rsp)
        return msg.status == 0
