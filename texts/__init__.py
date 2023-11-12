from enum import Enum

class MessageText(Enum):
    notEnougthParams = "Не все параметры переданы в команду\n\n"
    hireValidationError = "Передайте Id пользователя или username через @, затем укажите номер точки, где он работает \nПример: /hire 12345678 1 или /hire @username 1"
    usernameValidationError = "Username должен начинаться с @ \nПример: @username"
    userNotFound = "Пользователь с таким данными не найден"

    subscribtionsBtn = "Мои подписки"
    profileMessage = f'В профиле будет храниться ваш QR-код клиента, а в разделе \"{subscribtionsBtn}\" можно будет посмотреть, на новинки каких адресов вы подписаны'
    createQRBtn = "Создать QR-код"
    noSubs = "В данный момент вы не получаете уведомления о новинках. Вы можете подписаться на новинки в меню любой из наших точек"
    yesSubs = "Вы получете уведомления о новинках по следующим адресам:\n\n"
    createQRhelp = "Напишите номер клиента или отправьте в чат фотографию уже существующего QR-кода"
    createQRcancel = "Вы можете вернуться к созданию QR-кода на странице профиля"
    createQRphotoError = "Не могу распознать QR на фото. Попробуйте другую фотографию"
    stopQRProcess = "Оки, вы всегда сможете вернуться к созданию QR-кода в профиле :)"

    subscribe = "Новинки ❌"
    unsubscribe = "Новинки ✅"

    pickPointMap = "Наши магазины располагаются по следующим адресам:\n"
    pickPointHelp = "\n\nВыберите номер точки, о которой хотели бы узнать больше"
    searchHelp = "Поиск работает по названию и по номеру штрихкода \n\nНапишите название, или штрихкод, или отправьте в чат фотографию, где хорошо виден штрихкод"
    searchCancel = "Вы отменили поиск"
    searchPhotoError = "Не могу распознать штрихкод на фото. Попробуйте другую фотографию или введите штрихкод вручную"

    reportSent = "Ваш репорт отправлен и будет рассмотрен нашим менеджером.\nМы постараемся решить возникшую проблему!"
    reportSentWithFeedback = "Ваш репорт отправлен.\nНаш менеджер свяжется с вами для решения возникшей проблемы!"
    reportMessage = "Расскажите о возникшей проблеме"

    shouldContact = "С вами связаться?"
    shouldContactError = "В этом случае я могу понять либо \"да\", либо \"нет\""
    feedbackAbort = "Отмена"
    textError = "К сожалению, я понимаю только текстовые сообщения :("

    requestSent = "Ваш запрос на поставку отправлен и будет рассмотрен нашим менеджером!\nЧтобы не упустить новинки, Вы можете подписаться на них в меню этой точки"
    requestSentWithFeedback = "Ваш запрос на поставку отправлен!\nНаш менеджер свяжется с вами для уточнения вашего запроса!"
    requestMessage = "Напишите название интересующей вас позиции"
    requestLink = "Отправьте ссылку интересующей вас позиции с сайта <a href='https://untappd.com'>Untappd</a>"
    requestLinkError = "Это не похоже на ссылку. Давайте еще раз"

    noRepotsFound = "По вашим фильтрам не найдено репортов"
    reportNavHelp = "Использйте стрелки для перехода между страницами и кнопки для того, чтобы изменить статус репорта"
    navFirst = "Вы на первой странице"
    navLast = "Это последняя страница. Дальше некуда"