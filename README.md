# Token Protector

A open source python bot that scan and delete messages with discord token.

## Installation

You can install all required modules/library by doing `pip install -r requirements-(windows/debian).txt`
You also need to create a file `.env` under the same directory with your token in it. (`token=INSERT_YOUR_TOKEN`, check `.env.example`)

## Usage

The bot will be active once it joined the server. It will scan through the message content, text files and top layer of archives.</br>
Supported format:

- text files
- zip (with CRC32 encryption)
- 7zip
- rar
- tar
- gzip (tar compression/text file)
- bzip2 (tar compression/text file)

## Commands

There is only 2 commands.</br>
`/language` switch between languages.
`/toggle` toggle the bot's scanning function for a single user.

## Hosted Bot

This bot is also hosted by me. You can invite it [here](https://github.com/ItsRqtl/TokenProtector/) (currently unavailable).

## License

This project is under `MIT License`. You can check the details in [LICENSE](/LICENSE).
