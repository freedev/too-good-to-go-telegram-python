# Too Good To Go notification 

## TL;DR

This simple Python script helps to get mobile notification from ToGoodToGo when new offers appears from favorite list.

## Description

Once you have added all the users email in the file `constant.py` the file `get-credentials.py` can be invoked: users credentials will be stored locally.
Then the `main.py` can be scheduled to be executed iteratively, when new offers appears a new task (notification?) can be executed.

## Quick start

- Register your email with ToGoodToGo or install the App ToGoodToGo - https://toogoodtogo.com/
- Install App Telegram in your smartphone
- Create your own Telegram Bot with @BotFather and get your Telegram `token` - https://core.telegram.org/bots/features#botfather
- Get your Telegram Chat Id using Telegram Token - https://api.telegram.org/bot{TOKEN}/getUpdates
- Add your user into `constants.py` file `USERS` array: `UserData('your@email.com', 12345678)`
