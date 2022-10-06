# This file contain core functions of the program

from datetime import date, datetime as dt, timedelta as td
from json import loads, dumps
import requests
from os import path as os_path, listdir as os_listdir

if __name__ == "__main__":
    print("This file is not supposed to be run directly")

conf = {}
i18n = {}


def open_json(path):
    path = os_path.join(os_path.dirname(__file__), path)
    try:
        with open(path, "r") as file:
            return loads(file.read())
    except FileNotFoundError:
        print(f"File {path} not found")
        log2file(f"File {path} not found", "error")
        exit(1)
    except Exception as e:
        print(f"Error while reading {path}: {e}")
        log2file(f"Error while reading {path}: {e}", "error")
        exit(1)


schedule = open_json("config/schedule.json")


def merge_dicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(merge_dicts(dict1[k], dict2[k])))
            else:
                yield (k, dict2[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def log2file(message, type="info"):
    logs_dir = os_path.join(os_path.dirname(__file__), "logs")
    if not os_path.exists(logs_dir):
        os_path.mkdir(logs_dir)
        if not os_path.exists(logs_dir):
            print("Error while creating logs directory")
            exit(1)
    log_file = os_path.join(logs_dir, type + ".log")
    with open(log_file, "a") as file:
        message = f"{dt.now()} {message}\n"
        file.write(message)


def get_week(day=date.today()):
    dateX = day - date(2022, 8, 29)
    weeksElapsed = dateX.days // 7
    if weeksElapsed % 2 == 0:
        return 1
    else:
        return 2


def prepare_config(path):
    config = open_json(path)
    if not config["language"]:
        config["language"] = "ua"
    if not config["token"]:
        print("Telegram token is not set")
        log2file("Telegram token is not set", "error")
        exit(1)
    if not config["group_id"]:
        print("Telegram group id is not set")
        log2file("Telegram group id is not set", "error")
        exit(1)
    if not config["admin_id"]:
        print("Telegram admin id is not set")
        log2file("Telegram admin id is not set", "error")
        exit(1)
    if not config["subscribers"]:
        config["subscribers"] = []
    if not config["support"]:
        print("Telegram support is not set")
        log2file("Telegram support id is not set", "error")
        exit(1)
    global conf
    conf = config
    save_config()
    return config


def prepare_language(language):
    fallback_language = "ua"
    if not os_path.exists(os_path.join(os_path.dirname(__file__), f"lang/{language}.json")):
        print(
            f"Language file for {language} not found, using {fallback_language}")
        language = fallback_language
    fallback_dict = open_json(f"lang/{fallback_language}.json")
    global i18n
    if language == fallback_language:
        i18n = fallback_dict
        return fallback_dict
    else:
        language_dict = open_json(f"lang/{language}.json")
        language_dicts = dict(merge_dicts(fallback_dict, language_dict))
        i18n = language_dicts
        return language_dicts


def send_telegram_message(message, chat_id, parse_mode="plain"):
    token = conf["token"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    if parse_mode == "html":
        data["parse_mode"] = "HTML"
        data["disable_web_page_preview"] = True
    requests.post(url, data=data)


def send_to_admin(message):
    send_telegram_message(message, conf["admin_id"])


def send_to_subscribers(message, parse_mode="html"):
    send_telegram_message(message, conf["group_id"], parse_mode)
    for subscriber in conf["subscribers"]:
        send_telegram_message(message, subscriber, parse_mode)


def save_config():
    path = os_path.join(os_path.dirname(__file__), "config/settings.json")
    try:
        with open(path, "w") as file:
            file.write(dumps(conf))
    except FileNotFoundError:
        print(f"File {path} not found")
        log2file(f"File {path} not found", "error")
        exit(1)
    except Exception as e:
        print(f"Error while writing {path}: {e}")
        log2file(f"Error while writing {path}: {e}", "error")
        exit(1)


def add_subscriber(chat_id):
    conf["subscribers"].append(chat_id)
    save_config()


def remove_subscriber(chat_id):
    conf["subscribers"].remove(chat_id)
    save_config()


def check_subscriber(chat_id):
    return chat_id in conf["subscribers"]


def get_logs_files():
    logs_dir = os_path.join(os_path.dirname(__file__), "logs")
    names = os_listdir(logs_dir)
    names.remove(".gitkeep")
    if not names:
        return []
    else:
        return [os_path.join(logs_dir, name) for name in names]


def build_pairs(day=date.today()):
    week = get_week(day)
    ret = []
    try:
        pairs = schedule["weeks"][str(week)]["days"][str(
            day.weekday() + 1)]["pairs"]
    except KeyError:
        return []
    for pair in pairs:
        p = pairs[pair].copy()
        p["number"] = pair
        p["start"] = schedule["pairs"][pair]["start"]
        p["end"] = schedule["pairs"][pair]["end"]
        if (schedule["teachers"][str(p["teacher"])]):
            p["teacher"] = schedule["teachers"][str(p["teacher"])]
        if (schedule["subjects"][str(p["subject"])]):
            p["subject"] = schedule["subjects"][str(p["subject"])]
        ret.append(p)
    return ret


def pretty_pairs(pairs, its_day_of_week=False, need_print_week=False):
    pretty = ''
    if not pairs:
        if its_day_of_week:
            pretty += f'<b>{i18n["schedule"]["empty_variant"]}</b>\n'
        else:
            pretty += f'<b>{i18n["schedule"]["empty"]}</b>\n'
        if need_print_week:
            pretty += f'<b>{i18n["schedule"]["week"]} {need_print_week}</b>\n'
        pretty += '\n'
    else:
        if its_day_of_week:
            pretty += f'<b>{i18n["schedule"]["header_variant"]}</b>\n'
        else:
            pretty += f'<b>{i18n["schedule"]["header"]}</b>\n'
        if need_print_week:
            pretty += f'<i>{i18n["schedule"]["week"]} {need_print_week}</i>\n'
        pretty += '\n'
        for pair in pairs:
            pretty += f'<b>{pair["start"]} - {pair["end"]}</b>  <i>{i18n["schedule"]["pairs_type"][pair["type"]]}</i>\n'
            pretty += f'<pre>{pair["subject"]["name"]}</pre>\n'
            pretty += f'<b>{i18n["schedule"]["room"]}</b> {pair["room"]}\n'
            if pair["teacher"]:
                pretty += f'<b>{i18n["schedule"]["teacher"]}</b> <i>{i18n["schedule"]["teacher_degrees"][pair["teacher"]["degree"]]}</i> {pair["teacher"]["name"]}\n'
            if pair["class_link"]:
                pretty += f'[<a href="{pair["class_link"]}">{i18n["schedule"]["class_link"]}</a>] '
            if pair["meet_link"]:
                pretty += f'[<a href="{pair["meet_link"]}">{i18n["schedule"]["meet_link"]}</a>]'
            if (not (pair["class_link"] or pair["meet_link"])):
                pretty = pretty[:-1]
            pretty += "\n\n"
        pretty = pretty[:-1]
    return pretty


def pretty_hours():
    pretty = f'<b>{i18n["schedule"]["hours"]}</b>\n'
    pretty += f'<i>{i18n["schedule"]["hours_sub"]}</i>\n\n'
    for pair in schedule["pairs"]:
        pretty += f'<b>{pair}.</b>  {schedule["pairs"][pair]["start"]} - {schedule["pairs"][pair]["end"]}\n'
    return pretty


def get_next_pair():
    day_offset = 0
    day_find_count = 7
    while day_find_count:
        day = date.today() + td(days=day_offset)
        pairs = build_pairs(day)
        if pairs:
            for pair in pairs:
                h1 = int(pair["start"].split(":")[0])
                m1 = int(pair["start"].split(":")[1])
                if (day_find_count == 7):
                    t = dt.now().time()
                    h2 = t.hour
                    m2 = t.minute
                else:
                    h2 = 0
                    m2 = 0
                M1 = h1*60 + m1
                M2 = h2*60 + m2
                if M1 > M2:
                    return pair, day
        day_offset += 1
        day_find_count -= 1
    return None, None


def get_prev_pair():
    day_offset = 0
    day_find_count = 7
    while day_find_count:
        day = date.today() - td(days=day_offset)
        pairs = build_pairs(day)
        if pairs:
            for pair in pairs[::-1]:
                h1 = int(pair["end"].split(":")[0])
                m1 = int(pair["end"].split(":")[1])
                if (day_find_count == 7):
                    t = dt.now().time()
                    h2 = t.hour
                    m2 = t.minute
                else:
                    h2 = 23
                    m2 = 59
                M1 = h1*60 + m1
                M2 = h2*60 + m2
                if M1 < M2:
                    return pair, day
        day_offset += 1
        day_find_count -= 1
    return None, None


def pretty_next_pair(pair, when, need_when=True):
    if (not pair or not when):
        return f'<b>{i18n["schedule"]["empty_next"]}</b>'
    pretty = f'<b>{pair["start"]} - {pair["end"]}</b>  <i>{i18n["schedule"]["pairs_type"][pair["type"]]}</i>\n'
    pretty += f'<pre>{pair["subject"]["name"]}</pre>\n'
    pretty += f'<b>{i18n["schedule"]["room"]}</b> {pair["room"]}\n'
    if pair["teacher"]:
        pretty += f'<b>{i18n["schedule"]["teacher"]}</b> <i>{i18n["schedule"]["teacher_degrees"][pair["teacher"]["degree"]]}</i> {pair["teacher"]["name"]}\n'
    if pair["class_link"]:
        pretty += f'[<a href="{pair["class_link"]}">{i18n["schedule"]["class_link"]}</a>] '
    if pair["meet_link"]:
        pretty += f'[<a href="{pair["meet_link"]}">{i18n["schedule"]["meet_link"]}</a>]'
    if (not (pair["class_link"] or pair["meet_link"])):
        pretty = pretty[:-1]
    if (need_when):
        pretty += f'\n\n<b>{i18n["schedule"]["when"]}</b> {when.strftime("%d.%m.%Y")}'
        if when == date.today():
            pretty += f' ({i18n["schedule"]["days"]["today"]})'
        elif when == date.today() + td(days=1):
            pretty += f' ({i18n["schedule"]["days"]["tomorrow"]})'
        else:
            pretty += f' ({i18n["schedule"]["days"]["next"][int(when.strftime("%w"))]})'
    return pretty


def pretty_prev_pair(pair, when):
    if (not pair or not when):
        return f'<b>{i18n["schedule"]["empty_prev"]}</b>'
    pretty = f'<b>{pair["start"]} - {pair["end"]}</b>  <i>{i18n["schedule"]["pairs_type"][pair["type"]]}</i>\n'
    pretty += f'<pre>{pair["subject"]["name"]}</pre>\n'
    pretty += f'<b>{i18n["schedule"]["room"]}</b> {pair["room"]}\n'
    if pair["teacher"]:
        pretty += f'<b>{i18n["schedule"]["teacher"]}</b> <i>{i18n["schedule"]["teacher_degrees"][pair["teacher"]["degree"]]}</i> {pair["teacher"]["name"]}\n'
    if pair["class_link"]:
        pretty += f'[<a href="{pair["class_link"]}">{i18n["schedule"]["class_link"]}</a>] '
    if pair["meet_link"]:
        pretty += f'[<a href="{pair["meet_link"]}">{i18n["schedule"]["meet_link"]}</a>]'
    if (not (pair["class_link"] or pair["meet_link"])):
        pretty = pretty[:-1]
    pretty += f'\n\n<b>{i18n["schedule"]["when"]}</b> {when.strftime("%d.%m.%Y")}'
    print(date.today() - td(days=1))
    if when == date.today():
        pretty += f' ({i18n["schedule"]["days"]["today"]})'
    elif when == date.today() - td(days=1):
        pretty += f' ({i18n["schedule"]["days"]["yesterday"]})'
    else:
        pretty += f' ({i18n["schedule"]["days"]["prev"][int(when.strftime("%w"))]})'
    return pretty


def get_now_pair():
    day = date.today()
    pairs = build_pairs(day)
    if pairs:
        for pair in pairs:
            h1 = int(pair["start"].split(":")[0])
            m1 = int(pair["start"].split(":")[1])
            h2 = int(pair["end"].split(":")[0])
            m2 = int(pair["end"].split(":")[1])
            t = dt.now().time()
            h3 = t.hour
            m3 = t.minute
            M1 = h1*60 + m1
            M2 = h2*60 + m2
            M3 = h3*60 + m3
            if M1 < M3 < M2:
                return pair
    return None


def pretty_now_pair(pair):
    if (not pair):
        return f'<b>{i18n["schedule"]["empty_now"]}</b>'
    pretty = f'<b>{i18n["schedule"]["now"]}</b>\n\n'
    pretty += f'<b>{pair["start"]} - {pair["end"]}</b>  <i>{i18n["schedule"]["pairs_type"][pair["type"]]}</i>\n'
    pretty += f'<pre>{pair["subject"]["name"]}</pre>\n'
    pretty += f'<b>{i18n["schedule"]["room"]}</b> {pair["room"]}\n'
    if pair["teacher"]:
        pretty += f'<b>{i18n["schedule"]["teacher"]}</b> <i>{i18n["schedule"]["teacher_degrees"][pair["teacher"]["degree"]]}</i> {pair["teacher"]["name"]}\n'
    if pair["class_link"]:
        pretty += f'[<a href="{pair["class_link"]}">{i18n["schedule"]["class_link"]}</a>] '
    if pair["meet_link"]:
        pretty += f'[<a href="{pair["meet_link"]}">{i18n["schedule"]["meet_link"]}</a>]'
    if (not (pair["class_link"] or pair["meet_link"])):
        pretty = pretty[:-1]
    pretty += f'\n\n{i18n["schedule"]["all_today"]}'
    return pretty


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds
