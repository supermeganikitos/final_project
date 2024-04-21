import logging
import time
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, ConversationHandler, ContextTypes
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from config import TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def main():
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop), CommandHandler('skip', skip)]
    )

    application.add_handler(conv_handler)
    application.run_polling()
    application.start()


async def start(update, context):
    await update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "В каком городе вы живёте?")

    # Число-ключ в словаре states —
    # втором параметре ConversationHandler'а.
    return 1
    # Оно указывает, что дальше на сообщения от этого пользователя
    # должен отвечать обработчик states[1].
    # До этого момента обработчиков текстовых сообщений
    # для этого пользователя не существовало,
    # поэтому текстовые сообщения игнорировались.


# Добавили словарь user_data в параметры.
async def first_3response(update, context):
    # Сохраняем ответ в словаре.
    context.user_data['locality'] = update.message.text
    await update.message.reply_text(
        f"Какая погода в городе {context.user_data['locality']}?")
    return 2


# Добавили словарь user_data в параметры.
async def second_response(update, context):
    weather = update.message.text
    logger.info(weather)
    # Используем user_data в ответе.
    await update.message.reply_text(
        f"Спасибо за участие в опросе!")
    context.user_data.clear()  # очищаем словарь с пользовательскими данными
    return ConversationHandler.END


async def skip(update, context):
    weather = update.message.text
    logger.info(weather)
    # Используем user_data в ответе.
    await update.message.reply_text(
        f"Какая погода у вас за окном?")
    return 2


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


if __name__ == '__main__':
    main()