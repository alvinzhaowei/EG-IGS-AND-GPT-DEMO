from data.item_description_crawler import DescriptionCrawler
crawler = DescriptionCrawler()
url = "https://www.amazon.com.au/AZUL-Tile-Game-Pack-1/dp/B077MZ2MPW/ref=sr_1_5?c=ts&keywords=Board%2BGames&qid=1687402891&s=toys&sr=1-5&ts_id=5030765051&th=1"
result = crawler.crawl(url)
print(result)