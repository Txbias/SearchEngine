from bs4 import BeautifulSoup
import crawler
import dbmanager


def search(word):
    word_index = 0
    all_rows = dbmanager.get_all_rows()
    links = []
    for link in all_rows:
        links.append(link[0])

    for link in links:
        crawler1 = crawler.Crawler(link)
        crawler1.get_html()
        html = crawler1.content
        while word in html:
            word_index += 1
            print(word_index)
            html = html.replace(word, "", 1)

    return word_index

    
