# Airport Watcher
## Introduction
Every once in a while, airlines introduce new flight routes. If you fly often or if you like travelling, you might want to be aware of new destinations that are reachable from your closest airport.

Airport Watcher watches the wikipedia page of your airport and keeps track of changes to destinations. Whenever a destination is added or removed, it sends you a notification via a Telegram bot.

## Setup
### Creating a Telegram bot
Creating a Telegram bot is really simple. In Telegram, use [@BotFather](https://t.me/BotFather) to create your own bot. Follow the instructions provided by [@BotFather](https://t.me/BotFather) and get your bot token. Please keep in mind the token should be treated with the same care as with any other API token or password.

Once you have the bot created, you also need to find out your chat id. It's an 8-digit number. Use [@userinfobot](https://t.me/userinfobot) to find it out.

### Installing Airport Watcher dependencies
Execute the following commands to create a virtual environment and install required dependencies in it:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Airport Watcher is now ready to be used.

## Running Airport Watcher
You can run Airport Watcher as a daily cron job in your preferred server, e.g. in a Raspberry Pi or in the cloud. It is recommended to run it with a regular non-privileged user.

Open a terminal and type the following:

    crontab -e
Then copy and paste the following line:

    SHELL=/bin/bash
    0 10 * * * /path/airport_watcher/run.sh --airport 'Madrid Airport' --bot_token <your_telegram_bot_token> --chat_id <your_telegram_chat_id>

Adjust the path and the parameters. This example will run it at 10:00am in your local time zone.

### Specifying storage directory
Airport Watcher stores the last known destinations offered from each airport in a .json file. This is required in order to be able to detect changes since the last run. By default, files are located in the current directory. You can customize the directory where these files are stored by using the optional `--store` parameter:

    ./run.sh --store /tmp --airport 'Mexico City International Airport' --bot_token <your_telegram_bot_token> --chat_id <your_telegram_chat_id>

### Watching multiple airports
It is possible to watch more than one airport. Simply run Airport Watcher as many times as required passing each of the desired airports. For example:

    ./run.sh --airport 'Heathrow Airport' --bot_token <your_telegram_bot_token> --chat_id <your_telegram_chat_id>
    ./run.sh --airport 'London Gatwick Airport' --bot_token <your_telegram_bot_token> --chat_id <your_telegram_chat_id>
    ./run.sh --airport 'London Stansted Airport' --bot_token <your_telegram_bot_token> --chat_id <your_telegram_chat_id>
    ./run.sh --airport 'London Luton Airport' --bot_token <your_telegram_bot_token> --chat_id <your_telegram_chat_id>
    ./run.sh --airport 'London City Airport' --bot_token <your_telegram_bot_token> --chat_id <your_telegram_chat_id>

## Unit Tests
As with any other Python app, unit tests can be run this way:

    source venv/bin/activate
    python3 -m unittest
