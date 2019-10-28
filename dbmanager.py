import sqlite3


def create_tables():
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites(link TEXT, title TEXT, description TEXT, heading TEXT,
            paragraph TEXT, answer_time TEXT, times_found TEXT, language TEXT, date TEXT)
    ''')
    db.commit()
    db.close()

    db = sqlite3.connect("data/crawl.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl(link TEXT)
    ''')
    db.commit()
    db.close()


def insert_into_sites(site):
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            INSERT INTO sites(link, title, description, heading, paragraph, answer_time, times_found, language, date) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (site.link, site.title, site.description, site.heading, site.paragraph, site.answer_time, site.times_found, site.language, site.date))

    db.commit()
    db.close()


def update_column(site):
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            UPDATE sites SET title = ?, description = ?, heading = ?, paragraph = ?, answer_time = ?, times_found = ? WHERE link = ?
    ''', (site.title, site.description, site.heading, site.paragraph, site.answer_time, site.times_found, site.link))
    db.commit()
    cb.close()

def insert_into_crawl(link):
    db = sqlite3.connect("data/crawl.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            INSERT INTO crawl(link) VALUES(?)
    ''', (link, ))
    db.commit()
    db.close()


def get_all_rows(table):
    db = None
    cursor = None

    if "sites" in table:
        db = sqlite3.connect("data/sites.sqlite")
        cursor = db.cursor()
        cursor.execute('''
                SELECT link, title, description, heading, paragraph, answer_time, times_found, language, date FROM sites
        ''')
    elif "crawl" in table:
        db = sqlite3.connect("data/crawl.sqlite")
        cursor = db.cursor()
        cursor.execute('''
                SELECT link FROM crawl
        ''')
    all_rows = cursor.fetchall()
    db.commit()
    db.close()
    return all_rows


def remove_duplicates():
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            DELETE FROM sites WHERE rowid NOT IN (SELECT min(rowid) FROM sites
            GROUP BY link);
    ''')
    db.commit()
    db.close()

    db = sqlite3.connect("data/crawl.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            DELETE FROM crawl WHERE rowid NOT IN (SELECT min(rowid) FROM crawl
            GROUP BY link);
    ''')
    db.commit()
    db.close()


def delete_from_crawl(link):
    db = sqlite3.connect("data/crawl.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            DELETE FROM crawl WHERE link = ?
    ''', (link, ))
    db.commit()
    db.close()


def delete_from_sites(link):
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            DELETE FROM sites WHERE link = ?
    ''', (link, ))
    db.commit()
    db.close()


class Site():

    link = ""
    title = ""
    description = ""
    heading = ""
    paragraph = ""
    answer_time = ""
    times_found = ""
    language = ""
    date = ""

    def __init__(self, link, title, description, heading, paragraph, answer_time, times_found, language, date):
        self.link = link
        self.title = title
        self.description = description
        self.heading = heading
        self.paragraph = paragraph
        self.answer_time = str(answer_time)
        self.times_found = str(times_found)
        self.language = language
        self.date = str(date)
