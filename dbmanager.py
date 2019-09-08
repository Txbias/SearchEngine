import sqlite3



def insert_into_links(link):
    db = sqlite3.connect("data/links.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            INSERT INTO links(link) VALUES(?)
    ''', (link,))

    db.commit()
    db.close()


def get_all_rows():
    db = sqlite3.connect("data/links.sqlite")
    cursor = db.cursor()
    cursor.execute('''
            SELECT link FROM links
    ''')
    all_rows = cursor.fetchall()
    db.commit()
    db.close()
    return all_rows


def remove_duplicates():
    db = sqlite3.connect("data/links.sqlite")
    cursor = db.cursor()
    cursor.execute('''
         DELETE FROM links WHERE rowid not in
         (
         select  min(rowid)
         from    links
         group by
                 link
         )   
    ''')
    db.commit()
    db.close()