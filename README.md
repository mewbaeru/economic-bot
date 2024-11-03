# economic-bot
![Static Badge](https://img.shields.io/badge/mewbaeru-EconomyBot-economybot)
![Python Version](https://img.shields.io/badge/Python-3.12.4-blue.svg)
![GitHub Repo stars](https://img.shields.io/github/stars/mewbaeru/economic-bot)
![GitHub issues](https://img.shields.io/github/issues/mewbaeru/economic-bot)

> [!IMPORTANT]
> This project shows only the visual components of the bot in Discord.

Economy bot for discord made using [Disnake](https://github.com/DisnakeDev/disnake) and [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy).
===
# Usage
+ Install the required modules:
```
pip install -r requirements.txt
```
+ Create a file `.env` with these contents:
```
TOKEN=your_bot_token
```
+ Create a file `settings.json` _(to fill it out, take it as a basis [`example.settings.json`](https://github.com/mewbaeru/economic-bot/blob/main/assets/.example.settings.json)_.
+ Fill in the `assets/profile/font` _(**ttf**-expanded content)_ and `assets/role_play_gif` _(**gif**-expanded content)_ folders.
  
# Running the bot
```
python main.py
```
