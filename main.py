import json
import re
import requests
import yaml
from interactions import *
from decouple import config as env

client = Client(token=env("token"), intents = Intents.DEFAULT | Intents.GUILD_MESSAGE_CONTENT)

async def new_guild(guild):
    with open('./locales/settings.json', 'r') as f: data = json.load(f)
    data[f'{guild.id}'] = 0
    with open('./locales/settings.json', 'w') as f: json.dump(data, f, indent=4 ,sort_keys=False)

@client.event
async def on_start(): 
    bot = await client._http.get_self(); print(f'\nLogged in as\n{bot["username"]}#{bot["discriminator"]}\n{bot["id"]}\n')
    await client.change_presence(ClientPresence(activities=[PresenceActivity(type=PresenceActivityType.WATCHING, name="Leaked Tokens")], status=StatusType.ONLINE))
    dblist = []
    with open('./locales/settings.json', 'r') as f: data = json.load(f)
    for i in data.keys(): dblist.append(i)
    for g in client.guilds:
        if str(g.id) not in dblist: await new_guild(g)

@client.event()
async def on_guild_create(guild):
    with open('./locales/settings.json', 'r') as f: data = json.load(f)
    if str(guild.id) not in data.keys(): await new_guild(guild)

@client.event()
async def on_guild_delete(guild):
    with open('./locales/settings.json', 'r') as f: data = json.load(f)
    data.pop(int(guild.id))
    with open('./locales/settings.json', 'w') as f: json.dump(data, f, indent=4 ,sort_keys=False)   

def locale(key:str, guild_id):
    with open('./locales/settings.json', 'r') as f: data = json.load(f); lang = data[str(guild_id)]
    if lang == 0: lang = "en-us"
    elif lang == 1: lang = "zh-hant"
    elif lang == 2: lang = "zh-hans"
    with open(f'./locales/{lang}.yml', 'r', encoding='utf-8') as f: data = yaml.safe_load(f); return data[key]

def search(input): return bool(re.search(r"\b[a-zA-Z0-9\-\_]{24,26}\.[a-zA-Z0-9\-\_]{6}\.[a-zA-Z0-9\-\_]{38}", input))

async def delete(msg:Message):
    channel = await msg.get_channel(); perms = await channel.get_permissions_for(await get(client, Member, guild_id=msg.guild_id, object_id=client.me.id))
    if Permissions.MANAGE_MESSAGES in perms or Permissions.ALL in perms:
        await msg.reply(eval(f'f"""{locale("deleted", msg.guild_id)}"""'))
        await msg.delete()
    elif Permissions.SEND_MESSAGES in perms:
        await msg.reply(eval(f'f"""{locale("missing-del", msg.guild_id)}"""'))
    else: pass

@client.event
async def on_message_create(msg:Message):
    if search(msg.content) == True: await delete(msg)
    else:
        if msg.attachments != []:
            for i in msg.attachments:
                resp = requests.get(i.url)
                try: content = resp.content.decode("utf-8")
                except UnicodeDecodeError: pass
                else:
                    if search(content) == True: await delete(msg); break

@client.command(
    name="language", name_localizations={Locale.CHINESE_TAIWAN: "語言", Locale.CHINESE_CHINA: "语言"}, 
    description="change the bot's language", description_localizations={Locale.CHINESE_TAIWAN: "更變機器人的語言", Locale.CHINESE_CHINA: "更变机器人的语言"}, 
    options=[
        Option(
            type=OptionType.INTEGER, 
            name="language", name_localizations={Locale.CHINESE_TAIWAN: "語言", Locale.CHINESE_CHINA: "语言"}, 
            description="select the new language", description_localizations={Locale.CHINESE_TAIWAN: "選擇新語言", Locale.CHINESE_CHINA: "选择新语言"}, 
            required=True, choices=[
                Choice(name="English (US)", value=0, name_localizations={Locale.CHINESE_TAIWAN: "美式英文", Locale.CHINESE_CHINA: "美式英文"}),
                Choice(name="Chinese (TW)", value=1, name_localizations={Locale.CHINESE_TAIWAN: "繁體中文", Locale.CHINESE_CHINA: "繁体中文"}),
                Choice(name="Chinese (CN)", value=2, name_localizations={Locale.CHINESE_TAIWAN: "簡體中文", Locale.CHINESE_CHINA: "简体中文"})
            ]
        )
    ],
    default_member_permissions=Permissions.MANAGE_GUILD,
    dm_permission=False, scope=652456645796036619
)
async def language(ctx:CommandContext, language:int):
    with open('./locales/settings.json', 'r') as f: data = json.load(f)
    data[str(ctx.guild_id)] = language
    with open('./locales/settings.json', 'w') as f: json.dump(data, f, indent=4 ,sort_keys=False)
    await ctx.send(eval(f'f"""{locale("langupdated", ctx.guild_id)}"""'), ephemeral=True)

client.start()