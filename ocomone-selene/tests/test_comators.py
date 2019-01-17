# -*- coding=utf-8 -*-
from selene import browser, config
from selene.browsers import BrowserName
from selene.elements import SeleneElement, SeleneCollection

from ocomone_selene.comators import CommentParser


class TestCommentedLocator(CommentParser):
    def elements(self, locator) -> SeleneCollection:
        return browser.elements(locator)

    def element(self, locator) -> SeleneElement:
        return browser.element(locator)

    g_search_button: SeleneElement  # css:button


if __name__ == '__main__':
    config.browser_name = BrowserName.CHROME
    browser.open_url("https://ya.ru/")
    assert TestCommentedLocator().g_search_button.text == "Найти"
