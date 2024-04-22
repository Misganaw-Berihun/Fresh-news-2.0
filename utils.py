from pathlib import Path
from urllib.request import (
    urlretrieve,
    unquote,
    urlparse
)
import robocorp.log as log
import os
import re


def download_image(image_url, file_name):
    folder_path = "output/images/"
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    urlretrieve(image_url, file_path)


def contains_money(text):
    try:
        money_pattern = r'\$\d+(\.\d+)?|\d+\s*(dollars|USD)'
        return bool(re.search(money_pattern, text))
    except Exception as e:
        log.exception("An error occurred while checking" +
                      f"if text contains money: {e}")
        return False


def extract_word_count(text, word):
    try:
        search_count = len(re.findall(
            word, text,
            flags=re.IGNORECASE
            ))
        return search_count
    except Exception as e:
        log.exception("An error occurred while extracting" +
                      f" search count: {e}")
        return None


def extract_image_filename(img_src):
    try:
        decoded_src = unquote(img_src)
        parsed_url = urlparse(decoded_src)
        image_filename = (
            parsed_url.query.split('/')[-1] if
            parsed_url.query else
            parsed_url.path.split('/')[-1]
        )
        return image_filename
    except Exception as e:
        log.exception("An error occurred while" +
                      f"extracting image filename: {e}")
        return None
