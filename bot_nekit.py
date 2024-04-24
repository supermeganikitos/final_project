

from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler
from yandex_func_bot import *
from project_func_bot import *


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    for i in all_btn:
        application.add_handler(CommandHandler("i", show_sity))
    application.add_handler(CommandHandler("show_sity", show_sity))
    text_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()