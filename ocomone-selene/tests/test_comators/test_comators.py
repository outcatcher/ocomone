# -*- coding=utf-8 -*-
from selene import browser
from selene.elements import SeleneCollection, SeleneElement

from ocomone_selene.comators import AbstractCommentParser


class TestCommentedLocator(AbstractCommentParser):
    def elements(self, locator) -> SeleneCollection:
        return browser.elements(locator)

    def element(self, locator) -> SeleneElement:
        return browser.element(locator)

    search: SeleneElement  # css:button


def test_locators_working(start_stop):
    browser.open_url("https://ya.ru/")
    assert TestCommentedLocator().search.text == "Найти"
