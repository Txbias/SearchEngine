import dbmanager as dbm
import operator
import itertools


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
        try:
            if query.lower() in site[0].lower():
                values[index] += 1

            if query.lower() in site[1].lower():
                values[index] += 1

            if query.lower() in site[2].lower():
                values[index] += 1
        except AttributeError:
            pass

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

        print(returns)
        return returns