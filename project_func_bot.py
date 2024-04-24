import json
import logging
from random import randrange
import aiohttp
from telegram import ReplyKeyboardMarkup, KeyboardButton
from datetime import timedelta


BOT_TOKEN = '6900636091:AAF6Gdu8YEuGQrUNLjqWQ8S_EvkF-zfFoJM'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
t_i_m_e_r = 5  # таймер на 5 секунд
with open('sities.json') as f2:
    sities = json.load(f2)
all_btn = [KeyboardButton(text=i) for i in sities] # 5 рандомных элеиентов


def get_random_sity():
    with open('sities.json') as f2:
        sities = json.load(f2)
    return sities[randrange(0, len(sities) - 1)]


def get_sity(i):
    return list(filter(lambda x: x.text == i, all_btn))[0]


def get_span(coords_1, coords_2):
    l, b = coords_1.split(" ")
    r, t = coords_2.split(" ")
    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) * 1.1
    dy = abs(float(t) - float(b)) * 1.1
    # Собираем размеры в параметр span
    span = f"{dx},{dy}"
    return span


async def sity_photo():
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    sity = get_random_sity()
    response = await get_response(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "lang": 'ru_RU',
        "geocode": sity.split()[0]
    })
    response = response.json()
    with open('res.json', 'w') as f:
        json.dump(response, f, indent=4)
    toponym = response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    ll, spn = ','.join(toponym['Point']['pos'].split()), get_span(toponym['boundedBy']['Envelope']['lowerCorner'],
                                                                  toponym['boundedBy']['Envelope']['upperCorner'])
    # Можно воспользоваться готовой функцией,
    # которую предлагалось сделать на уроках, посвящённых HTTP-геокодеру.

    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    return static_api_request, sity


async def guess_the_sity(update, context):
    sity__photo = sity_photo()
    reply_keyboard = [*[[]]['/help'], ['/i_dont_know'], ['/timer_5m'], ['/nazad']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await context.bot.send_photo(
        update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API, по сути, ссылка на картинку.
        # Телеграму можно передать прямо её, не скачивая предварительно карту.
        sity__photo[0],
        caption=f'у вас есть 1 минуты чтобы угадать город'
    )


async def show_sity(update, context):
    sity__photo = sity_photo()
    await context.bot.send_photo(
        update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API, по сути, ссылка на картинку.
        # Телеграму можно передать прямо её, не скачивая предварительно карту.
        sity__photo[0],
        caption=f"Нашёл:{sity__photo[1]}"
    )


async def get_response(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def timer_lobby(update, context):
    reply_keyboard = [['/timer_30s'], ['/timer_1m'], ['/timer_5m'], ['/nazad']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text(
        "Какой таймер вам нужен?",
        reply_markup=markup
    )


async def task(context):
    global t_i_m_e_r
    """Выводит сообщение"""
    await context.bot.send_message(context.job.chat_id, text=f'КУКУ! {t_i_m_e_r}c. прошли!')


async def unset(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)

    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# Обычный обработчик, как и те, которыми мы пользовались раньше.
async def set_timer(update, context, check_chat=True, t_i_m_e_r_=t_i_m_e_r):

    global t_i_m_e_r
    t_i_m_e_r = t_i_m_e_r_
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    job_removed = remove_job_if_exists(str(chat_id), context)
    if check_chat:
        locality = str(update.message.text).strip().split()[-1]
        if locality.isdigit():
            t_i_m_e_r_ = int(locality)
    text = f'Вернусь через {t_i_m_e_r_} с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)
    context.job_queue.run_once(task,
                               when=timedelta(seconds=t_i_m_e_r_),
                               chat_id=chat_id,
                               name=str(chat_id),
                               data=t_i_m_e_r_)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    reply_keyboard = [['/show_sity', '/guess_the_city']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    user = update.effective_user
    await update.message.reply_text(
        "Я бот. Какая информация вам нужна?",
        reply_markup=markup
    )