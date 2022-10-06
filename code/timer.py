# This script should run every 15 minutes (from crontab or systemd timer)

from core import prepare_config, log2file, prepare_language, get_next_pair, pretty_next_pair, send_to_subscribers, convert_timedelta, save_config
from datetime import date, timedelta as td, datetime as dt, time as datetime_time

from time import time as get_unix

window = 10

if __name__ == "__main__":
    log2file("Starting timer script")
    config = prepare_config("config/settings.json")
    if ("last_send" in config):
        if (get_unix() - config["last_send"] + 1) < window:
            log2file("Timer: Has been sent recently")
            exit()
    else:
        config["last_send"] = 0
    i18n = prepare_language(config["language"])
    pair, when = get_next_pair()
    if when == date.today():
        # check if pair between now and now + window
        future = dt.now() + td(minutes=window)
        now = dt.now()
        h0 = now.hour
        m0 = now.minute
        h1 = future.hour
        m1 = future.minute
        h2 = int(pair["start"].split(":")[0])
        m2 = int(pair["start"].split(":")[1])
        M0 = h0 * 60 + m0
        M1 = h1 * 60 + m1
        M2 = h2 * 60 + m2
        pair_time = datetime_time(h2, m2)
        time_diff = convert_timedelta(dt.combine(date.today(), pair_time) -
                                      dt.combine(date.today(), now.time()))
        minutes_before = time_diff[1]
        seconds_before = time_diff[2]
        if M0 <= M2 <= M1:
            config["last_send"] = get_unix()
            save_config()
            pretty = i18n["schedule"]["pair_soon"].format(
                minutes=minutes_before, seconds=seconds_before)
            pretty += pretty_next_pair(pair, when, need_when=False)
            send_to_subscribers(pretty)
            log2file("Sending notification. Pair at: {}".format(pair["start"]))
        else:
            log2file("Timer: No pairs in window")

    else:
        log2file("No pair today")
