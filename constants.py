class SortOption:
    RELEVANCY = "0"
    NEWEST = "1"
    OLDEST = "2"


class Selectors:
    SEARCH_FIELD = "xpath://input[@data-element='search-form-input']"
    SEARCH_BUTTON = "xpath://button[@data-element='search-button']"
    CANCEL_SUBSCRIPTION = "#icon-close-greylt"
    SORT_BY = "xpath://select[@class='select-input']"
    ARTICLES = "xpath://ul[@class='search-results-module-results-menu']/li"
    NEXT_PAGE = "xpath://div[@class='search-results-module-next-page']"
    MODAL = "xpath://*[contains(@id, 'modality-')]"


class FileConstants:
    EXCEL_FILE_PATH = "output/news.news.xlsx"
    EXCEL_FILE_SHEET_NAME = "news"