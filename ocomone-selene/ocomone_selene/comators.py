# -*- coding=utf-8 -*-
"""Map field to element via comment"""
import inspect
import re
from copy import copy
from typing import Type

from ocomone_selene.wiring import Wireable, _STRATEGIES, _cached_getter, _convert_locator, _to_property, _wired_getter

FIELD_RE = re.compile("^\s+(\w+?):\s*(\w+?)\s+#\s*(.+)$")  # e.g. `field_2: SeleneElement  # id:my-id`


class CommentParsingMeta(type):
    """Metaclass for creating class with locators in comments"""

    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        lines = inspect.getsourcelines(cls)[0]
        cls._strategies = copy(_STRATEGIES)
        for line in lines:
            if "#" not in line:  # if no comment — nothing to do
                continue
            re_found = FIELD_RE.search(line)
            if not re_found:
                continue
            field_name, _, locator = re_found.groups()  # field class text is dropped
            if hasattr(cls, field_name):  # ignore already set fields
                continue
            field_class: Type[Wireable] = cls.__annotations__[field_name]
            locator = _convert_locator(*locator.split(":"))
            getter = _cached_getter(_wired_getter(field_class, locator), field_name)
            new_property = _to_property(field_name, field_class, getter)
            setattr(cls, field_name, new_property)
        return cls


# noinspection PyAbstractClass
class CommentParser(Wireable, metaclass=CommentParsingMeta):
    """Class containing fields to be parsed"""
