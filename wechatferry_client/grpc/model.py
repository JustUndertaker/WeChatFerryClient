from enum import IntEnum
from typing import Optional

from google.protobuf import json_format
from google.protobuf.message import Message
from pydantic import BaseModel

from . import wcf_pb2


class Functions(IntEnum):
    """functions"""

    FUNC_RESERVED = 0x00
    """保留"""
    FUNC_IS_LOGIN = 0x01
    """请求是否登录"""
    FUNC_GET_SELF_WXID = 0x10
    """请求获取自身wxid"""
    FUNC_GET_MSG_TYPES = 0x11
    """请求获取所有msg类型"""
    FUNC_GET_CONTACTS = 0x12
    """请求获取联系人"""
    FUNC_GET_DB_NAMES = 0x13
    """请求获取数据库名"""
    FUNC_GET_DB_TABLES = 0x14
    """请求获取数据库表"""
    FUNC_SEND_TXT = 0x20
    """请求发送文本"""
    FUNC_SEND_IMG = 0x21
    """请求发送图片"""
    FUNC_SEND_FILE = 0x22
    """请求发送文件"""
    FUNC_SEND_XML = 0x23
    """请求发送xml"""
    FUNC_ENABLE_RECV_TXT = 0x30
    """接收文本"""
    FUNC_DISABLE_RECV_TXT = 0x40
    """不允许接收文本"""
    FUNC_EXEC_DB_QUERY = 0x50
    """退出数据库查询"""
    FUNC_ACCEPT_FRIEND = 0x51
    """接收好友邀请"""
    FUNC_ADD_ROOM_MEMBERS = 0x52
    """添加群成员"""


class EmptyMsg(BaseModel):
    """
    空信息
    """

    ...


class TextMsg(BaseModel):
    """
    text类型
    """

    msg: str
    """要发送的消息内容"""
    receiver: str
    """消息接收人，当为群时可@"""
    aters: str
    """要@的人列表，逗号分隔"""


class PathMsg(BaseModel):
    """
    路径类型
    """

    path: str
    """要发送的图片的路径"""
    receiver: str
    """消息接收人"""


class DbQuery(BaseModel):
    """
    sql请求
    """

    db: str
    """目标数据库"""
    sql: str
    """查询 SQL"""


class Verification(BaseModel):
    """
    Verification
    """

    v3: str
    v4: str


class AddMembers(BaseModel):
    """
    添加成员请求
    """

    roomid: str
    """要加的群ID"""
    wxids: str
    """要加群的人列表，逗号分隔"""


class XmlMsg(BaseModel):
    """
    xml消息
    """

    receiver: str
    """消息接收人"""
    content: str
    """xml 内容"""
    path: str
    """图片路径"""
    type: int
    """消息类型"""


class Request(BaseModel):
    """
    请求实体
    """

    func: Functions
    """请求类型"""
    empty: Optional[EmptyMsg] = None
    str: Optional[str] = None
    txt: Optional[TextMsg] = None
    file: Optional[PathMsg] = None
    query: Optional[DbQuery] = None
    v: Optional[Verification] = None
    m: Optional[AddMembers] = None
    xml: Optional[XmlMsg] = None

    def get_request_data(self) -> bytes:
        """
        获取Request请求数据
        """
        request: Message = json_format.ParseDict(
            self.dict(exclude_defaults=True),
            wcf_pb2.Request(),
            ignore_unknown_fields=True,
        )
        return request.SerializeToString()


