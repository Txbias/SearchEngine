import httplib2 as hl
from bs4 import BeautifulSoup
import re
import urllib.request
import dbmanager as dbm
from reppy.robots import Robots
import requests
import threading
from random import randint
import sys


def get_url_to_robots(url):
    if str(url).endswith("/"):
        url = url + "robots.txt"
    else:
        url = url + "/robots.txt"

    return url


def get_url(domain):
    return "https://" + domain


def check_url(url):
    try:
        r = requests.get(url, timeout=10)
        if not r.status_code == 404:
            return True
        else:
            return False
    except ValueError:
        return False

    except requests.exceptions.MissingSchema:
        return False
    except requests.exceptions.ConnectTimeout:
        return False
    except requests.exceptions.ReadTimeout:
        return False


def get_domain(url):
    url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    if "/" in url:
        url = url[:url.find("/")]

    return url


dbm.create_table()

url_pattern = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
suburl_pattern = re.compile("(/[\w0-9]+)+")
user_agent = 'Test'

def crawl_page(url):

    if not check_url(url):
        return

    domain = get_domain(url)
    #http = hl.Http()

    #content = str(http.request(url)[1]).strip()

    print("Start URL: ", url)
    content = requests.get(url).text

    soup = BeautifulSoup(content, "html.parser")
    links = soup.find_all('a')
    try:
        title = soup.find('title').string
    except AttributeError:
        title = url

    title = str(title).replace("\n", " ")
    metas = soup.find_all('meta')
    description = ""

    for meta in metas:
        try:
            if "description" in meta.get('name'):
                description = meta.get('content')
        except TypeError:
            pass

    index = 0
    for link in links:
        links[index] = link.get('href')
        index += 1

    links = list(filter(None, links)) # remove empty strings


    links = list(set(links)) # removing duplicates
    filtered_links = list()
    for link in links:
        if url_pattern.match(link):
            filtered_links.append(link)
            links.remove(link)
        elif suburl_pattern.match(link):
            filtered_links.append(url + link)
            links.remove(link)


    print("Found links: ", len(filtered_links))
    for link in filtered_links:
        if not check_url(link):
            filtered_links.remove(link)



    #print(filtered_links)

    filtered_links.append(url)

    sites = list()

    for link in filtered_links:
        if not link in url:
            print("link: ", link)
            domain = get_domain(link)
            robots_url = get_url_to_robots(get_url(domain))
            try:
                robots = Robots.fetch(robots_url)
                if not robots.allowed(link, user_agent):
                    print("Removed")
                    filtered_links.remove(link)
            except:
                print("Removed")
                filtered_links.remove(link)


    index = 0
    for link in filtered_links:

        if "#" in link:
            link = link[:link.find("#")]
            filtered_links[index] = link

        content = content = requests.get(link).text     # str(http.request(link)[1]).strip() # content = str(http.request(link)[1]).encode('utf-8').strip().decode()
        soup = BeautifulSoup(content, "html.parser")
        try:
            title = soup.find('title').string
        except AttributeError:
            title = url

        title = str(title).replace("\n", " ")
        metas = soup.find_all('meta')
        description = ""

        for meta in metas:
            try:
                if "description" in meta.get('name'):
                    description = meta.get('content')
            except TypeError:
                pass

        if description is None:
            description = ""

        site = dbm.Site(link, title, description)
        sites.append(site)
        filtered_links.remove(link)


    for site in sites:
        dbm.insert_into_sites(site)

    print("Links found: ", len(sites))

    dbm.remove_duplicates()

    index += 1


def crawl():
    rows = dbm.get_all_rows()

    if len(rows) > 0:
        index = randint(0, len(rows))
        link = rows[index - 1][0]

        crawl_page(link)
    else:
        crawl_page("https://github.com")



threads = list()

for i in range(4):
    t = threading.Thread(target=crawl, args=[])
    threads.append(t)

index = 0
for thread in threads:
    index += 1
    thread.start()
    print("Started Thread ", index)
