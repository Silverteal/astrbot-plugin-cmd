# coding=utf-8
"""Astr-cmd内部使用的元数据信息。"""
import yaml

PLUGIN_ID: str

PLUGIN_PATH: str = __file__.removesuffix(__name__ + '.py')  # TODO：换个更优雅的实现方式

with open(PLUGIN_PATH + "metadata.yaml", "r", encoding='utf-8') as f:
    PLUGIN_ID = yaml.safe_load(f)["name"]
