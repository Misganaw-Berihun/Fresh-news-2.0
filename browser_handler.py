from RPA.Browser.Selenium import Selenium
from workitem_handler import WorkItemHandler

from date_utils import (
    get_k_months_before,
    is_date_after_or_equal_to_target
)
from utils import (
    download_image,
    contains_money,
    extract_image_filename,
    extract_word_count
)
from constants import (
    Selectors
)
import robocorp.log as log
import time


class BrowserHandler:
    def __init__(self, url):
        handler = WorkItemHandler()
        payload = handler.get_current_payload()

        self._browser = Selenium()
        self._URL = url
        self._search_term = payload.get("search_term")
        self._num_months = payload.get("num_months")
        self._news = []

    def open_browser(self):
        try:
            self._browser.open_available_browser(maximized=True)
            self._browser.go_to(self._URL)
            self._browser.wait_until_page_contains_element(
                Selectors.SEARCH_BUTTON
            )
            log.info("Browser opened and navigated to URL successfully.")
        except Exception as e:
            log.exception(
                "An error occurred while trying to open the browser" +
                f"and navigate to the URL: {e}"
            )

    def search_for(self):
        try:
            self._browser.click_element_if_visible(
                Selectors.SEARCH_BUTTON
            )
            self._browser.input_text(
                Selectors.SEARCH_FIELD, self._search_term
            )
            self._browser.press_keys(
                Selectors.SEARCH_FIELD, "ENTER"
            )
            self._browser.wait_until_page_contains_element(
                Selectors.SORT_BY
            )
            log.info("Search performed successfully.")
        except Exception as e:
            log.exception(
                f"An error occurred during the search operation: {e}"
            )

    def cancel_subscription_popup(self):
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
            self._browser.execute_javascript(script)
            time.sleep(1)
            self._browser.execute_javascript("window.scrollTo(0, 0);")
            log.info("Subscription popup closed successfully.")
        except Exception as e:
            log.exception(
                "An error occurred while trying to close" +
                f"the subscription popup: {e}"
            )

    def sort_items(self, sort_option):
        try:
            self._browser.click_element_if_visible(Selectors.SORT_BY)
            self._browser.select_from_list_by_value(
                Selectors.SORT_BY,
                sort_option
            )
            time.sleep(5)
            self._browser.wait_until_page_contains_element(
                Selectors.ARTICLES
            )
            log.info("Sorting items successfully.")
        except Exception as e:
            log.exception(
                f"An error occurred while trying to sort items: {e}"
            )

    def get_news_lists(self):
        MAX_PAGES = 10
        current_page = 1
        try:
            target_date = get_k_months_before(self._num_months)
            while True:
                news_articles = self._browser.find_elements(
                    Selectors.ARTICLES
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

                if current_page == MAX_PAGES:
                    break

                self._browser.wait_until_element_is_visible(
                    Selectors.NEXT_PAGE
                )
                self._browser.click_element(
                    Selectors.NEXT_PAGE
                )
                current_page += 1
        except Exception as e:
            log.exception(
                "An error occurred while trying to retrieve"
                f" news articles: {e}"
            )

    def _extract_news_data(self, article):
        try:
            title = article.find_element(
                'xpath',
                "//h3[@class='promo-title']/a"
            ).text
            timestamp = article.find_element(
                'xpath',
                "//p[@class='promo-timestamp']"
            ).text
            description = article.find_element(
                'xpath',
                "//p[@class='promo-description']"
            ).text
            url = article.find_element(
                'xpath',
                "//h3[@class='promo-title']/a"
            ).get_attribute("href")
            img_src = article.find_element(
                'xpath',
                "//img[@class='image']"
            ).get_attribute("src")

            title_search_count = extract_word_count(
                title,
                self._search_term
            )
            description_search_count = extract_word_count(
                description,
                self._search_term
            )
            image_filename = extract_image_filename(img_src)
            title_contains_money = contains_money(title)
            description_contains_money = contains_money(
                description
            )
            article_contains_money = bool(
                title_contains_money or
                description_contains_money
            )

            if image_filename:
                download_image(img_src, image_filename)
                time.sleep(2)

            return {
                "title": title,
                "url": url,
                "description": description,
                "timestamp": timestamp,
                "picture_filename": image_filename,
                "title_search_count": title_search_count,
                "description_search_count": description_search_count,
                "contains_money": article_contains_money
            }
        except Exception as e:
            log.exception(
                f"An error occurred while trying to extract news data: {e}"
            )
            return None

    def get_news(self):
        return self._news.copy()
