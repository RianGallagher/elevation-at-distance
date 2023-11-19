# A binary search to find the entry that has the distance closest to the distance entered.
def find_closest_entry(list: list[dict[str, float]], search_item: float):
    found = False
    search_list = list

    while found is False:
        middle = round(len(search_list) / 2)
        if (search_list[middle] == search_item or len(search_list) == 1):
            found = True
            break

        if (len(search_list) == 2):
            if (abs(search_list[0]["distance"] - search_item) < abs(search_list[1]["distance"] - search_item)):
                search_list = search_list[:1]
            else:
                search_list = search_list[1:]
            break

        if (search_list[middle]["distance"] > search_item):
            search_list = search_list[:middle]
        else:
            search_list = search_list[middle:]

    return search_list[0]
