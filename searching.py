import dbmanager as dbm
import operator
import itertools


def replace_special_characters(text):

    text = text.replace("â\x80\x93", "-")
    text = text.replace("Ã¼", "ü")
    return text


def search(query, results):
    rows = dbm.get_all_rows()
    rows_as_lists = list()

    for row in rows:
    	rows_as_lists.append(list(row))

    rows_as_lists.sort()
    rows_as_lists = list(rows_as_lists for rows_as_lists,_ in itertools.groupby(rows_as_lists))

    values = list()

    for i in range(len(rows_as_lists)):
    	values.append(0)

    index = 0
    for site in rows_as_lists:
        keywords = query.split()
        if not len(keywords) == 1: keywords.append(query)

        for keyword in keywords:
            try:
                if keyword.lower() in site[0].lower(): # link
                    values[index] += 4

                if keyword.lower() in site[1].lower(): # title
                    values[index] += 3

                if keyword.lower() in site[2].lower(): # description
                    values[index] += 2

                if keyword.lower() in site[3].lower(): # headings
                    values[index] += 1

                if keyword.lower() in site[4].lower(): # paragraphs
                    values[index] += int(site[4].lower().count(keyword.lower()) / 2)


            except AttributeError:
                pass


        if site[0].count('/') <= 2:
            values[index] += 2

        if site[0].count('?') <= 1:
            values[index] += 1

        if site[0].count('.') <= 2:
            values[index] += 1

        index += 1



    valued_sites = list()

    index = 0
    for site in rows_as_lists:
    	valued_sites.append((site, values[index]))
    	index += 1


    valued_sites.sort(key = operator.itemgetter(1), reverse = True)

    if len(valued_sites) == 0:
        return []
    elif valued_sites[0][1] == 0:
        return []
    else:

        returns = list()
        for i in range(results):
            returns.append(valued_sites[i][0])


        big_index = 0
        for r in returns:
            small_index = 0
            for part in r:
                returns[big_index][small_index] = replace_special_characters(str(part))
                small_index += 1

            big_index += 1

        return returns
