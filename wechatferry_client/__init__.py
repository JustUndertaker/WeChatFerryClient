import time

from .cmd import install, uninstall


def init():
    """
    初始化client
    """
    print("正在注入微信...")
    if not install(cmd_path="./wcf.exe", debug=False):
        print("注入微信失败...")
        exit(-1)
    print("注入成功...")

    time.sleep(5)
    print("正在关闭注入...")
    if not uninstall(cmd_path="./wcf.exe"):
        print("关闭注入失败...")
        exit(-1)
    print("关闭注入成功...")
