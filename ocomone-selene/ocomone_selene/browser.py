# -*- coding=utf-8 -*-
"""Features for selene browser management"""
from selene import browser, config
from selene.browsers import BrowserName
from selenium import webdriver


def headless_chrome():
    """Configure system to use headless chrome"""
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager

    options = ChromeOptions()
    options.headless = True
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=options)
    browser.set_driver(driver)


def headless_firefox():
    """Configure system to use headless firefox"""
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from webdriver_manager.firefox import GeckoDriverManager

    options = FirefoxOptions()
    options.headless = True
    browser.driver()
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
    browser.set_driver(driver)


def headless_default():
    """Configure default browser to be headless"""
    browser_name = config.browser_name
    if browser_name == BrowserName.CHROME:
        headless_chrome()
    elif browser_name == BrowserName.FIREFOX:
        headless_firefox()
