from robocorp.tasks import task
from robocorp.tasks import get_output_dir
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.keys import Keys

@task
def minimal_task():
    browser = Selenium(auto_close=False)
    browser.open_available_browser('https://www.latimes.com/')
    browser.click_element_when_visible(xpath="/html/body/ps-header/header/div[2]/button")
