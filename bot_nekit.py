from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler
from yandex_func_bot import *
from project_func_bot import *


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    for i in all_btn:
        application.add_handler(CommandHandler("i", show_sity))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("show_sity", show_sity))
    application.add_handler(CommandHandler("help", help_func))
    application.add_handler(CommandHandler("guess_the_sity", guess_the_sity))
    application.add_handler(CommandHandler("nazad", unset_nazad))
    application.run_polling()


if __name__ == '__main__':
    main()