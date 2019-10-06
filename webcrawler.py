from bs4 import BeautifulSoup
import re
import dbmanager as dbm
from reppy.robots import Robots
import requests
import threading
from random import randint
import sys
import stopit


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
    except requests.exceptions.ConnectionError:
        return False


def get_domain(url):
    url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    if "/" in url:
        url = url[:url.find("/")]

    return url


dbm.create_table()

url_pattern = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
suburl_pattern = re.compile("(/[\w0-9]+)+")
html_cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

user_agent = 'Test'

def crawl_page(url):

    if not check_url(url):
        return

    domain = get_domain(url)


    print("Start URL: ", url)
    content = requests.get(url).text

    soup = BeautifulSoup(content, "html.parser")
    links = soup.find_all('a')
    try:
        title = soup.find('title').string
    except AttributeError:
        title = url

    title = str(title).replace("\n", " ")

    headings = soup.find_all('h2')
    headings.extend(soup.find_all('h3'))
    headings.extend(soup.find_all('h4'))

    index = 0
    for heading in headings:
        headings[index] = re.sub(html_cleanr, '', str(heading))
        headings[index] = headings[index].strip()
        index += 1

    heading_text = ""
    for heading in headings:
        heading_text += heading + " "


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


    for link in links:
        if "?" in link: # Found get parameter
            links.append(link[:link.find("?")]) # Add additional link with no get parameters



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





    filtered_links.append(url)

    sites = list()

    for link in filtered_links:
        if link in get_url(get_domain(link)):
            pass

        elif not link in url:
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

        content = content = requests.get(link).text
        soup = BeautifulSoup(content, "html.parser")
        try:
            title = soup.find('title').string
        except AttributeError:
            title = url

        title = str(title).replace("\n", " ")

        headings = soup.find_all('h2')
        headings.extend(soup.find_all('h3'))
        headings.extend(soup.find_all('h4'))

        small_index = 0
        for heading in headings:
            headings[index] = re.sub(html_cleanr, '', str(heading))
            headings[index] = headings[index].strip()
            small_index += 1

        heading_text = ""
        for heading in headings:
            heading_text += str(heading) + " "


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

        site = dbm.Site(link, title, description, heading_text)
        sites.append(site)
        filtered_links.remove(link)


    for site in sites:
        dbm.insert_into_sites(site)

    print("Links found: ", len(sites))

    dbm.remove_duplicates()

    index += 1


def crawl():
    while True:
        with stopit.ThreadingTimeout(100) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING

            rows = dbm.get_all_rows()

            if len(rows) > 0:
                index = randint(0, len(rows))
                link = rows[index - 1][0]

                crawl_page(link)
            else:
                crawl_page("https://github.com")

        print(len(dbm.get_all_rows()))





if len(sys.argv) != 2:
    exit("Usage: python webcrawler.py [amount of threads]")

amount_threads = None
try:
    amount_threads = int(sys.argv[1])
except:
    exit("Usage: python webcrawler.py [amount of threads]")

threads = list()

for i in range(amount_threads):
    t = threading.Thread(target=crawl, args=[])
    threads.append(t)

index = 0
for thread in threads:
    index += 1
    thread.start()
    print("Started Thread ", index)
