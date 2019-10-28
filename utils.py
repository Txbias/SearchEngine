import dbmanager as dbm


def remove_incorrectly_crawled_sites():
    from webcrawler import get_domain, get_url
    rows = dbm.get_all_rows("sites")
    rows_as_lists = list()

    for row in rows:
        rows_as_lists.append(list(row))

    index = 0
    errors = ["403 Forbidden", "Yahoo - 404 Not Found", "404 Not found", None, "Page Not Found | Reuters.com", "We're sorry, but that page cannot be found - POLITICO",
              "404 - File or directory not found.", "Bitly | Page Not Found | 404", "The page you were looking for doesn't exist – Trustpilot Support Center", "Error 404",
              "Error 404 (Not Found)!!1", "502 Proxy Error", "Page not found - Stack Overflow", "Access Denied"]
    languages = ["de", "en", "de-de", "en-us", "it", "fr"]

    for row in rows_as_lists:
        if row[1] in errors:
            rows_as_lists.remove(row)
            dbm.delete_from_sites(row[0])
            index += 1
            continue
        for row2 in rows_as_lists:
            if row[1] == row2[1] and rows_as_lists.index(row) != rows_as_lists.index(row2) and row[1].lower() != "wikipedia" and row[1].lower() != "youtube":
                if get_url(get_domain(row[0])) == get_url(get_domain(row2[0])) and not any(l in row[0] for l in languages) and not any(l in row2[0] for l in languages):
                    rows_as_lists.remove(row)
                    dbm.delete_from_sites(row[0])
                    print("deleted: " + str(row[1]))
                    index += 1
                    break


    print("Deleted %s duplicates!"  %(str(index)))
