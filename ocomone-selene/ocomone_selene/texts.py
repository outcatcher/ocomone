# -*- coding=utf-8 -*-
"""Library for mapping class with texts to .ini file"""

from configparser import ConfigParser


class TextMappingMeta(type):
    """Metaclass for creating set of texts loaded from ini files"""

    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        if not hasattr(cls, "file_path") or not getattr(cls, "file_path"):  # if file_path is missing or empty
            return cls  # can't map
        file_path: str = getattr(cls, "file_path")
        configs = ConfigParser(interpolation=None)
        configs.read(file_path, "utf8")
        if not configs:
            raise AttributeError(f"File {file_path} is not valid INI file")
        messages = configs["DEFAULT"]
        for message in messages:
            setattr(cls, message.upper(), messages[message])
        return cls


class AbstractTextMapping(metaclass=TextMappingMeta):
    """Base class text mappings"""

    file_path: str  # required field for mapping
