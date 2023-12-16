# Token Protector

A open source python bot that scan and delete messages with discord token.

## Installation

You can install all required modules/library by doing `pip install -r requirements.txt`  
You also need to create a file `.env` under the same directory with your token in it. (`token=INSERT_YOUR_TOKEN`, check `.env.example`)

## Usage

The bot will be active once it joined the server.  
It will scan through the message content and attachments (less than 25MiB), including plain text and top layer of archives (up to 25 files, without password).

Supported format:

- plain text files
- zip (with CRC32 encryption)
- 7zip
- rar
- tar
- gzip (tar compression/text file)
- bzip2 (tar compression/text file)

## Commands

There is only 2 commands.  
`/language` switch between languages.  
`/opt-out` opt out from the protection (re-run the command to opt in).

## Hosted Bot

This bot is also hosted by me. You can invite it [here](https://github.com/ItsRqtl/TokenProtector/) (available soon).

## License

This project is under `MIT License`. You can check the details in [LICENSE](/LICENSE).
