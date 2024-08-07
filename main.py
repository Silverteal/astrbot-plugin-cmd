# coding=utf-8
"""插件主模块"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from typing import cast

import _ssh as ssh
import config
from _meta import PLUGIN_ID
from model.platform.qq_official import QQOfficial
from type.astrbot_message import MessageType

flag_not_support = False
try:
    from util.plugin_dev.api.v1.bot import Context, AstrMessageEvent, CommandResult
    from util.plugin_dev.api.v1.config import *
except ImportError:
    flag_not_support = True
    print("导入接口失败。请升级到 AstrBot 最新版本。")

'''
注意以格式 XXXPlugin 或 Main 来修改插件名。
提示：把此模板仓库 fork 之后 clone 到机器人文件夹下的 addons/plugins/ 目录下，然后用 Pycharm/VSC 等工具打开可获更棒的编程体验（自动补全等）
'''


class Main:
    """
    AstrBot 会传递 context 给插件。
    
    - context.register_commands: 注册指令
    - context.register_task: 注册任务
    - context.message_handler: 消息处理器(平台类插件用)
    """

    def __init__(self, context: Context) -> None:
        self.context = context
        context.register_commands(PLUGIN_ID, config.keyword, "运行终端命令。", 1, self.runcmd)
        self.ssh = ssh.init()
        self.thread_pool = ThreadPoolExecutor(max_workers=config.cmd.max_concurrent)

    def __del__(self) -> None:
        """插件销毁时，同时销毁线程池"""
        self.thread_pool.shutdown(cancel_futures=True)

    """
    指令处理函数。
    
    - 需要接收两个参数：message: AstrMessageEvent, context: Context
    - 返回 CommandResult 对象
    """

    def runcmd(self, message: AstrMessageEvent, context: Context) -> CommandResult:
        """在远程终端执行命令并注册输出接收器"""
        running_cmd = message.message_str.removeprefix(config.keyword + ' ')  # 消息字符串。可能需要去除前导字符？
        SshCommandRunner(ssh_session=self.ssh, message=message, thread_pool=self.thread_pool).run()

        return CommandResult().message(f"运行终端命令：{running_cmd}")


class SshCommandRunner(StringIO):
    """执行终端命令，接收远程终端输出，并将输出转发到对应会话。"""

    def __init__(self, *, ssh_session: ssh.SshSession, thread_pool: ThreadPoolExecutor,
                 message: AstrMessageEvent) -> None:
        """初始化将要执行的命令，不会马上执行命令
        :param ssh_session: 要使用的 ssh 会话，应是 _ssh.SshSession 实例
        :param thread_pool: 等待命令执行完成所使用线程的线程池
        :param message: 命令消息体。将从中获取回复所需信息
        """
        super().__init__()
        self.msg_driver = message.platform
        self.ssh = ssh_session
        self.session_id = str(message.session_id)  # 群ID是session id。有的框架用 int，有的框架用 str，具体看类型提示
        self.session_type = message.message_obj.type  # 信息是群聊信息，频道信息还是单聊
        self.command = message.message_str.removeprefix(config.keyword + ' ')
        self.thread_pool = thread_pool
        self.context = message.context
        self.logger = message.context.logger

    def run(self) -> None:
        """启动一个新的线程发送填写的命令。在整个 SshCommandRunner 的生命周期中只应该调用一次"""
        self.logger.info("执行命令开始：" + self.command)
        self.thread_pool.submit(self._run)

    def write(self, s: str, /) -> int:
        """
        SshCommandRunner 接收来自远程终端的 stdout 和 stderr 写入。写入的内容将被自动处理并发送到发起会话，并不会真正写入内存。
        :param s: 远程终端写入的内容
        :return: 类文件基类要求返回的写入长度
        """
        self.send_text(s)
        return len(str)

    def _run(self) -> None:
        """在新的线程中运行命令。"""
        self.ssh.run(self.command, self)
        self.logger.info("执行命令结束：" + self.command)

    def send_text(self, content: str) -> None:
        """
        向当前对象所对应的会话发送文本消息。只支持官 bot - ``qqchan``/``QQOfficial``
        :param content: 要发送的消息内容
        """
        # - 如果目标是 QQ 群，请添加 key `group_openid`。
        # - 如果目标是 频道消息，请添加 key `channel_id`。
        # - 如果目标是 频道私聊，请添加 key `guild_id`。
        # - 如果目标是 QQ 用户，请添加 key `openid`。
        target_types = {
            MessageType.GROUP_MESSAGE: "group_openid",
            MessageType.FRIEND_MESSAGE: "openid",
            MessageType.GUILD_MESSAGE: "channel_id",
        }
        sender: QQOfficial = cast(QQOfficial, self.msg_driver.platform_instance)
        coroutine = sender.send_msg({target_types[self.session_type]: str(self.session_id)},
                                    CommandResult().message(content))
        asyncio.run(coroutine)
