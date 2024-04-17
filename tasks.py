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
import time

class SortOption:
    RELEVANCY = "0"
    NEWEST = "1"
    OLDEST = "2"

browser = Selenium()
URL = "https://www.latimes.com/"
checkboxes = ["World & Nation", "California", "Business", "Technology and the Internet"]
search_term = "covid"

SEARCH_FIELD_SELECTOR = "xpath:/html/body/ps-header/header/div[2]/div[2]/form/label/input"
SEARCH_BUTTON_SELECTOR = "xpath:/html/body/ps-header/header/div[2]/button"
SEE_ALL_SELECTOR = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/aside/div/div[3]/div[1]/ps-toggler/ps-toggler/button"
CANCEL_SUBSCRIPTION_SELECTOR = "#icon-close-greylt"
SORT_BY_SELECTOR = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/div[1]/div[2]/div/label/select"
ARTICLES_SELECTOR = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/ul/li"
NEXT_PAGE_SELECTOR = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/div[2]/div[3]/a"
POPUP_MODAL_SELECTOR = "//*[contains(@id, 'modality-')]"

@task
def fresh_news():
    open_browser(URL)
    search_for(search_term)
    time.sleep(10)
    cancel_subscription_popup()
    time.sleep(5)
    sort_items(SortOption.NEWEST)
    time.sleep(5)
    check_checkboxes(checkboxes)
    time.sleep(5)
    news = get_news_lists(1)
    time.sleep(5)
    write_news_to_excel('output/news.xlsx', 'news', news)

def open_browser(url):
    """
    Open the default web browser and navigate to the specified URL.

    Args:
        url (str): The URL to navigate to.
    """
    browser.open_available_browser(maximized=True)
    browser.go_to(url)
    browser.wait_until_page_contains_element(SEARCH_BUTTON_SELECTOR, timeout=30)

def search_for(search_str):
    """
    Perform a search using the provided search term.

    Args:
        search_str (str): The term to search for.
    """
    browser.click_element_if_visible(SEARCH_BUTTON_SELECTOR)    
    browser.input_text(SEARCH_FIELD_SELECTOR, search_str)
    browser.press_keys(SEARCH_FIELD_SELECTOR, "ENTER")
    browser.wait_until_page_contains_element(f"xpath:{POPUP_MODAL_SELECTOR}",timeout=60)


def cancel_subscription_popup():
    """
    Wait for the icon with the specified selector to appear and click it.
    """
    try:
        script = """
        var shadowHost = document.querySelector("[id^='modality-']");
        var shadowRoot = shadowHost.shadowRoot;
        var closeButton = shadowRoot.querySelector("a[aria-label='Close']");
        var clickEvent = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
        closeButton.dispatchEvent(clickEvent);
        """
        browser.execute_javascript(script)        
        browser.wait_until_page_contains_element(SORT_BY_SELECTOR)
    except Exception as e:
        print(f"Error: {e}")


def check_checkboxes(checkboxes: List[str]) -> None:
    """
    Check the checkboxes on the website based on the provided list.

    Args:
        checkboxes (List[str]): A list of checkboxes to be checked. Each checkbox 
            should be a string representing the name or label of the checkbox.

    Returns:
        None
    """
    browser.click_element_if_visible(SEE_ALL_SELECTOR)

    for checkbox in checkboxes:
        checkbox_selector = f"xpath://span[text()='{checkbox}']/preceding-sibling::input[@type='checkbox']"
        browser.select_checkbox(checkbox_selector)

    browser.wait_until_page_contains_element(ARTICLES_SELECTOR)

def sort_items(sort_option: SortOption) -> None:
    """
    Select a sorting option from the dropdown menu on the website.

    Args:
        sort_option (str): The sorting option to select. This should be one of 
            the following: "relevancy", "newest", or "oldest".

    Returns:
        None
    """
    browser.click_element_if_visible(SORT_BY_SELECTOR)
    browser.select_from_list_by_value(SORT_BY_SELECTOR, sort_option)
    browser.wait_until_page_contains_element(SEE_ALL_SELECTOR)


