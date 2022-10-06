# This script should be running constantly (from the systemd service or from a while loop in a bash script from crontab)

from asyncio import futures
import signal

from core import log2file, prepare_config, prepare_language, send_to_admin, get_week, check_subscriber, add_subscriber, remove_subscriber, get_logs_files, build_pairs, pretty_pairs, pretty_hours, get_next_pair, pretty_next_pair, get_prev_pair, pretty_prev_pair, get_now_pair, pretty_now_pair


import html
import datetime as dt
import traceback

from os import path as os_path, kill as os_kill, getpid as os_getpid
from sys import exit as sys_exit
from threading import Thread
from json import dumps
from time import sleep
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext


def suicide():
    sleep(0.1)  # need to get reboot message
    log2file("Stopping dispatcher script")
    updater.stop()
    updater.is_idle = False


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        i18n["system_messages"]["start"])


def subscribe(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if check_subscriber(chat_id):
        update.message.reply_text(
            i18n["system_messages"]["already_subscribed"])
    else:
        add_subscriber(chat_id)
        update.message.reply_text(i18n["system_messages"]["subscribed"])


def unsubscribe(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if check_subscriber(chat_id):
        remove_subscriber(chat_id)
        update.message.reply_text(i18n["system_messages"]["unsubscribed"])
    else:
        update.message.reply_text(
            i18n["system_messages"]["not_subscribed"])


def hours(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(pretty_hours(), parse_mode=ParseMode.HTML)
    pass


def error_handler(update: object, context: CallbackContext) -> None:
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'<pre>update = {html.escape(dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
        f''
        f'/reload_bot /send_logs'
    )
    context.bot.send_message(
        chat_id=config["admin_id"], text=message, parse_mode=ParseMode.HTML)


def reload_bot(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id == int(config["admin_id"]):
        log2file("Reloading bot")
        update.message.reply_text(i18n["system_messages"]["reloading"])
        Thread(target=suicide).start()
    else:
        update.message.reply_text(i18n["system_messages"]["not_admin"])


def week(update: Update, context: CallbackContext) -> None:
    week = get_week()
    day_of_week = dt.datetime.today().weekday()
    if week == 1:
        week_key = "week_first"
    else:
        week_key = "week_second"
    message = i18n["week"]["messages"]["week_anwer"].format(
        week=i18n["week"]["messages"][week_key], day_of_week=i18n["week"]["days_full"][day_of_week].lower())
    update.message.reply_text(message)


def send_logs(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id == int(config["admin_id"]):
        logs = get_logs_files()
        if not logs:
            update.message.reply_text(i18n["system_messages"]["no_logs"])
        else:
            for log in logs:
                update.message.reply_document(document=open(log, "rb"))
    else:
        update.message.reply_text(i18n["system_messages"]["not_admin"])


def support(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(i18n["system_messages"]["support"].format(
        support=config["support"]))


def today_pairs(update: Update, context: CallbackContext) -> None:
    message = pretty_pairs(build_pairs())
    update.message.reply_text(
        message.format(
            date=i18n["schedule"]["days"]["today"]), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def tomorrow_pairs(update: Update, context: CallbackContext) -> None:
    message = pretty_pairs(build_pairs(
        day=dt.date.today() + dt.timedelta(days=1)))
    update.message.reply_text(
        message.format(
            date=i18n["schedule"]["days"]["tomorrow"]), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def yesterday_pairs(update: Update, context: CallbackContext) -> None:
    message = pretty_pairs(build_pairs(
        day=dt.date.today() - dt.timedelta(days=1)))
    update.message.reply_text(
        message.format(
            date=i18n["schedule"]["days"]["yesterday"]), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def full_schedule(update: Update, context: CallbackContext) -> None:
    path = "images/schedule.jpg"
    path = os_path.join(os_path.dirname(__file__), path)
    print(path)
    if os_path.exists(path):
        update.message.reply_photo(photo=open(path, "rb"))
    else:
        log2file("Schedule file not found", "error")
        update.message.reply_text(i18n["system_messages"]["no_schedule"])


def get_next_monday_schedule(update: Update, context: CallbackContext) -> None:
    get_next_day_schedule(update, context, 0)


def get_next_tuesday_schedule(update: Update, context: CallbackContext) -> None:
    get_next_day_schedule(update, context, 1)


def get_next_wednesday_schedule(update: Update, context: CallbackContext) -> None:
    get_next_day_schedule(update, context, 2)


def get_next_thursday_schedule(update: Update, context: CallbackContext) -> None:
    get_next_day_schedule(update, context, 3)


def get_next_friday_schedule(update: Update, context: CallbackContext) -> None:
    get_next_day_schedule(update, context, 4)


def get_next_saturday_schedule(update: Update, context: CallbackContext) -> None:
    get_next_day_schedule(update, context, 5)


def get_next_sunday_schedule(update: Update, context: CallbackContext) -> None:
    get_next_day_schedule(update, context, 6)


def get_next_day_schedule(update: Update, context: CallbackContext, day_of_week):
    day = dt.date.today()
    while day.weekday() != day_of_week:
        day += dt.timedelta(days=1)
    message = pretty_pairs(build_pairs(day=day), True)
    update.message.reply_text(
        message.format(
            date=i18n["schedule"]["days"]["next"][day_of_week]), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def schedule_of(update: Update, context: CallbackContext) -> None:
    if context.args:
        try:
            date = dt.datetime.strptime(context.args[0], "%d.%m.%Y").date()
            message = pretty_pairs(build_pairs(
                date), False, get_week(date))
            update.message.reply_text(
                message.format(
                    date=date.strftime("%d.%m.%Y")), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except ValueError:
            update.message.reply_text(
                i18n["system_messages"]["wrong_date_format"])
    else:
        update.message.reply_text(i18n["system_messages"]["no_date"])


def next_pair(update: Update, context: CallbackContext) -> None:
    pair, when = get_next_pair()
    update.message.reply_text(
        pretty_next_pair(pair, when), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def prev_pair(update: Update, context: CallbackContext) -> None:
    pair, when = get_prev_pair()
    update.message.reply_text(
        pretty_prev_pair(pair, when), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def now_pair(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        pretty_now_pair(get_now_pair()), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def deadly_signal_handler(signum, frame):
    log2file("Received signal: " + str(signum), "info")
    send_to_admin(i18n["system_messages"]["bot_stopped"])
    os_kill(os_getpid(), signal.SIGKILL)


def help_bot(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(i18n["system_messages"]["help"].format(
        support=config["support"]), parse_mode=ParseMode.HTML, disable_web_page_preview=True)


if __name__ == "__main__":
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, deadly_signal_handler)
    log2file("Starting dispatcher script")
    config = prepare_config("config/settings.json")
    i18n = prepare_language(config["language"])
    send_to_admin(i18n["system_messages"]["restarted"])

    updater = Updater(config["token"])
    dispatcher = updater.dispatcher

    dispatcher.add_error_handler(error_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("reload_bot", reload_bot))
    dispatcher.add_handler(CommandHandler("send_logs", send_logs))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(CommandHandler("week", week))
    dispatcher.add_handler(CommandHandler("today", today_pairs))
    dispatcher.add_handler(CommandHandler("tomorrow", tomorrow_pairs))
    dispatcher.add_handler(CommandHandler("yesterday", yesterday_pairs))
    dispatcher.add_handler(CommandHandler("full", full_schedule))
    dispatcher.add_handler(CommandHandler("monday", get_next_monday_schedule))
    dispatcher.add_handler(CommandHandler(
        "tuesday", get_next_tuesday_schedule))
    dispatcher.add_handler(CommandHandler(
        "wednesday", get_next_wednesday_schedule))
    dispatcher.add_handler(CommandHandler(
        "thursday", get_next_thursday_schedule))
    dispatcher.add_handler(CommandHandler("friday", get_next_friday_schedule))
    dispatcher.add_handler(CommandHandler(
        "saturday", get_next_saturday_schedule))
    dispatcher.add_handler(CommandHandler("sunday", get_next_sunday_schedule))
    dispatcher.add_handler(CommandHandler("schedule_of", schedule_of))
    dispatcher.add_handler(CommandHandler("next", next_pair))
    dispatcher.add_handler(CommandHandler("prev", prev_pair))
    dispatcher.add_handler(CommandHandler("now", now_pair))
    dispatcher.add_handler(CommandHandler("support", support))
    dispatcher.add_handler(CommandHandler("hours", hours))
    dispatcher.add_handler(CommandHandler("help", help_bot))

    updater.start_polling()
    updater.idle()
