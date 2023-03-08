from enum import IntEnum
from typing import Optional

from google.protobuf.message import Message
from pydantic import BaseModel, root_validator


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

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {
            "msg": v.msg,
            "receiver": v.receiver,
            "aters": v.aters,
        }


class PathMsg(BaseModel):
    """
    路径类型
    """

    path: str
    """要发送的图片的路径"""
    receiver: str
    """消息接收人"""

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"path": v.path, "receiver": v.receiver}


class DbQuery(BaseModel):
    """
    sql请求
    """

    db: str
    """目标数据库"""
    sql: str
    """查询 SQL"""

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"db": v.db, "sql": v.sql}


class Verification(BaseModel):
    """
    Verification
    """

    v3: str
    v4: str

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"v3": v.v3, "v4": v.v4}


class AddMembers(BaseModel):
    """
    添加成员请求
    """

    roomid: str
    """要加的群ID"""
    wxids: str
    """要加群的人列表，逗号分隔"""

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"roomid": v.roomid, "wxids": v.wxids}


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

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {
            "receiver": v.receiver,
            "content": v.content,
            "path": v.path,
            "type": v.type,
        }


class RequestMsg(BaseModel):
    """
    请求消息
    """

    empty: Optional[EmptyMsg]
    str: Optional[str]
    txt: Optional[TextMsg]
    file: Optional[PathMsg]
    query: Optional[DbQuery]
    v: Optional[Verification]
    m: Optional[AddMembers]
    xml: Optional[XmlMsg]


class Request(BaseModel):
    """
    请求实体
    """

    func: Functions
    """请求类型"""
    msg: RequestMsg
    """请求消息"""

    def gen_dict(self) -> dict:
        """生成dict"""
        data = {
            "func": self.func,
        }
        for key, value in self.msg.dict().items():
            if value is not None:
                data[key] = value
                break
        return data


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

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
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

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"MsgTypes": v.MsgTypes}


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

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
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

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"contacts": v.contacts}


class DbNames(BaseModel):
    """
    数据库名称
    """

    names: list[str]
    """名称列表"""

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"names": v.names}


class DbTable(BaseModel):
    """数据库表"""

    name: str
    """表名"""
    sql: str
    """建表 SQL"""

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"name": v.name, "sql": v.sql}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return DbTable(
            name=v.name,
            sql=v.sql,
        )


class DbTables(BaseModel):
    """
    数据库表
    """

    tables: list[DbTable]
    """数据库表列表"""

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"tables": v.tables}


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

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"type": v.type, "column": v.column, "content": v.content}


class DbRow(BaseModel):
    """
    数据库记录
    """

    fields: list[DbField]
    """记录列表"""

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"fields": v.fields}


class DbRows(BaseModel):
    """
    数据库记录列表
    """

    rows: list[DbRow]
    """记录列表"""

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        return {"rows": v.rows}


class ResponseMsg(BaseModel):
    """返回消息"""

    status: Optional[int]
    str: Optional[str]
    wxmsg: Optional[WxMsg]
    types: Optional[MsgTypes]
    contacts: Optional[RpcContacts]
    dbs: Optional[DbNames]
    tables: Optional[DbTables]
    rows: Optional[DbRows]


class Response(BaseModel):
    """返回消息"""

    func: Functions
    """返回类型"""
    status: Optional[int]
    str: Optional[str]
    wxmsg: Optional[WxMsg]
    types: Optional[MsgTypes]
    contacts: Optional[RpcContacts]
    dbs: Optional[DbNames]
    tables: Optional[DbTables]
    rows: Optional[DbRows]

    @root_validator(pre=True)
    def from_protobuf(cls, v):
        if not isinstance(v, Message):
            raise TypeError("必须是protobuf的Message实例")
        try:
            status = v.status
        except Exception:
            status = None
        try:
            string = v.str
        except Exception:
            string = None
        try:
            wxmsg = v.wxmsg
        except Exception:
            wxmsg = None
        try:
            types = v.types
        except Exception:
            types = None
        try:
            contacts = v.contacts
        except Exception:
            contacts = None
        try:
            dbs = v.dbs
        except Exception:
            dbs = None
        try:
            tables = v.tables
        except Exception:
            tables = None
        try:
            rows = v.rows
        except Exception:
            rows = None
        return {
            "func": v.func,
            "status": status,
            "str": string,
            "wxmsg": wxmsg,
            "types": types,
            "contacts": contacts,
            "dbs": dbs,
            "tables": tables,
            "rows": rows,
        }
