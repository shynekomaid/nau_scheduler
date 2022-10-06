# This script should run every morning for example (07:30) (from crontab or systemd timer)

from core import pretty_pairs, build_pairs, send_to_subscribers, log2file, prepare_config, prepare_language


if __name__ == "__main__":
    log2file("Starting MOTD script")
    config = prepare_config("config/settings.json")
    i18n = prepare_language(config["language"])
    pairs = build_pairs()
    if len(pairs) > 0:
        message = i18n["system_messages"]["motd"]
        message += pretty_pairs(pairs)
        send_to_subscribers(message)
        log2file("MOTD: Sent")
    else:
        log2file("MOTD: No pairs today")
