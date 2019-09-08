import crawler
import sqlite3
import dbmanager
import search
import random
from threading import Thread
import socket
import httplib2
import time


crawler1 = crawler.Crawler("http://Youtube.com")

#crawler1.get_html()
#links = crawler1.get_links()
#print(links)

db = sqlite3.connect("data/links.sqlite")
cursor = db.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS links(id INTEGER PRIMARY KEY, link TEXT)
''')
db.commit()
db.close()

dbmanager.insert_into_links("http://www.facebook.com")
dbmanager.remove_duplicates()
all_rows = dbmanager.get_all_rows()
print(len(all_rows))
#search.search("html")


def find_links(count):
        for i in range(count):
                print(i)
                try:
                        all_rows = dbmanager.get_all_rows()
                        link = random.choice(all_rows)
                        link = link[0] # Extract link from tuple
                        crawler1 = crawler.Crawler(link)
                        crawler1.get_html()
                        links = crawler1.get_links()
                        print("links: ", len(links))
                        for link in links:
                                dbmanager.insert_into_links(link)

                        dbmanager.remove_duplicates
                except socket.error:
                        pass
                except httplib2.ServerNotFoundError:
                        pass
                except socket.gaierror:
                        pass
                except sqlite3.OperationalError:
                        pass


# Create threads
threads = []
for i in range(2):
        t = Thread(target=find_links, args=(2, ))
        threads.append(t)

# Start threads
index = 0
for t in threads:
       index += 1
       t.start()
       print("Started Thread ", index) 



print(len(dbmanager.get_all_rows()))
