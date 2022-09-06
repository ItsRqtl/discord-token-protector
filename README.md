# Token Protector

A open source python bot that scan and delete messages with discord token.

## Installation

You can install all required modules/library by doing `pip install -r requirements.txt`
You also need to create a file `.env` under the same directory with your token in it. (`token=INSERT_YOUR_TOKEN`, check `.env.example`)

## Usage

The bot will be active once it joined the server. It will scan through the message content, text files and top layer of archives (currently support: 7z, rar, zip with CRC32 encryption).</br>
There is only 1 command.</br>
`/language` switch between languages.

## Hosted Bot

This bot is also hosted by me. You can invite it [here](https://discord.com/api/oauth2/authorize?client_id=1015401626632212560&permissions=11264&scope=bot).

## License

This project is under `MIT License`. You can check the details in [LICENSE](/LICENSE).
