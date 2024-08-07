# coding=utf-8
"""Astr-cmd内部使用的元数据信息。"""
import yaml

PLUGIN_ID: str

with open("metadata.yaml", "r", encoding='utf-8') as f:
    PLUGIN_ID = yaml.safe_load(f)["name"]
