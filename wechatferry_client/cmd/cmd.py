"""
子进程运行wcf.exe
"""
import subprocess


def install(cmd_path: str, debug: bool) -> bool:
    """
    说明:
        安装dll注入微信进程

    参数:
        * `cmd_path`: wcf.exe路径
        * `debug`: 是否开启wcf的debug日志

    返回:
        * `bool`: 是否注入成功
    """
    cmd = [cmd_path, "start"]
    if debug:
        cmd.append("debug")
    child = subprocess.run(cmd)
    return child.returncode == 0


def uninstall(cmd_path: str) -> bool:
    """
    说明:
        卸载安装的dll注入

    参数:
        * `cmd_path`: wcf.exe路径

    返回:
        * `bool`: 是否卸载成功
    """
    cmd = [cmd_path, "stop"]
    child = subprocess.run(cmd)
    return child.returncode == 0
