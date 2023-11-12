import datetime

def getDate(ObjectId: str) -> str:
    first_four_bytes = ObjectId[:8]  # Получение первых 8 символов (4 байта) из строки

    # Преобразование из шестнадцатеричного формата в целое число
    timestamp = int(first_four_bytes, 16)

    # Преобразование из секунд с начала эпохи Unix в объект datetime
    date_time = datetime.datetime.utcfromtimestamp(timestamp)

    # Форматирование даты
    return date_time.strftime("%d.%m.%Y")