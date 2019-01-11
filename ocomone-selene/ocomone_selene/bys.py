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
    target_id = element(by_partial_text(label_text)).get_attribute("for")
    return by_id(target_id)
