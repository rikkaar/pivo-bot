from typing import List

def getSkip(page, range):
    return ((page - 1) * range) if page > 0 else 0
