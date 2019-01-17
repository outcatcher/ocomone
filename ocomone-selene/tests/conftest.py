# -*- coding=utf-8 -*-
import pytest
from selene import browser, config
from selene.browsers import BrowserName

from ocomone_selene.browser import headless_default


@pytest.fixture
def start_stop():
    config.browser_name = BrowserName.CHROME
    headless_default()
    yield
    browser.close()
