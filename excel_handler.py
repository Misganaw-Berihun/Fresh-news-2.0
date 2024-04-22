from RPA.Excel.Files import Files
from constants import FileConstants
import robocorp.log as log


class ExcelHandler:
    def __init__(self):
        self._excel = Files()

    def write_news_to_excel(self, news):
        try:
            excel = Files()
            excel.create_workbook(FileConstants.EXCEL_FILE_PATH)

            if (FileConstants.EXCEL_FILE_SHEET_NAME
                    not in excel.list_worksheets()):
                excel.create_worksheet(FileConstants.EXCEL_FILE_SHEET_NAME)

            excel.set_active_worksheet(FileConstants.EXCEL_FILE_SHEET_NAME)
            for index, item in enumerate(news, start=1):
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
