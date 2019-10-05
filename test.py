import dbmanager as dbm
import sqlite3

rows = dbm.get_all_rows()

print(len(rows))
duplicates = 0

links = list()

for row in rows:
    links.append(row[0])


length_before = len(links)
links = list(set(links))
lenght_after = len(links)
print(length_before - lenght_after)


print(duplicates)

db = sqlite3.connect("data/sites.sqlite")
cursor = db.cursor()
cursor.execute('''
delete from sites
where rowid not in (select min(rowid)
                    from sites
                    group by link,title,description)

''')
all_rows = cursor.fetchall()
db.commit()
db.close()
