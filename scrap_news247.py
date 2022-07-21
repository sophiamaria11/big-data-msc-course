import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import sys
import re


def scrap_news247(topic, pages=20) -> None:
    """
    Scraps articles from the news247 online journal and exports them to a csv file.

    :param topic: The topic of interest. You should double check that the topic
     is spelled correctly by visiting the website with your browser.
    :param pages: The number of pages that should be scrapped.
    """

    articles = []
    for page in tqdm(range(1, pages + 1), desc="Getting articles from page"):
        data = requests.get(f"https://www.news247.gr/{topic}?pages={page}")
        soup = BeautifulSoup(data.text, 'html.parser')
        article_summaries = soup.find_all('div', "article__summary")

        page_is_empty = not article_summaries
        if page_is_empty:  # If this page is empty the next pages will be empty too
            break

        for article_summary in article_summaries:
            contents = article_summary.contents
            article_detailed_text = contents[3].text

            article_datetime_posted = contents[5].text
            article_datetime_posted_datetime = to_datetime(article_datetime_posted)

            articles.append(
                (article_datetime_posted_datetime, article_detailed_text)
            )

    if articles:
        columns = ['date', 'text']
        df = pd.DataFrame(articles, columns=columns)
        df.to_csv(f"{topic}_news247_{datetime.today().strftime('%Y-%m-%d_%H:%M')}.csv", index=False, sep="|")


def to_datetime(date_string: str) -> datetime:
    """
    Converts strings of format '31 Μαρτίου 2021 12:34' to datetime

    :param date_string: The string to be processed ('31 Μαρτίου 2021 12:34')
    :return: the corresponding datetime object
    """

    # The month must be translated from greek to english first
    translate = {
        "Ιανουαρίου": "Jan",
        "Φεβρουαρίου": "Feb",
        "Μαρτίου": "Mar",
        "Απριλίου": "Apr",
        "Μαΐου": "May",
        "Ιουνίου": "Jun",
        "Ιουλίου": "Jul",
        "Αυγούστου": "Aug",
        "Σεπτεμβρίου": "Sep",
        "Οκτωβρίου": "Oct",
        "Νοεμβρίου": "Nov",
        "Δεκεμβρίου": "Dec",
    }
    greek_month = re.search(r"[A-Za-zΑ-Ωα-ωίϊΐόάέύϋΰήώ]+", date_string).group(0)
    date_string = date_string.replace(greek_month, translate[greek_month])

    return datetime.strptime(date_string, '%d %b %Y %H:%M')


if __name__ == '__main__':
    scrap_news247(sys.argv[1])
