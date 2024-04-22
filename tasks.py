from robocorp.tasks import task
from browser_handler import BrowserHandler
from excel_handler import ExcelHandler
from constants import SortOption


@task
def fresh_news():
    url = "https://www.latimes.com/"
    browser_handler = BrowserHandler(url)
    browser_handler.open_browser()
    browser_handler.search_for()
    browser_handler.cancel_subscription_popup()
    browser_handler.sort_items(SortOption.NEWEST)
    browser_handler.get_news_lists()

    news = browser_handler.get_news()
    excel_handler = ExcelHandler()
    excel_handler.write_news_to_excel(news)
