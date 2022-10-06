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
        - [Getting your group chat id](#getting-your-group-chat-id)
      - [Config bot in telegram side](#config-bot-in-telegram-side)
      - [Create systemd service](#create-systemd-service)
      - [Start and enable systemd service](#start-and-enable-systemd-service)

## Install guide

### Requirements

- Linux server (preferably Ubuntu 18.04 or higher)
- Python 3.7 or higher
- SystemD (optional, but recommended)
- Crontab (if you don't want to use SystemD)

### Deployment

#### Install requirements

Installing Install Python3, pip and virtualenv:

Ubuntu 20.04 and higher:

```bash
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-venv
```

Ububtu 18.04:

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7
sudo apt install python3-pip
python3.7 -m pip install pip
sudo apt install python3.7-venv
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

Ubuntu 20.04 and higher:

```bash
cd /opt/nau-scheduler-bot
python3 -m venv sched
source sched/bin/activate
pip install -r requirements.txt
```

Ubuntu 18.04:

```bash
cd /opt/nau-scheduler-bot
python3.7 -m venv sched
source sched/bin/activate
python3.7 -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Create config file

  > In settings.json you must specify your telegram bot token and your group chat id.
  >
  > You can get your bot token from [@BotFather](https://t.me/BotFather) and your group chat using get_updates method of telegram bot api.

Creating config file from template:

```bash
  cp code/config/default.json code/config/settings.json
  nano code/config/settings.json
```

##### Getting your group chat id

1. Turn off any bot pooling for token
2. Add your bot to your group
3. Send any message to bot (ex: /group_id@tmischedule_bot). Replace @tmischedule_bot with your bot username
4. Open in browser <https://api.telegram.org/botTOKEN/getUpdates>. (Replace TOKEN with your bot token)
5. Search for `/group_id` and copy chat id

#### Config bot in telegram side

Send `/start` command to your bot from admin account (admin_id in settings.json). If you don't do this, bot can't send debug messages to you.

Don't forget to add your bot to your group chat. If you don't do this, bot can't send messages to your group chat.

#### Create systemd service

Move systemd service file to systemd directory:

Ubuntu 20.04 and higher:

```bash
sudo cp /opt/nau-scheduler-bot/systemd/ubuntu20.04/* /etc/systemd/system/
```

Ubuntu 18.04:

```bash
sudo cp /opt/nau-scheduler-bot/systemd/ubuntu18.04/* /etc/systemd/system/
```

#### Start and enable systemd service

```bash
sudo systemctl daemon-reload

sudo systemctl start scheduler_dispatcher.service
sudo systemctl enable scheduler_dispatcher.service

sudo systemctl start scheduler_timer.timer
sudo systemctl enable scheduler_timer.timer
```
