from typing import List


def getSlice(list: List[any], range: int, curr_page):
    start_index = (curr_page - 1) * range
    end_index = start_index + range

    # Получение репортов для текущей страницы
    list[:] = list[start_index:end_index]

    return list

def getSkip(page, range):
    return ( ( page - 1 ) * range ) if page > 0 else 0