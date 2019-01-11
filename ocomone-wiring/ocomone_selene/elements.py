# -*- coding=utf-8 -*-
"""Wrapper for most common used web elements"""

from abc import ABC
from enum import Enum
from typing import Union

from selene.elements import SeleneCollection, SeleneElement
from selenium.webdriver.support.select import Select as _Select

from .wiring import Wireable, register_setter, register_without_setter


# pylint: disable=abstract-method

class SeleneElementWrapper(SeleneElement, ABC):
    """Superclass for wrappers around :class:`SeleneElement`"""

    def __init__(self, _element: SeleneElement):
        super().__init__(_element._locator, _element._webdriver)  # pylint: disable=protected-access


class ReadonlyElement(SeleneElementWrapper):
    """Class for non-editable elements"""


register_without_setter(ReadonlyElement)


class Message(ReadonlyElement):
    """Message box wrapper for both error and success message"""


class Button(ReadonlyElement):
    """Button wrapper"""


class TextInput(SeleneElementWrapper):
    """Mutable input wrapper"""


register_setter(TextInput, TextInput.set)


class Checkbox(SeleneElementWrapper):
    """Checkbox input"""

    def set(self, value: bool):  # pylint: disable=arguments-differ
        """Set checkbox value"""
        if self.is_selected() != value:
            self.click()


register_setter(Checkbox, Checkbox.set)


class Select(_Select, Wireable):
    """Wrapper around """
    _el: SeleneElement

    def elements(self, locator) -> SeleneCollection:
        return self._el.element(locator)

    def element(self, locator) -> SeleneElement:
        return self._el.element(locator)

    def __init__(self, element: SeleneElement):
        _Select.__init__(self, element)

    def select_by_value(self, value: Union[Enum, str]):
        """Select by value equals given value or value.name if value is :class:`Enum`"""
        if isinstance(value, Enum):
            value = value.name
        super().select_by_value(value)


register_setter(Select, Select.select_by_value)
