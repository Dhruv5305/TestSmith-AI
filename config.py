"""
Auto-generated Selenium test by TestSmith AI
Fixed config import
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Fixed import (uses package path instead of plain 'config')
from testsmith_ai.config import HEADLESS, BROWSER, IMPLICIT_WAIT


@pytest.fixture
def driver():
    """
    Fixture to initialize and quit WebDriver
    """
    if BROWSER.lower() == "chrome":
        options = Options()
        if HEADLESS:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    elif BROWSER.lower() == "firefox":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from webdriver_manager.firefox import GeckoDriverManager

        options = FirefoxOptions()
        if HEADLESS:
            options.add_argument("--headless")

        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    else:
        raise ValueError(f"Unsupported browser: {BROWSER}")

    driver.implicitly_wait(IMPLICIT_WAIT)
    yield driver
    driver.quit()


def test_open_google(driver):
    """
    Objective: Open google.com homepage and verify title
    """
    driver.get("https://www.google.com")
    assert "Google" in driver.title
