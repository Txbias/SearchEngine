import dbmanager as dbm
import operator
import itertools
from webcrawler import get_hostname, get_domain, get_url


def replace_special_characters(text):
    text = text.replace("â\x80\x93", "-")
    text = text.replace("Ã¼", "ü")
    text = text.replace("â\x80\x94", "—")
    text = text.replace("â\x80\x9d", "\"")
    text = text.replace("â\x80\x9c", "\"")
    text = text.replace("Ã¶", "ö")
    text = text.replace("Ã¤", "ä")
    return text


def search(query, results, current_lang):
    rows = dbm.get_all_rows("sites")
    rows_as_lists = list()

    for row in rows:
        rows_as_lists.append(list(row))

    rows_as_lists.sort()
    rows_as_lists = list(rows_as_lists for rows_as_lists, _ in itertools.groupby(rows_as_lists))

    values = list()

    for i in range(len(rows_as_lists)):
        values.append(0)

    index = 0
    for site in rows_as_lists:
        keywords = query.split()
        if not len(keywords) == 1: keywords.append(query)

        if not site[2] is None:
            if len(site[2]) == 0:
                if len(site[4]) >= 120:
                    site[2] = site[4][:120] + "..."
                else:
                    rows_as_lists[index][2] = rows_as_lists[index][4]
        else:
            rows_as_lists[index][2] = rows_as_lists[index][4]

        in_title = False
        in_link = False

        if len(keywords) == 1:
            if keywords[0].lower() == get_hostname(get_domain(site[0])) or keywords[0].lower() == get_url(
                    get_domain(site[0])):
                values[index] += 8
                in_link = True

        for keyword in keywords:
            try:
                if keyword.lower() in site[0].lower():  # link
                    values[index] += 6
                    in_link = True

                if keyword.lower() in site[1].lower():  # title
                    values[index] += 6
                    in_title = True

                if keyword.lower() in site[2].lower():  # description
                    values[index] += 3

                if keyword.lower() in site[3].lower():  # headings
                    values[index] += 2

                if keyword.lower() in site[4].lower():  # paragraphs
                    values[index] += int(site[4].lower().count(keyword.lower()) / 6)

            except AttributeError:
                pass

        if float(site[5]) < 2:  # answer time
            values[index] += 1

        if site[6] == current_lang:  # language
            values[index] += 3

        if site[0].count('/') <= 3:
            if in_title or in_link:
                values[index] += 1
            else:
                values[index] += 2

        if site[0].count('?') <= 1:
            values[index] += 1

        if site[0].count('.') <= 2:
            values[index] += 1

        if int(site[6]) > 0:  # times found
            if in_title or in_link:
                values[index] += int(site[6] / 2)
            else:
                values[index] += int(site[6] / 6)

        if len(site[2]) > 300:
            rows_as_lists[index][2] = site[2][:300]

        if len(site[1]) > 118:
            rows_as_lists[index][1] = site[1][:115] + "..."
            if values[index] > 0:
                values[index] -= 1
        index += 1

    valued_sites = list()

    index = 0
    for site in rows_as_lists:
        valued_sites.append((site, values[index]))
        index += 1

    valued_sites.sort(key=operator.itemgetter(1), reverse=True)

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

        print(returns)

        return returns
