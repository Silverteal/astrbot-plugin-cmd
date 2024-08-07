# coding=utf-8
"""简易的配置文件实现。后续可能增加专门的配置文件。就目前而言，必须手改 Python 脚本"""
from types import SimpleNamespace

type Config = SimpleNamespace

# 配置文件版本
version = 1

# 初始化配置项
ssh = SimpleNamespace()
ssh.auth = SimpleNamespace()
ssh.auth.pkey = SimpleNamespace()
cmd = SimpleNamespace()

# 机器人命令前缀
keyword = "cmd"

# ssh 连接设置
ssh.host = '127.0.0.1'
ssh.port = 22
ssh.timeout = 30  # 连接超时秒数

# ssh 身份认证设置
ssh.user = 'root'
ssh.auth.method = 'password'  # 选填 'password' 或 'pkey'

# 如果认证方式是 'password' 则填写密码
ssh.auth.password = '<PASSWORD>'

# 如果认证方式是 'pkey' 则填写私钥路径
ssh.auth.pkey.path = 'C:/fakeroot/pkey'
ssh.auth.pkey.passphrase = None  # 如私钥有密码短语则在此填写，否则，请保持为 None。后续可能允许手动填写。现阶段您也可以通过 input 手写。

# 命令执行设置
cmd.timeout = 30  # 命令超时秒数
cmd.max_concurrent = None  # 同时最大执行命令的数量。填写 None 将由 concurrent.future.ThreadPoolExecutor 自行管理
