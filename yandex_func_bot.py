import logging
import datetime
from telegram import ReplyKeyboardMarkup
from random import randrange
from datetime import timedelta


BOT_TOKEN = '6900636091:AAF6Gdu8YEuGQrUNLjqWQ8S_EvkF-zfFoJM'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
t_i_m_e_r = 5  # таймер на 5 секунд


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
    reply_keyboard = [['/dice', '/timer']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    user = update.effective_user
    await update.message.reply_text(
        "Я бот. Какая информация вам нужна?",
        reply_markup=markup
    )


async def dice(update, context): # это будет кубик, но с городами
    reply_keyboard = [['/grahey_6_1_sht'], ['/grahey_6_2_sht'], ['/grahey_20_1_sht'], ['/nazad']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text(
        "Какой кубик вам нужен?",
        reply_markup=markup
    )


async def timer_30s(update, context):
    await set_timer(update, context, check_chat=False, t_i_m_e_r_=30)


async def timer_1m(update, context):
    await set_timer(update, context, check_chat=False, t_i_m_e_r_=60)


async def timer_5m(update, context):
    await set_timer(update, context, check_chat=False, t_i_m_e_r_=300)


async def grahey_6_1_sht(update, context):
    await update.message.reply_text('Ребро вашего кубика: ' + str(randrange(1, 6)))


async def grahey_6_2_sht(update, context):
    await update.message.reply_text('Ребро вашего кубика: ' + str(randrange(1, 6)))
    await update.message.reply_text('Ребро вашего кубика: ' + str(randrange(1, 6)))


async def grahey_20_1_sht(update, context):
    await update.message.reply_text('Ребро вашего кубика: ' + str(randrange(1, 20)))


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.")


async def echo(update, context):
    await update.message.reply_text('Я получил сообщение ' + update.message.text)


async def help(update, context):
    await update.message.reply_text(
        "Я бот справочник.")


async def address(update, context):
    await update.message.reply_text(
        "Адрес: г. Москва, ул. Льва Толстого, 16")


async def phone(update, context):
    await update.message.reply_text("Телефон: +7(495)776-3030")


async def site(update, context):
    await update.message.reply_text(
        "Сайт: http://www.yandex.ru/company")


async def work_time(update, context):
    await update.message.reply_text(
        "Время работы: круглосуточно.")


async def time(update, context):
    await update.message.reply_text(
        f"time:{datetime.datetime.now().time()}")


async def date(update, context):
    await update.message.reply_text(
        f"date:{datetime.datetime.now().date()}")
