# -*- coding=utf-8 -*-
"""Features for selene browser management"""
from selene import browser, config
from selene.browsers import BrowserName
from selenium import webdriver


def _headless_browser(browser_name: BrowserName):
    if browser_name == BrowserName.CHROME:
        from webdriver_manager.chrome import ChromeDriverManager as Manager
        from selenium.webdriver.chrome.options import Options
        drv_cls = webdriver.Chrome
    elif browser_name == BrowserName.FIREFOX:
        from webdriver_manager.firefox import GeckoDriverManager as Manager
        from selenium.webdriver.firefox.options import Options
        drv_cls = webdriver.Firefox
    else:
        raise AttributeError(f"Invalid browser: {browser_name}")
    options = Options()
    driver = drv_cls(executable_path=Manager().install(), options=options)
    browser.set_driver(driver)


def headless_chrome():
    """Configure system to use headless chrome"""
    _headless_browser(BrowserName.CHROME)


def headless_firefox():
    """Configure system to use headless firefox"""
    _headless_browser(BrowserName.FIREFOX)


def headless_default():
    """Configure default browser to be headless"""
    browser_name = config.browser_name
    _headless_browser(browser_name)
