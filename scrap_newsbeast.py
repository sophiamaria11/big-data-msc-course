import requests
import re
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
import pandas as pd

topic = "dimitris-lignadis"
num_pages = 16  # WARNING: If the number of pages exceed the one available by the site, the site returns the page 1.

articles = []
for page in range(1, num_pages + 1):
    data = requests.get(f"https://www.newsbeast.gr/tag/{topic}/page/{page}")
    soup = BeautifulSoup(data.text, 'html.parser')
    results = soup.find_all('div', "jsx-3244605671 articleDisplay")

    if not results:
        break

    for element in results:

        date_regex = r'\d{2}\/\d{2}\/\d{4}'
        raw_string_with_date = element.contents[3].text
        date_included = re.search(date_regex, raw_string_with_date)
        if date_included:
            date = date_included.group(0)
        elif re.search(r'(\d+) ώ', raw_string_with_date):
            posted_X_hours_ago = int(re.search(r'(\d+) ώ', raw_string_with_date).group(1))
            temp = datetime.today() - timedelta(hours=0, minutes=posted_X_hours_ago * 60)
            date = temp.strftime('%d/%m/%Y')
        else:
            date = datetime.today().strftime('%d/%m/%Y')

        date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S')
        title = element.contents[0].text
        articles.append((date, title))

    columns = ['date', 'text']
    df = pd.DataFrame(articles, columns=columns)
    df.to_csv(f"{topic}_newsbeast_{datetime.today().strftime('%Y-%m-%d_%H:%M')}.csv", index=False, sep="|")
