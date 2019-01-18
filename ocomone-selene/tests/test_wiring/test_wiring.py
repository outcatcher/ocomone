import time

from ocomone import Resources
from selene import browser
from selene.elements import SeleneCollection, SeleneElement

from ocomone_selene import Wireable, WiredDecorator
from ocomone_selene.elements import TextInput

wired = WiredDecorator(Resources(__file__, "."))


class WiredThing(Wireable):
    def elements(self, locator) -> SeleneCollection:
        return browser.elements(locator)

    def element(self, locator) -> SeleneElement:
        return browser.element(locator)


@wired("test.yml")
class WiredYml(WiredThing):
    button: SeleneElement
    input: TextInput


@wired("test.csv")
class WiredCsv(WiredThing):
    search: SeleneElement


URL = "https://ya.ru/"


def wait_for(fnc, *args, timeout=5):
    end_time = time.time() + timeout
    while time.time() < end_time:
        if fnc(*args):
            return
    raise TimeoutError(f"Condition {fnc} not reached for arguments {args}")


def test_locators_working_yml(start_stop):
    browser.open_url(URL)
    assert WiredYml().button.text == "Найти"


def test_locators_working_csv(start_stop):
    browser.open_url(URL)
    assert WiredCsv().search.text == "Найти"


def test_fill_field(start_stop):
    browser.open_url(URL)
    page = WiredYml()
    page.input = "google"
    page.button.click()
    wait_for(lambda: "?text=google" in browser.driver().current_url)
