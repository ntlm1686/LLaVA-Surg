import requests
from bs4 import BeautifulSoup
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("keyword", type=str)

cookies = {
    'device_view': 'full',
    '_pk_id.3.7d48': 'REPLACE WITH YOURS', # ! TODO
    'G_ENABLED_IDPS': 'google',
    'WebSurgRGPD': 'REPLACE WITH YOURS', # ! TODO
    'profile': '1',
    '_pk_ses.3.7d48': '1',
    'websurgsessionid': 'REPLACE WITH YOURS', # ! TODO
    '_pk_ref.3.7d48': 'REPLACE WITH YOURS', # ! TODO
}

if __name__ == "__main__":
    args = parser.parse_args()
    search_keyword = args.keyword
    base_url = "https://websurg.com"
    url = f"https://websurg.com/en/search/?q={search_keyword}"
    pagebase_url = f"https://websurg.com/en/search/?q={search_keyword}&p="
    session = requests.Session()
    session.cookies.update(cookies)
    r = session.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    pagination_div = soup.find('div', class_='pagination')
    option_tags = pagination_div.find_all('option')
    num_options = len(option_tags)
    print(f"Found {num_options} pages videos")
    videodict = {}

    for i in range(1, num_options+1):
        page_url = pagebase_url + str(i)
        print("Page URL:", page_url)
        pageres = session.get(page_url)
        pagesoup = BeautifulSoup(pageres.content, 'html.parser')
        href_list = [base_url + a['href'] for a in pagesoup.find_all('a', class_='content') if a['href'].startswith('/en/doi/')]
        print(href_list)

        for href in href_list:
            linkres = session.get(href)
            linksoup = BeautifulSoup(linkres.content, 'html.parser') # ! bug

            title_tag = linksoup.find('meta', property='og:title')
            description_tag = linksoup.find('meta', property='og:description')

            if title_tag:
                title = title_tag['content']
            else:
                title = "Title Not Found"

            if description_tag:
                description = description_tag['content']
            else:
                description = "Description Not Found"

            div_with_videoid = linksoup.find('div', attrs={'videoid': True})
            if div_with_videoid:
                videoid = div_with_videoid['videoid']
            else:
                videoid = "Videoid Not Found"

            data = {
                "title": title,
                "description": description,
                "videoid": videoid
            }

            videodict[href] = data

    with open(f"./{search_keyword}_list.json", "w", encoding="utf-8") as file:
        json.dump(videodict, file, indent=4)
