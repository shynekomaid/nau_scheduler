# This script should run every 5 minutes (from crontab or systemd timer)

from core import prepare_config, log2file, prepare_language, build_pairs

if __name__ == "__main__":
    log2file("Starting timer script")
    config = prepare_config("config/settings.json")
    i18n = prepare_language(config["language"])
