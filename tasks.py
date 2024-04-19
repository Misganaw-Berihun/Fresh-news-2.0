from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from workitem_handler import WorkItemHandler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import (
    expected_conditions as EC
)
from urllib.request import (
    urlretrieve,
    urlparse,
    unquote
)
from date_utils import (
    get_k_months_before,
    is_date_after_or_equal_to_target
)
from pathlib import Path
import robocorp.log as log
import re
import os
import time


class SortOption:
    RELEVANCY = "0"
    NEWEST = "1"
    OLDEST = "2"


class News_Scraper:
    def __init__(self):
        handler = WorkItemHandler()
        payload = handler.get_current_payload()

        self._browser = Selenium()
        self._URL = "https://www.latimes.com/"
        self._search_term = payload.get("search_term")
        self._num_months = payload.get("num_months")
        self._news = []

        self.SEARCH_FIELD_SELECTOR = (
            "xpath:/html/body/ps-header/header/div[2]/div[2]"
            "/form/label/input"
        )
        self.SEARCH_BUTTON_SELECTOR = (
            "xpath:/html/body/ps-header/header/div[2]/button"
        )
        self.CANCEL_SUBSCRIPTION_SELECTOR = (
            "#icon-close-greylt"
        )
        self.SORT_BY_SELECTOR = (
            "xpath:/html/body/div[2]/ps-search-results-module/"
            "form/div[2]/ps-search-filters/div/main/div[1]/"
            "div[2]/div/label/select"
        )
        self.ARTICLES_SELECTOR = (
            "xpath:/html/body/div[2]/ps-search-results-module/"
            "form/div[2]/ps-search-filters/div/main/ul/li"
        )
        self.NEXT_PAGE_SELECTOR = (
            "xpath://div[@class='search-results-module-next-page']"
        )
        self.MODAL_SELECTOR = (
            "xpath://*[contains(@id, 'modality-')]"
        )
        self.EXCEL_FILE_PATH = (
            "output/news.news.xlsx"
        )
        self.EXCEL_FILE_SHEET_NAME = "news"

    def fresh_news(self):
        try:
            self._open_browser()
            self._search_for()
            self._cancel_subscription_popup()
            self._sort_items(SortOption.NEWEST)
            self._get_news_lists()
            self._write_news_to_excel()
        except Exception as e:
            log.exception(
                f"An error occurred during the scraping process: {e}"
            )

    def _open_browser(self):
        try:
            self._browser.open_available_browser(maximized=True)
            self._browser.go_to(self._URL)
            WebDriverWait(self._browser.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, self.SEARCH_BUTTON_SELECTOR)
                    )
            )
            log.info("Browser opened and navigated to URL successfully.")
        except Exception as e:
            log.exception(
                "An error occurred while trying to open the browser" +
                f"and navigate to the URL: {e}"
            )

    def _search_for(self):
        try:
            self._browser.click_element_if_visible(
                self.SEARCH_BUTTON_SELECTOR
            )
            self._browser.input_text(
                self.SEARCH_FIELD_SELECTOR, self._search_term
            )
            self._browser.press_keys(
                self.SEARCH_FIELD_SELECTOR, "ENTER"
            )
            WebDriverWait(self._browser.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, self.SORT_BY_SELECTOR)
                    )
            )
            log.info("Search performed successfully.")
        except Exception as e:
            log.exception(
                f"An error occurred during the search operation: {e}"
            )

    def _cancel_subscription_popup(self):
        try:
            self._browser.execute_javascript(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(5)
            script = """
                var shadowHost = document.querySelector("[id^='modality-']");
                var shadowRoot = shadowHost.shadowRoot;
                var closeBtn = shadowRoot.querySelector("a[aria-label='Close']"
                );
                var clickEvent = new MouseEvent('click',
                    {bubbles: true, cancelable: true, view: window}
                );
                closeBtn.dispatchEvent(clickEvent);
            """
            time.sleep(1)
            self._browser.execute_javascript("window.scrollTo(0, 0);")
            self._browser.execute_javascript(script)
            log.info("Subscription popup closed successfully.")
        except Exception as e:
            log.exception(
                "An error occurred while trying to close" +
                f"the subscription popup: {e}"
            )

    def _sort_items(self, sort_option):
        try:
            self._browser.click_element_if_visible(self.SORT_BY_SELECTOR)
            self._browser.select_from_list_by_value(
                self.SORT_BY_SELECTOR,
                sort_option
            )
            time.sleep(5)
            WebDriverWait(self._browser.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, self.ARTICLES_SELECTOR)
                    )
            )
            log.info("Soring items successfully.")
        except Exception as e:
            log.exception(
                f"An error occurred while trying to sort items: {e}"
            )

    def _get_news_lists(self):
        try:
            target_date = get_k_months_before(self._num_months)
            while True:
                news_articles = self._browser.find_elements(
                    self.ARTICLES_SELECTOR
                )

                for article in news_articles:
                    news_data = self._extract_news_data(
                        article
                    )

                    if not is_date_after_or_equal_to_target(
                            news_data["timestamp"],
                            target_date
                    ):
                        return

                    self._news.append(news_data)    

                    try:
                        self._browser.wait_until_page_contains_element(
                            self.NEXT_PAGE_SELECTOR
                        )
                        self._browser.click_element(
                            self.NEXT_PAGE_SELECTOR
                        )
                    except Exception:
                        return
        except Exception as e:
            log.exception(
                "An error occurred while trying to retrieve"
                f" news articles: {e}"
            )

    def _download_image(self, image_url, file_name):
        folder_path = "output/images/"
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(folder_path, file_name)
        urlretrieve(image_url, file_path)

    def _extract_news_data(self, article):
        try:
            title = article.find_element(
                'xpath', 
                ".//h3/a"
            ).text
            timestamp = article.find_element(
                'xpath',
                ".//p[@class='promo-timestamp']"
            ).text
            description = article.find_element(
                'xpath',
                ".//p[@class='promo-description']"
            ).text
            url = article.find_element(
                'xpath',
                ".//h3/a"
            ).get_attribute("href")
            img_src = article.find_element(
                'xpath',
                ".//img[@class='image']"
            ).get_attribute("src")

            title_search_count = len(re.findall(
                self._search_term, title,
                flags=re.IGNORECASE
            ))
            description_search_count = len(re.findall(
                self._search_term, description,
                flags=re.IGNORECASE
            ))

            decoded_src = unquote(img_src)
            parsed_url = urlparse(decoded_src)
            image_filename = parsed_url.query.split('/')[-1]

            money_pattern = r'\$\d+(\.\d+)?|\d+\s*(dollars|USD)'
            title_contains_money = bool(re.search(money_pattern, title))
            description_contains_money = bool(re.search(
                money_pattern,
                description
            ))
            contains_money = bool(
                title_contains_money or
                description_contains_money
            )

            self._download_image(img_src, image_filename)
            time.sleep(2)

            return {
                "title": title,
                "url": url,
                "description": description,
                "timestamp": timestamp,
                "picture_filename": image_filename,
                "title_search_count": title_search_count,
                "description_search_count": description_search_count,
                "contains_money": contains_money
            }
        except Exception as e:
            log.exception(
                f"An error occurred while trying to extract news data: {e}"
            )
            return None

    def _write_news_to_excel(self):
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
            log.exception(
                "An error occurred while trying to write news"
                f" data to Excel: {e}"
            )


@task
def fresh_news():
    scraper = News_Scraper()
    scraper.fresh_news()
