import json
import logging
from random import randrange, sample, shuffle
import aiohttp
from telegram import ReplyKeyboardMarkup, KeyboardButton
from datetime import timedelta
import sqlite3


BOT_TOKEN = '6900636091:AAF6Gdu8YEuGQrUNLjqWQ8S_EvkF-zfFoJM'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
t_i_m_e_r = 60  # таймер на 5 секунд
with open('sities.json') as f2:
    sities = json.load(f2)
all_btn = [KeyboardButton(text=i) for i in sities] # 5 рандомных элеиентов
flag = False
corr_ans = None
country = None


async def work_with_bd(update, context, type):
    con = sqlite3.connect(r"""C:\Users\sstus\PycharmProjects\final_project\site_db\db\blogs.db""")
    cur = con.cursor()
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    username = update.message.chat.username
    query = f'''SELECT * FROM
    users
    WHERE first_name = '{first_name}' AND
    last_name = '{last_name}' AND
    username = '{username}';
    '''
    q = "SELECT MAX(id) FROM users;"
    res1 = cur.execute(q).fetchone()
    result = cur.execute(query).fetchall()
    if not result:
        query = f'''INSERT INTO users
            values ('{res1[0] + 1}', '{first_name}', '{last_name}', '{username}', '0', '0');'''
        result = cur.execute(query).fetchall()
        con.commit()
    if type == 1:
        query = f'''SELECT saw FROM
            users
            WHERE first_name = '{first_name}' AND
            last_name = '{last_name}' AND
            username = '{username}';
            '''
        s = cur.execute(query).fetchone()[0] + 1
        query = f'''UPDATE users
            SET saw = '{s}'
            WHERE first_name = '{first_name}' AND
            last_name = '{last_name}' AND
            username = '{username}';
            '''
        cur.execute(query)
    elif type == 2:
        query = f'''SELECT guessed FROM
                    users
                    WHERE first_name = '{first_name}' AND
                    last_name = '{last_name}' AND
                    username = '{username}';
                    '''
        g = cur.execute(query).fetchone()[0]
        query = f'''UPDATE users
                    SET guessed = '{g + 1}'
                    WHERE first_name = '{first_name}' AND
                    last_name = '{last_name}' AND
                    username = '{username}';
                    '''
        cur.execute(query)
    con.commit()
    con.close()


async def corr_ans_func(update, context):
    global corr_ans
    if corr_ans == update.message.text:
        flag = True
        chat_id = update.message.chat_id
        remove_job_if_exists(str(chat_id), context)
        text = 'Вы выиграли'
        await work_with_bd(update, context, 2)
    else:
        flag = False
        text = f'Вы проиграли, правильным ответом было {corr_ans}'
    await update.message.reply_text(text)
    await start(update, context)


async def help_func(update, context):
    global country
    await update.message.reply_text(
        country,
    )


def random_elem():
    a = sample(all_btn, 5)
    return a


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
    with open('res.json', 'w') as f:
        json.dump(response, f, indent=4)
    toponym = response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    ll, spn = ','.join(toponym['Point']['pos'].split()), get_span(toponym['boundedBy']['Envelope']['lowerCorner'],
                                                                  toponym['boundedBy']['Envelope']['upperCorner'])
    # Можно воспользоваться готовой функцией,
    # которую предлагалось сделать на уроках, посвящённых HTTP-геокодеру.

    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=sat"
    return [static_api_request, sity]


async def guess_the_sity(update, context):
    global flag, country, corr_ans
    flag = False
    sity__photo = await sity_photo()
    print(sity__photo)
    corr_ans = sity__photo[1]
    country = sity__photo[1].split()[1]
    a = [[i] for i in random_elem() + [get_sity(sity__photo[1])]]
    shuffle(a)
    reply_keyboard = [*a, ['/help'], ['/nazad']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await context.bot.send_photo(
        update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API, по сути, ссылка на картинку.
        # Телеграму можно передать прямо её, не скачивая предварительно карту.
        sity__photo[0],
        caption=f'у вас есть 1 минута чтобы угадать город',
    )
    await context.bot.send_message(update.message.chat_id, text='.', reply_markup=markup)

    await set_timer(update, context)
    ans = str(update.message.text).lower()
    if ans == sity__photo[1].lower():
        flag = True


async def show_sity(update, context):
    sity__photo = await sity_photo()
    await context.bot.send_photo(
        update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API, по сути, ссылка на картинку.
        # Телеграму можно передать прямо её, не скачивая предварительно карту.
        sity__photo[0],
        caption=f"Нашёл:{sity__photo[1]}"
    )
    await work_with_bd(update, context, 1)


async def get_response(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def task(update, context):
    global t_i_m_e_r
    """Выводит сообщение"""
    if flag:
        text = 'Вы угадали'
    else:
        text = 'Вы  не угадали'
    await context.bot.send_message(context.job.chat_id, text=text)
    await start(update, context)



async def unset(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Вопрос отменен вы проиграли!' if job_removed else 'У вас нет активных вопросов'
    await update.message.reply_text(text)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    reply_keyboard = [['/show_sity', '/guess_the_sity']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    user = update.effective_user
    await update.message.reply_text(
        "Я геобот. Какая информация вам нужна?",
        reply_markup=markup
    )


async def unset_nazad(update, context):
    await unset(update, context)
    await start(update, context)


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
async def set_timer(update, context):
    global t_i_m_e_r
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = f'{t_i_m_e_r} секунд пошло!'
    await update.effective_message.reply_text(text)
    context.job_queue.run_once(task,
                               when=timedelta(seconds=t_i_m_e_r),
                               chat_id=chat_id,
                               name=str(chat_id),
                               data=t_i_m_e_r)


