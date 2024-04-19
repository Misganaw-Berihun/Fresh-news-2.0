# Fresh-news-2.0

## Overview

This project aims to automate the process of extracting data from a news website using Robocorp. The extracted data includes news titles, dates, descriptions, and images. Additionally, the bot identifies the presence of specific phrases, counts occurrences of search phrases in the title and description, and determines whether the news contains any mention of money.

## Challenge Details

### Source

The news site choosen for this project is:
- [Los Angeles Times](https://www.latimes.com/)

### Parameters

The process should accept the following parameters:

1. **Search phrase:** The keyword(s) to search for in the news articles.
2. **Number of months:** Specifies the time period for which you need to receive news. For example, `1` for the current month only, `2` for the current and previous month, and so on.

### Process Steps

1. **Open the site:** Navigate to the selected news website.
2. **Enter search phrase:** Input the search phrase in the website's search field.
3. **Select news category:** If applicable, choose the desired news category or section.
4. **Retrieve latest news:** Select the newest news articles from the search results.
5. **Extract data:** Capture the title, date, description, and image URL of each news article.
6. **Store data in Excel:** Save the extracted data in an Excel file, including title, date, description, picture filename, count of search phrases in the title and description, and whether the news contains any mention of money.
