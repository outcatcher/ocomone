"""Custom locator strategies"""

from selene import browser
from selene.bys import by_partial_text
from selene.elements import SeleneElement
from selenium.webdriver.common.by import By

__all__ = ["by_id", "by_label"]


def by_id(element_id: str):
    """Find element by exact ID"""
    return By.ID, element_id


def by_label(label_text: str, parent: SeleneElement = None):
    """Search element by corresponding label"""
    element = browser.element if parent is None else parent.element
    label = element(by_partial_text(label_text))
    target_id = label.get_attribute("for")
    if target_id is None:
        raise TypeError(f"Label `{parent}` -> `{label}` has no attribute @for")
    return by_id(target_id)
