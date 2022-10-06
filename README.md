# NAU SCHEDULER BOT

## Table of Contents

- [NAU SCHEDULER BOT](#nau-scheduler-bot)
  - [Table of Contents](#table-of-contents)
  - [Install guide](#install-guide)
    - [Requirements](#requirements)
    - [Deployment](#deployment)
      - [Install requirements](#install-requirements)
      - [Clone the repository](#clone-the-repository)
      - [Prepare virtual environment](#prepare-virtual-environment)
      - [Create config file](#create-config-file)
      - [Config bot in telegram side](#config-bot-in-telegram-side)

## Install guide

### Requirements

- Linux server (preferably Ubuntu 18.04 or higher)
- Python 3.7 or higher
- SystemD (optional, but recommended)
- Crontab (if you don't want to use SystemD)

### Deployment

#### Install requirements

Installing Install Python3, pip and virtualenv:

```bash
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-venv
```

#### Clone the repository

> I recomend cloning it to `/opt/nau-scheduler-bot` directory, but you can choose any other directory.
>
> If you choose another directory, keep in mind to change paths in `/systemd/nau-scheduler-bot.service` file.

```bash
sudo -i
cd /opt
git clone https://github.com/tminei/nau_scheduler
mv nau_scheduler nau-scheduler-bot
exit
sudo chown -R $USER:$USER /opt/nau-scheduler-bot
sudo chmod -R 755 /opt/nau-scheduler-bot
```

#### Prepare virtual environment

```bash
cd /opt/nau-scheduler-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Create config file

  > In settings.json you must specify your telegram bot token and your group chat id.
  >
  > You can get your bot token from [@BotFather](https://t.me/BotFather) and your group chat using get_updates method of telegram bot api.

Creating config file from template:

```bash
  cp config/default.json config/settings.json
  nano config/settings.json
```

#### Config bot in telegram side

Send `/start` command to your bot from admin account (admin_id in settings.json). If you don't do this, bot can't send debug messages to you.

Don't forget to add your bot to your group chat. If you don't do this, bot can't send messages to your group chat.
