import asyncio

from google.protobuf import json_format
from google.protobuf.message import Message
from pynng import Pair0

from . import wcf_pb2
from .model import Request, Response


def handle_msg() -> None:
    pass


class GrpcManager:
    """
    grpc管理
    """

    api_socket: Pair0
    """调用api的socket"""
    msg_socket: Pair0
    """接收消息的socket"""

    def __init__(self) -> None:
        self.api_socket = Pair0(send_timeout=2000, recv_timeout=2000)
        self.msg_socket = Pair0(send_timeout=2000, recv_timeout=2000)

    def init(self) -> None:
        """
        初始化grpc连接
        """
        self.api_socket.dial("127.0.0.1:10086", block=False)
        self.msg_socket.dial("127.0.0.1:10087", block=False)
        asyncio.create_task(self.recv_msg())

    def close(self) -> None:
        """
        关闭grpc连接
        """
        self.api_socket.close()
        self.msg_socket.close()

    async def recv_msg(self) -> None:
        """
        接收数据，上报事件
        """
        while True:
            data = await self.msg_socket.arecv_msg()
            rsp: Message = wcf_pb2.Response()
            rsp.ParseFromString(data.bytes)
            msg = Response.parse_obj(rsp)
            handle_msg(msg)

    async def request(self, request: Request) -> Response:
        """
        发送请求
        """
        get_request: Message = json_format.ParseDict(
            request.json(), wcf_pb2.Request(), ignore_unknown_fields=True
        )
        await self.api_socket.asend(get_request.SerializeToString())
        res = await self.api_socket.arecv_msg()
        rsp: Message = wcf_pb2.Response()
        rsp.ParseFromString(res.bytes)
        msg = Response.parse_obj(rsp)
        return msg