def get_k_months_before(k):
    """
    Get the date k months before the current date.

    Args:
        k (int): Number of months before the current date.

    Returns:
        datetime: The target date k months before the current date.
    """
    current_date = datetime.today()
    target_date = current_date - relativedelta(months=k)
    return target_date


def is_date_after_or_equal_to_target(str_date, target_date):
    """
    Check if a given date is after or equal to a target date.

    Args:
        str_date (str): The date string to compare in the format 'Month Day, Year',
            e.g., 'Jan. 15, 2022' or 'December 25, 2021'.
        target_date (datetime): The target date to compare against.

    Returns:
        bool: True if the given date is after or equal to the target date, 
            False otherwise.
    """
    try:
        date_obj = datetime.strptime(str_date, '%b. %d, %Y')
    except ValueError:
        date_obj = datetime.strptime(str_date, '%B %d, %Y')
    
    return date_obj >= target_date


def get_news_lists(k: int) -> list:
    """
    Get a list of news articles published k months from now.

    Args:
        k (int): The number of months from now to retrieve news articles for.

    Returns:
        list: A list of news articles published k months from now.
    """
    news = []
    target_date = get_k_months_before(k)

    while True:
        news_articles = browser.find_elements(ARTICLES_SELECTOR)

        for article in news_articles:
            news_data = extract_news_data(article)

            if not is_date_after_or_equal_to_target(news_data["timestamp"], target_date):
                return news
            
            news.append(news_data)
            time.sleep(2)

        try:
            browser.wait_until_page_contains_element(NEXT_PAGE_SELECTOR)
            next_page = browser.click_element_if_visible(NEXT_PAGE_SELECTOR)
        except:
            return news
    
    return news


def extract_news_data(article):
    """
    Extract data from a single news article.

    Args:
        article: WebElement representing a single news article.

    Returns:
        dict: A dictionary containing extracted data from the news article.
    """
    title = article.find_element('xpath', ".//h3/a").text
    timestamp = article.find_element('xpath', ".//p[@class='promo-timestamp']").text
    description = article.find_element('xpath', ".//p[@class='promo-description']").text
    url = article.find_element('xpath', ".//h3/a").get_attribute("href")
    picture_filename = url.split('/')[-1].split('.')[0]
    
    title_search_count = len(re.findall(search_term, title, flags=re.IGNORECASE))
    description_search_count = len(re.findall(search_term, description, flags=re.IGNORECASE))

    money_pattern = r'\$\d+(\.\d+)?|\d+\s*(dollars|USD)'
    title_contains_money = bool(re.search(money_pattern, title))
    description_contains_money = bool(re.search(money_pattern, description))
    contains_money = bool(title_contains_money or description_contains_money)

    return {
        "title": title,
        "url": url,
        "description": description,
        "timestamp": timestamp,
        "picture_filename": picture_filename,
        "title_search_count": title_search_count,
        "description_search_count": description_search_count,
        "contains_money": contains_money
    }

def write_news_to_excel(file_path: str, sheet_name: str, news: list) -> None:
    """
    Write news data to an Excel file.

    Args:
        file_path (str): The file path to save the Excel file.
        sheet_name (str): The name of the worksheet to write the news data to.
        news (list): A list of dictionaries containing news data.

    Returns:
        None
    """
    excel = Files()

    excel.create_workbook(file_path) 
    if sheet_name not in excel.list_worksheets():
        excel.create_worksheet(sheet_name)
    
    excel.set_active_worksheet(sheet_name)
    for index, item in enumerate(news, start=1):
        if index == 1:
            headers = list(item.keys())
            excel.append_rows_to_worksheet([headers], header=True)
        
        row_values = list(item.values())
        excel.append_rows_to_worksheet([row_values])
    
    excel.save_workbook()
    excel.close_workbook()