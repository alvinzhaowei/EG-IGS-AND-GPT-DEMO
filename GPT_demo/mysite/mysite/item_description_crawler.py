import requests
from bs4 import BeautifulSoup
import re


class DescriptionCrawler:
    def crawl(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0 '}
        r = requests.get(url, headers=header, allow_redirects=True)
        html = r.content
        soup = BeautifulSoup(html, "html.parser")
        # with open("test_file", "w", encoding="utf-8") as f:
        #     f.write(soup.text)
        text = soup.get_text()
        lines = re.split('\r|\n', text)
        lines = [item for item in lines if item != '']
        # print(lines)
        keywords = ["Product description", "About this item"]
        for line in lines:
            for keyword in keywords:
                if line.find(keyword) >= 0:
                    return line
        return "Not found"
