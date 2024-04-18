from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from date_utils import get_k_months_before, is_date_after_or_equal_to_target
from workitem_handler import WorkItemHandler
import robocorp.log as log
import re
import time


class SortOption:
    RELEVANCY = "0"
    NEWEST = "1"
    OLDEST = "2"


class News_Scraper:
    """
    A scraper class for collecting news articles from the
    Los Angeles Times website.

    This class utilizes Selenium for web scraping to search
    for news articles based on specific search terms,
    topics, and the number of months past. It then writes the
    collected news information to an Excel file.
    """
    def __init__(self):
        """
        Initializes the News_Scraper instance
        """
        handler = WorkItemHandler()
        payload = handler.get_current_payload()

        self._browser = Selenium()
        self._URL = "https://www.latimes.com/"
        self._search_term = payload.get("search_term")
        self._num_months = payload.get("num_months")
        self._topics = payload.get("topics")
        self._news = []

        self.SEARCH_FIELD_SELECTOR = "xpath:/html/body/ps-header/header/div[2]/div[2]/form/label/input"
        self.SEARCH_BUTTON_SELECTOR = "xpath:/html/body/ps-header/header/div[2]/button"
        self.SEE_ALL_SELECTOR = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/aside/div/div[3]/div[1]/ps-toggler/ps-toggler/button"
        self.CANCEL_SUBSCRIPTION_SELECTOR = "#icon-close-greylt"
        self.SORT_BY_SELECTOR = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/div[1]/div[2]/div/label/select"
        self.ARTICLES_SELECTOR = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/ul/li"
        self.NEXT_PAGE_SELECTOR = "xpath:/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/div[2]/div[3]/a"
        self.MODAL_SELECTOR = "xpath://*[contains(@id, 'modality-')]"
        self.EXCEL_FILE_PATH = "output/news.news.xlsx"
        self.EXCEL_FILE_SHEET_NAME = "news"

    def fresh_news(self):
        """
        Orchestrates the process of opening the browser, searching for news
        articles based on the specified criteria, handling subscription
        popups, sorting the articles, checking relevant checkboxes,
        collecting the list of news, and finally writing the collected
        news to an Excel file.
        """
        try:
            self._open_browser()
            self._search_for()
            time.sleep(10)
            self._cancel_subscription_popup()
            time.sleep(3)
            self._sort_items(SortOption.NEWEST)
            time.sleep(3)
            self._check_checkboxes()
            time.sleep(3)
            self._get_news_lists()
            time.sleep(3)
            self._write_news_to_excel()
        except Exception as e:
            log.exception(f"An error occurred during the scraping process: {e}")

    def _open_browser(self):
        """
        Open the default web browser and navigate to the specified URL.
        """
        try:
            self._browser.open_available_browser(maximized=True)
            self._browser.go_to(self._URL)
            self._browser.wait_until_page_contains_element(self.SEARCH_BUTTON_SELECTOR, timeout=30)
            log.info("Browser opened and navigated to URL successfully.")
        except Exception as e:
            log.exception(f"An error occurred while trying to open the browser and navigate to the URL: {e}")

    def _search_for(self):
        """
        Perform a search using the provided search term.
        """
        try:
            self._browser.click_element_if_visible(self.SEARCH_BUTTON_SELECTOR)
            self._browser.input_text(self.SEARCH_FIELD_SELECTOR, self._search_term)
            self._browser.press_keys(self.SEARCH_FIELD_SELECTOR, "ENTER")
            self._browser.wait_until_page_contains_element(self.MODAL_SELECTOR, timeout=60)
            log.info("Search performed successfully.")
        except Exception as e:
            log.exception(f"An error occurred during the search operation: {e}")

    def _cancel_subscription_popup(self):
        """
        Wait for the icon with the specified selector to appear and click it.
        """
        try:
            script = """
            var shadowHost = document.querySelector("[id^='modality-']");
            var shadowRoot = shadowHost.shadowRoot;
            var closeBtn = shadowRoot.querySelector("a[aria-label='Close']");
            var clickEvent = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
            closeBtn.dispatchEvent(clickEvent);
            """
            self._browser.execute_javascript(script)
            self._browser.wait_until_page_contains_element(self.SORT_BY_SELECTOR)
            log.info("Subscription popup closed successfully.")
        except Exception as e:
            log.exception(f"An error occurred while trying to close the subscription popup: {e}")

    def _sort_items(self, sort_option):
        """
        Select a sorting option from the dropdown menu on the website.
        """
        try:
            self._browser.click_element_if_visible(self.SORT_BY_SELECTOR)
            self._browser.select_from_list_by_value(self.SORT_BY_SELECTOR, sort_option)
            self._browser.wait_until_page_contains_element(self.SEE_ALL_SELECTOR)
            log.info("Soring items successfully.")
        except Exception as e:
            log.exception(f"An error occurred while trying to sort items: {e}")

    def _check_checkboxes(self):
        """
        Check the checkboxes on the website based on the provided topics list.
        """
        try:
            self._browser.click_element_if_visible(self.SEE_ALL_SELECTOR)
            for checkbox in self._topics:
                checkbox_selector = f"xpath://span[text()='{checkbox}']/preceding-sibling::input[@type='checkbox']"
                self._browser.select_checkbox(checkbox_selector)
            self._browser.wait_until_page_contains_element(self.ARTICLES_SELECTOR)
            log.info("Checkboxes checked successfully.")
        except Exception as e:
            log.exception(f"An error occurred while trying to check checkboxes: {e}")

    def _get_news_lists(self):
        """
        Get a list of news articles published self.num_months months from now.
        """
        try:
            target_date = get_k_months_before(self._num_months)
            while True:
                news_articles = self._browser.find_elements(self.ARTICLES_SELECTOR)

                for article in news_articles:
                    news_data = self._extract_news_data(article)

                    if not is_date_after_or_equal_to_target(news_data["timestamp"], target_date):
                        return
                    self._news.append(news_data)
                    time.sleep(2)

                    self._browser.wait_until_page_contains_element(self.NEXT_PAGE_SELECTOR)
                    self._browser.click_element_if_visible(self.NEXT_PAGE_SELECTOR)
        except Exception as e:
            log.exception(f"An error occurred while trying to retrieve news articles: {e}")
            return

    def _extract_news_data(self, article):
        """
        Extract data from a single news article.

        Args:
            article: WebElement representing a single news article.

        Returns:
            dict: A dictionary containing extracted data from the news article.
        """
        try:
            title = article.find_element('xpath', ".//h3/a").text
            timestamp = article.find_element('xpath', ".//p[@class='promo-timestamp']").text
            description = article.find_element('xpath', ".//p[@class='promo-description']").text
            url = article.find_element('xpath', ".//h3/a").get_attribute("href")
            picture_filename = url.split('/')[-1].split('.')[0]
            title_search_count = len(re.findall(self._search_term, title, flags=re.IGNORECASE))
            description_search_count = len(re.findall(self._search_term, description, flags=re.IGNORECASE))

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
        except Exception as e:
            log.exception(f"An error occurred while trying to extract news data: {e}")
            return None

    def _write_news_to_excel(self):
        """
        Write news data to an Excel file.
        """
        try:
            excel = Files()
            excel.create_workbook(self.EXCEL_FILE_PATH)
            if self.EXCEL_FILE_SHEET_NAME not in excel.list_worksheets():
                excel.create_worksheet(self.EXCEL_FILE_SHEET_NAME)
            excel.set_active_worksheet(self.EXCEL_FILE_SHEET_NAME)
            for index, item in enumerate(self._news, start=1):
                if index == 1:
                    headers = list(item.keys())
                    excel.append_rows_to_worksheet([headers], header=True)
                row_values = list(item.values())
                excel.append_rows_to_worksheet([row_values])
            excel.save_workbook()
            excel.close_workbook()
        except Exception as e:
            log.exception(f"An error occurred while trying to write news data to Excel: {e}")


@task
def fresh_news():
    scraper = News_Scraper()
    scraper.fresh_news()
