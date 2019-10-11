import sqlite3


def create_tables():
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites(link TEXT, title TEXT, description TEXT, heading TEXT,
            paragraph TEXT, answer_time TEXT, times_found TEXT, language TEXT)
    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl(link TEXT)
    ''')
    db.commit()
    db.close()


def insert_into_sites(site):
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            INSERT INTO sites(link, title, description, heading, paragraph, answer_time, times_found, language) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    ''', (site.link, site.title, site.description, site.heading, site.paragraph, site.answer_time, site.times_found, site.language))

    db.commit()
    db.close


def insert_into_crawl(link):
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            INSERT INTO crawl(link) VALUES(?)
    ''', (link, ))
    db.commit()
    db.close()


def get_all_rows(table):
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()

    if "sites" in table:
        cursor.execute('''
                SELECT link, title, description, heading, paragraph, answer_time, times_found, language FROM sites
        ''')
    elif "crawl" in table:
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
    cursor.execute('''
            DELETE FROM crawl WHERE rowid NOT IN (SELECT min(rowid) FROM crawl
            GROUP BY link);
    ''')
    db.commit()
    db.close()


def delete_from_crawl(link):
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            DELETE FROM crawl WHERE link = ?
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

    def __init__(self, link, title, description, heading, paragraph, answer_time, times_found, language):
        self.link = link
        self.title = title
        self.description = description
        self.heading = heading
        self.paragraph = paragraph
        self.answer_time = str(answer_time)
        self.times_found = str(times_found)
        self.language = language
