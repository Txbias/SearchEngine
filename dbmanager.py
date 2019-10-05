import sqlite3


def create_table():
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites(id INTEGER PRIMARY KEY, link TEXT, title TEXT, description TEXT)
    ''')
    db.commit()
    db.close()


def insert_into_sites(site):
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            INSERT INTO sites(link, title, description) VALUES(?, ?, ?)
    ''', (site.link, site.title, site.description))

    db.commit()
    db.close()


def get_all_rows():
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            SELECT link, title, description FROM sites
    ''')
    all_rows = cursor.fetchall()
    db.commit()
    db.close()
    return all_rows


def remove_duplicates():
    db = sqlite3.connect("data/sites.sqlite")
    cursor = db.cursor()
    cursor.execute('''
         DELETE FROM sites WHERE rowid not in
         (
         select  min(rowid)
         from    sites
         group by
                 link
         )
    ''')
    db.commit()
    db.close()


class Site():

    link = ""
    title = ""
    description = ""

    def __init__(self, link, title, description):
        self.link = link
        self.title = title
        self.description = description
