# Token Protector

A open source python bot that scan and delete messages with discord token.

## Installation

You can install all required modules/library by doing `pip install -r requirements.txt`  
Please also follow the installation instructions of [python-magic](https://github.com/ahupp/python-magic#installation) library to install the required library for magic.

You need to create a file `.env` under the same directory with your token in it. (`token=INSERT_YOUR_TOKEN`, check `.env.example`)  
You also need to create a file `config.toml` under the config folder. (check `config/config.toml.example`)

## Usage

The bot will be active once it joined the server.  
It will scan through the message content and attachments (less than 25MiB), including plain text and top layer of archives (up to 25 files, without password).

Supported format:

- plain text files
- zip
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

This bot is also hosted by me. You can invite it [here](https://ptb.discord.com/api/oauth2/authorize?client_id=1015401626632212560&permissions=274877983744&scope=bot).

## License

This project is under `MIT License`. You can check the details in [LICENSE](/LICENSE).
