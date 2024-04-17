import logging
import time
import random
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, ConversationHandler, ContextTypes
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from config import T_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

start_keyboard = [['/dice', '/timer']]
markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=False)
first_keyboard = [['/one_hexagonal', '/two_hexagonal'], ['/twenty_sided', '/exit']]
markup1 = ReplyKeyboardMarkup(first_keyboard, one_time_keyboard=False)
second_keyboard = [['/thirty_sec', '/one_min'], ['/five_min', '/exit']]
markup2 = ReplyKeyboardMarkup(second_keyboard, one_time_keyboard=False)
close_keyboard = [['/close']]
markup_close = ReplyKeyboardMarkup(close_keyboard, one_time_keyboard=False)


def main():
    application = Application.builder().token(T_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("timer", timer))
    application.add_handler(CommandHandler("thirty_sec", thirty_sec))
    application.add_handler(CommandHandler("one_min", one_min))
    application.add_handler(CommandHandler("five_min", five_min))
    application.add_handler(CommandHandler("close", close))
    application.add_handler(CommandHandler("dice", dice))
    application.add_handler(CommandHandler("one_hexagonal", one_hexagonal))
    application.add_handler(CommandHandler("two_hexagonal", two_hexagonal))
    application.add_handler(CommandHandler("twenty_sided", twenty_sided))
    application.add_handler(CommandHandler("exit", exit))

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # Регистрируем обработчик в приложении.
    application.add_handler(text_handler)

    # Запускаем приложение.
    application.run_polling()
    application.start()


async def echo(update, context):
    user = update.effective_user
    if user.first_name == '':
        await update.message.reply_text()
    else:
        await update.message.reply_text(f'{update.message.text}')


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}!",
        reply_markup=markup
    )


async def dice(update, context):
    await update.message.reply_html(
        rf"Какой кубик хотите?",
        reply_markup=markup1)


async def one_hexagonal(update, context):
    await update.message.reply_html(
        rf"Итак, вам выпало: {random.randint(1, 6)}"
    )


async def two_hexagonal(update, context):
    await update.message.reply_html(
        rf"Итак, вам выпало: {random.randint(1, 6)}, {random.randint(1, 6)}"
    )


async def twenty_sided(update, context):
    await update.message.reply_html(
        rf"Итак, вам выпало: {random.randint(1, 20)}"
    )


async def exit(update, context):
    await update.message.reply_html(
        rf"Хорошо, вернемся назад",
        reply_markup=markup)


async def timer(update, context):
    await update.message.reply_html(
        rf"На какое время ставим таймер?",
        reply_markup=markup2)


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def task(context):
    await context.bot.send_message(context.job.chat_id, text=f'время истекло')


async def thirty_sec(update, context):
    chat_id = update.effective_message.chat_id
    TIMER = int(30)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
    text = f'засек 30 секунд!'
    await update.message.reply_html(text, reply_markup=markup_close)


async def one_min(update, context):
    chat_id = update.effective_message.chat_id
    TIMER = int(60)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
    text = f'засек 1 минуту!'
    await update.message.reply_html(text, reply_markup=markup_close)


async def five_min(update, context):
    chat_id = update.effective_message.chat_id
    TIMER = int(300)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
    text = f'засек 5 минут!'
    await update.message.reply_html(text, reply_markup=markup_close)


async def close(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_html(text, reply_markup=markup2)


if __name__ == '__main__':
    main()
