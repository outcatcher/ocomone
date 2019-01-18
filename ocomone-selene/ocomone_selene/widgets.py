# -*- coding=utf-8 -*-
"""Base class for creating Wireable widgets"""
from typing import Type

from selene import browser
from selene.elements import SeleneElement

from .comators import CommentParsingMeta
from .elements import ReadonlyElement
from .wiring import Wireable, get_custom_element, register_without_setter

__all__ = ["BaseWidget"]


class WidgetMeta(CommentParsingMeta):
    """Auto-registering widgets"""

    def __init__(cls: Type["BaseWidget"], *args, **kwargs):
        super().__init__(*args, **kwargs)

        if cls.__name__ != "BaseWidget":
            register_without_setter(cls)


class BaseWidget(Wireable, metaclass=WidgetMeta):
    """Base class for widgets"""

    def __init__(self, root_element: ReadonlyElement = None):
        if root_element is None:
            root_element = browser.element("html")
        self.root_element = root_element

    def get_element(self, field_name, field_type: type = SeleneElement, *type_args):
        """Get locator for given field name"""
        if hasattr(self, field_name):
            return getattr(self, field_name)
        return get_custom_element(self, field_name, field_type, *type_args)

    def is_displayed(self) -> bool:
        """Shows that root element is visible"""
        return self.root_element.is_displayed()

    def assure(self, condition, timeout=None):
        """Wait for timeout seconds for condition to become True"""
        return self.root_element.assure(condition, timeout)

    def assure_not(self, condition, timeout=None):
        """Wait for timeout seconds for condition to become False"""
        return self.root_element.assure_not(condition, timeout)

    def element(self, ccs_selector_or_by):
        """Find element if widget"""
        return self.root_element.element(ccs_selector_or_by)

    def elements(self, ccs_selector_or_by):
        """Find element if widget"""
        return self.root_element.elements(ccs_selector_or_by)
