# coding=utf-8
"""SSH 的简易封装"""
from io import TextIOBase
from typing import Any, Optional, cast

from fabric import Connection
from invoke.runners import Promise

from .config import Config
from .config import cmd as run_conf
from .config import ssh as ssh_conf


class SshSession:
    """fabric.Connection 的简单包装，旨在简化 run 函数的参数。"""

    def __init__(self, run_conf_override: Optional[Config] = None, **kwargs: dict[str, Any]):
        """
        :param run_conf_override: 覆盖 config 模块中的 cmd 配置。不应该使用。
        :param kwargs: 应传入 Connection 的参数列表。
        """
        self.run_conf = run_conf_override if run_conf_override else run_conf
        self._connection = Connection(**kwargs)

    def run(self, cmd: str, callback: TextIOBase) -> Promise:
        """
        通过远程终端运行指定的命令，并将结果写入 callback。
        :param cmd: 命令文本
        :param callback: 回调对象，应为一个支持写入的类文件对象，用于写入 stdout 和 stderr 内容
        :return: 一个 invoke.runner.Promise 对象，可对其执行 join
        """
        return cast(Promise,
                    self._connection.run(cmd, warn=True, timeout=self.run_conf.timeout,
                                         in_stream=None, out_stream=callback, err_stream=callback))


def init() -> SshSession:
    """
    根据 config 模块的配置，初始化和构造命令会话对象
    :return: 根据配置文件参数构造的 SshSession 实例
    """
    conn_inf = {
        "host": ssh_conf.host,
        "port": ssh_conf.port,
        "user": ssh_conf.user,
        "connect_timeout": ssh_conf.timeout,
        "connect_kwargs": {},
    }
    conn_credentials = {}
    if ssh_conf.auth.method == "password":
        conn_credentials["password"] = ssh_conf.auth.password
    elif ssh_conf.auth.method == "pkey":
        conn_credentials["key_filename"] = ssh_conf.auth.pkey.path
        if ssh_conf.auth.pkey.passphrase:
            conn_credentials["passphrase"] = ssh_conf.auth.pkey.passphrase
    conn_inf["connect_kwargs"] = conn_credentials

    return SshSession(**conn_inf)