class WxMsg(BaseModel):
    """
    微信消息
    """

    is_self: bool
    """是否自己发送的"""
    is_group: bool
    """是否群消息"""
    type: int
    """消息类型"""
    id: str
    """消息 id"""
    xml: str
    """消息 xml"""
    sender: str
    """消息发送者"""
    roomid: str
    """群 id（如果是群消息的话）"""
    content: str
    """消息内容"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        """
        从protobuf返回字典
        """
        return {
            "is_self": v.is_self,
            "is_group": v.is_group,
            "type": v.type,
            "id": v.id,
            "xml": v.xml,
            "sender": v.sender,
            "roomid": v.roomid,
            "content": v.content,
        }


class MsgTypes(BaseModel):
    """
    消息类型返回
    """

    MsgTypes: dict[int, str]
    """所有消息分类"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        """
        从protobuf返回字典
        """
        return {"MsgTypes": dict(v.MsgTypes)}


class RpcContact(BaseModel):
    """
    联系人
    """

    wxid: str
    """微信 id"""
    code: str
    """微信号"""
    name: str
    """微信昵称"""
    country: str
    """国家"""
    province: str
    """省/州"""
    city: str
    """城市"""
    gender: int
    """性别"""

    @classmethod
    def from_protobuf(cls, v: Message):
        return {
            "wxid": v.wxid,
            "code": v.code,
            "name": v.name,
            "country": v.country,
            "province": v.province,
            "city": v.city,
            "gender": v.gender,
        }


class RpcContacts(BaseModel):
    """
    联系人
    """

    contacts: list[RpcContact]
    """联系人列表"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        contacts = [RpcContact.from_protobuf(one) for one in v.contacts]
        return {"contacts": list(contacts)}


class DbNames(BaseModel):
    """
    数据库名称
    """

    names: list[str]
    """名称列表"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        return {"names": list(v.names)}


class DbTable(BaseModel):
    """数据库表"""

    name: str
    """表名"""
    sql: str
    """建表 SQL"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        return {"name": v.name, "sql": v.sql}


class DbTables(BaseModel):
    """
    数据库表
    """

    tables: list[DbTable]
    """数据库表列表"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        tables = [DbTables.from_protobuf(one) for one in v.tables]
        return {"tables": tables}


class DbField(BaseModel):
    """
    数据库字段
    """

    type: int
    """字段类型"""
    column: str
    """字段名称"""
    content: bytes
    """字段内容"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        return {"type": v.type, "column": v.column, "content": v.content}


class DbRow(BaseModel):
    """
    数据库记录
    """

    fields: list[DbField]
    """记录列表"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        fields = [DbField.from_protobuf(one) for one in v.fields]
        return {"fields": fields}


class DbRows(BaseModel):
    """
    数据库记录列表
    """

    rows: list[DbRow]
    """记录列表"""

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        rows = [DbRow.from_protobuf(one) for one in v.rows]
        return {"rows": rows}


class Response(BaseModel):
    """返回消息"""

    func: Functions
    """返回类型"""
    status: Optional[int] = None
    str: Optional[str] = None
    wxmsg: Optional[WxMsg] = None
    types: Optional[MsgTypes] = None
    contacts: Optional[RpcContacts] = None
    dbs: Optional[DbNames] = None
    tables: Optional[DbTables] = None
    rows: Optional[DbRows] = None

    @classmethod
    def check_msg_type(cls, v: Message) -> dict:
        """
        检测是哪种消息
        """
        if v.HasField("status"):
            return {"status": v.status}
        if v.HasField("str"):
            return {"str": v.str}
        if v.HasField("wxmsg"):
            return {"wxmsg": WxMsg.from_protobuf(v.wxmsg)}
        if v.HasField("types"):
            return {"types": MsgTypes.from_protobuf(v.types)}
        if v.HasField("contacts"):
            return {"contacts": RpcContacts.from_protobuf(v.contacts)}
        if v.HasField("dbs"):
            return {"dbs": DbNames.from_protobuf(v.dbs)}
        if v.HasField("tables"):
            return {"tables": DbTables.from_protobuf(v.tables)}
        if v.HasField("rows"):
            return {"rows": DbRows.from_protobuf(v.rows)}

    @classmethod
    def from_protobuf(cls, v: Message) -> dict:
        data = {"func": v.func}
        data.update(cls.check_msg_type(v))
        return data

    @classmethod
    def parse_protobuf(cls, v: Message) -> "Response":
        """
        从protobuf中获取实例
        """
        return cls.parse_obj(cls.from_protobuf(v))
