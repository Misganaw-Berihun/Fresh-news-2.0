from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from enum import Enum
from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re


class SortOption:
    RELEVANCY = "0"
    NEWEST = "1"
    OLDEST = "2"

browser = Selenium()
URL = "https://www.latimes.com/"
checkboxes = ["World & Nation", "California", "Business", "Technology and the Internet"]
@task
def minimal_task():
    open_browser(URL)
    search_for("covid")
    check_checkboxes(checkboxes)
    sort_items(SortOption.NEWEST)

def open_browser(url):
    """
    Open the default web browser and navigate to the specified URL.

    Args:
        url (str): The URL to navigate to.
    """
    browser.open_available_browser(maximized=True)
    browser.go_to(url)


def search_for(search_str):
    """
    Perform a search using the provided search term.

    Args:
        search_str (str): The term to search for.
    """
    search_field_selector = "xpath:/html/body/ps-header/header/div[2]/div[2]/form/label/input"
    search_button_selector = "xpath:/html/body/ps-header/header/div[2]/button"
    
    browser.click_element_if_visible(search_button_selector)    
    browser.input_text(search_field_selector, search_str)
    browser.press_keys(search_field_selector, "ENTER")


def check_checkboxes(checkboxes: List[str]) -> None:
    """
    Check the checkboxes on the website based on the provided list.

    Args:
        checkboxes (List[str]): A list of checkboxes to be checked. Each checkbox 
            should be a string representing the name or label of the checkbox.

    Returns:
        None
    """
    see_all_selector = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/aside/div/div[3]/div[1]/ps-toggler/ps-toggler/button"
    browser.click_element_if_visible(see_all_selector)

    for checkbox in checkboxes:
        checkbox_selector = f"xpath://span[text()='{checkbox}']/preceding-sibling::input[@type='checkbox']"

        if browser.checkbox_should_not_be_selected(checkbox_selector):
            browser.select_checkbox(checkbox_selector)


def sort_items(sort_option: SortOption) -> None:
    """
    Select a sorting option from the dropdown menu on the website.

    Args:
        sort_option (str): The sorting option to select. This should be one of 
            the following: "relevancy", "newest", or "oldest".

    Returns:
        None
    """
    sort_by_selector = 'xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/div[1]/div[2]/div/label/select'
    browser.select_from_list_by_value(sort_by_selector, sort_option
    )