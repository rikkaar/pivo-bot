from enum import Enum
from database.services.addresses import AddressesService
from database.services.reports import ReportService

class FilterState(int, Enum):
    false = 0
    all = 1
    true = 2

async def getFiltersText(contact: FilterState, fulfilled: FilterState, point: str) -> str:
    emoji_true = "✅"
    emoji_false = "❌"
    emoji_all = "🌐"
    emoji_location = "📍"

    if contact == FilterState.all:
        contactText = f"{emoji_all} Вне зависимости от формы связи"
    elif contact == FilterState.false:
        contactText = f"{emoji_false} Без обратной связи"
    else:
        contactText = f"{emoji_true} С обратной связью"

    if fulfilled == FilterState.all:
        fulfilledText = f"{emoji_all} Вне зависимости от статуса исполнения"
    elif fulfilled == FilterState.false:
        fulfilledText = f"{emoji_false} Необработанные заявки"
    else:
        fulfilledText = f"{emoji_true} Исполненные заявки"

    if point:
        pointText = await AddressesService.get_address(point)
        pointText = f"{emoji_location} {pointText.shortAddress}"
    else:
        pointText = f"{emoji_all} Заявки со всех адресов"

    filterText = f"Текущие настройки фильтрации:\n\nАдрес: {pointText}\nТип заяки: {contactText}\nСтатус заявки: {fulfilledText}"
    
    return filterText

def filterChange(curr: FilterState) ->FilterState:
    if curr == FilterState.all:
        return FilterState.true
    elif curr == FilterState.true:
        return FilterState.false
    else:
        return FilterState.all