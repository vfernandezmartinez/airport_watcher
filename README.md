# Airport Watcher
## Introduction
Every once in a while, airlines introduce new flight routes. If you fly often or if you like travelling, you might want to be aware of new destinations that are reachable from your closest airport.

Airport Watcher watches the wikipedia page of your airport and keeps track of changes to destinations. Whenever a new destination is added, it sends you a notification via a Telegram bot.

## Setup
### Creating a Telegram bot
In Telegram, use [@BotFather](https://t.me/BotFather) to create your own bot. Follow the instructions provided by [@BotFather](https://t.me/BotFather) and get your bot token.

Once you have the bot created, you also need to find out your chat id. It's an 8-digit number. Use [@userinfobot](https://t.me/userinfobot) to find it out.

### Installing Airport Watcher dependencies
Execute the following command:

    ./setup.sh

### Running Airport Watcher
You can run Airport Watcher as a daily cron job in your preferred server. Open a terminal and type the following:

    crontab -e
Then copy and paste the following line:

    SHELL=/bin/bash
    0 10 * * * /path/airport_watcher/run.sh --airport 'Madrid Airport' --bot_token <your_telegram_bot_token> --chat_id <your_telegram_chat_id>

Adjust the path and the parameters. This will run it at 10:00am in your local time zone.