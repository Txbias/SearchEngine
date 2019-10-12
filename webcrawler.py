from bs4 import BeautifulSoup
import re
import dbmanager as dbm
from reppy.robots import Robots
import requests
import threading
import random
import sys
import stopit
import time
from datetime import datetime


url_pattern = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
suburl_pattern = re.compile("(/[\w0-9]+)+")
html_cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

user_agent = 'search'
date_format = "%m/%d/%Y"

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
        if not r.status_code == 404 or not r.status_code == 500:
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


def isExisting(link, rows):
    return_value = False
    for row in rows:
        if link in row[0][0]:
            return_value = True

    return return_value

def get_site_information(url):

    starttime = time.time()
    content = requests.get(url).text
    endtime = time.time()
    totaltime = round(endtime - starttime, 3)

    soup = BeautifulSoup(content, "html.parser")

    try:
        title = soup.find('title').string
    except AttributeError:
        title = url

    title = str(title).replace("\n", " ")

    headings = soup.find_all('h1')
    headings.extend(soup.find_all('h2'))
    headings.extend(soup.find_all('h3'))
    headings.extend(soup.find_all('h4'))
    headings.extend(soup.find_all('h5'))

    index = 0
    for heading in headings:
        headings[index] = re.sub(html_cleanr, '', str(heading))
        headings[index] = headings[index].strip()
        index += 1

    heading_text = ""
    for heading in headings:
        heading_text += heading + " "

    if len(heading_text) > 700:
        heading_text = heading_text[:700]


    paragraphs = soup.find_all('p')
    p_text = ""

    for p in paragraphs:
        p_text += str(p)

    p_text = re.sub(html_cleanr, '', p_text)
    p_text = " ".join(p_text.split())

    if len(p_text) > 700:
        p_text = p_text[:700]


    metas = soup.find_all('meta')
    description = ""

    for meta in metas:
        try:
            if "description" in meta.get('name'):
                description = meta.get('content')
        except TypeError:
            pass

    html_tag = soup.find("html")
    language = ""
    try:
        language = html_tag.get("lang")
    except:
        pass

    if language is None:
        language = " "

    datestring = time.strftime(date_format, time.gmtime())


    all_rows = dbm.get_all_rows("sites")
    times_found = 0
    for row in all_rows:
        if url in row[0][0]:
            times_found = int(row[0][6] + 1)


    site = dbm.Site(url, title, description, heading_text, p_text, totaltime, times_found, language, datestring)

    return site


def crawl_page(url):

    if not check_url(url):
        return

    domain = get_domain(url)
    try:
        content = requests.get(url).text
    except requests.exceptions.ConnectionError:
        return

    soup = BeautifulSoup(content, "html.parser")

    print("Start URL: ", url)
    site = get_site_information(url)
    rows = dbm.get_all_rows("sites")
    for i in range(100):
        try:
            if isExisting(site.link, rows):
                dbm.update_column(site)
                break;
            else:
                dbm.insert_into_sites(site)
                break;
        except:
            pass

    links = soup.find_all('a')

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
            if str(link).startswith("/") and url.endswith("/"):
                filtered_links.append(get_url(get_domain(url[:-1])) + link)
            else:
                filtered_links.append(get_url(get_domain(url)) + link)

            links.remove(link)

    index = 0
    for link in filtered_links:
        if "?" in link: # Found get parameter
            filtered_links[index] = filtered_links[index][:filtered_links[index].find("?")] # Remove get parameters

        if "#" in link:
            filtered_links[index] = filtered_links[index][:filtered_links[index].find("#")]

        if "%" in link:
            filtered_links[index] = filtered_links[index][:filtered_links[index].find("%")]

        index += 1


    filtered_links.append(url)

    print("Links found: ", len(filtered_links))
    for link in filtered_links:
        if not check_url(link):
            filtered_links.remove(link)


    sites = list()

    for link in filtered_links:
        if link in get_url(get_domain(link)):
            pass

        elif not link in url:
            domain = get_domain(link)
            robots_url = get_url_to_robots(get_url(domain))
            try:
                robots = Robots.fetch(robots_url)
                if not robots.allowed(link, user_agent):
                    if link.endswith("/"):
                        if robots.allowed(link[:-1].allowed(link[:-1], user_agent)):
                            pass
                        else:
                            filtered_links.remove(link)
                    else:
                        filtered_links.remove(link)
                else:
                    print("link: ", link)
            except:
                filtered_links.remove(link)


    for link in filtered_links:
        if get_url(get_domain(link)) + str("/sitemap") in link:
            print(1)
            continue

        sites.append(get_site_information(link))
        filtered_links.remove(link)

    rows = dbm.get_all_rows("sites")
    for site in sites:
        for i in range(100):
            try:
                if isExisting(site.link, rows):
                    dbm.update_column(site)
                    break;
                else:
                    dbm.insert_into_sites(site)
                    break;
            except:
                print("Exception")

    print("Links found: ", len(sites))

    dbm.remove_duplicates()



def crawl():
    while True:

        crawl_rows = dbm.get_all_rows("crawl")
        if len(crawl_rows) < 2:
            sites_rows = dbm.get_all_rows("sites")
            print("sites: " + str(len(sites_rows)))
            sites_rows.sort(key=lambda row: datetime.strptime(row[8], date_format)) # Sort by date
            sites_rows = sites_rows[:400] # Get the 400 oldest links
            for row in sites_rows:
                for i in range(100): # trys it 100 times
                    try:
                        dbm.insert_into_crawl(str(row[0]))
                        break
                    except dbm.sqlite3.OperationalError:
                        pass




        with stopit.ThreadingTimeout(100) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING

            rows = dbm.get_all_rows("crawl")
            print("URLS in crawl memory: " + str(len(rows)))

            if len(rows) > 1:
                index = random.randint(0, len(rows) - 1)
                link = rows[index]
                dbm.delete_from_crawl(link[0])
                crawl_page(link[0])
            else:
                crawl_pages = ["https://www.Gitub.com", "https://twitter.com", "https://google.de", "https://leo.org",
                               "https://wikipedia.org"]
                crawl_page(random.choice(crawl_pages))

        print("Total found sites: " + str(len(dbm.get_all_rows("sites"))))




if __name__ == "__main__":
    dbm.create_tables()

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
        time.sleep(2)
