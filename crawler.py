import httplib2 as hl
from bs4 import BeautifulSoup


class Crawler:

    url = ""
    http = hl.Http()
    content = ""

    def __init__(self, url):
        self.url = url


    def get_html(self):
        self.content = self.http.request(self.url)[1]
        self.content = self.content
        #print(str(self.content))
        self.content = str(self.content)
        self.content = self.content.encode("utf-8").strip()
        self.content = self.content.decode()
    

    def get_links(self):
        soup = BeautifulSoup(self.content, "html.parser")
        links_old = soup.find_all('a')
        links = []
        for link in links_old:
            links.append(link.get("href"))
        
        links = list(filter(None, links)) # remove empty strings

        index = 0
        for link in links:
            if "//" in link:
                links[index] = links[index].replace("//", "/")
            while links[index].startswith("/"):
                links[index] = links[index].replace("/", "", 1)
            if not link.startswith("http://") or not link.startswith("https:"):
                    if link.lower().startswith("www") or ".com" in link or ".de" in link:
                        links[index] = "http://" + link
                    else:
                        links[index] = self.url + link

            hindex = link.count("http:")

            if hindex > 1:
                links[index] = links[index].replace("http://", "", 1)
            
            while "////" in link:
                links[index] = links[index].replace("////", "//", 1)
            index += 1

        links = list(set(links)) # remove duplicates
        
        return links


    def get_robots(self):
        pass
