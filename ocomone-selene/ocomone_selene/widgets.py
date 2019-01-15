# -*- coding=utf-8 -*-
"""Base class for creating Wireable widgets"""
from selene import browser
from selene.elements import SeleneElement

from .elements import ReadonlyElement, register_without_setter
from .wiring import Wireable, get_custom_element

__all__ = ["BaseWidget"]


class WidgetMeta(type):
    """Auto-registering widgets"""

    def __init__(cls, *args, **kwargs):
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

    @property
    def is_displayed(self) -> bool:
        """Shows that root element is visible"""
        return self.root_element.is_displayed()

    def element(self, ccs_selector_or_by):
        """Find element if widget"""
        return self.root_element.element(ccs_selector_or_by)

    def elements(self, ccs_selector_or_by):
        """Find element if widget"""
        return self.root_element.elements(ccs_selector_or_by)
