import io
import re
import json
import yaml
import magic
import py7zr
import zipfile
import rarfile
import requests
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

def check_archive():
    try: checkArchive = checkArchive
    except UnboundLocalError:
        with open("./conf.json", "r") as f: dat = json.load(f); checkArchive = dat["checkArchive"]
    finally: return checkArchive

def check_image():
    try: checkImage = checkImage
    except UnboundLocalError:
        with open("./conf.json", "r") as f: dat = json.load(f); checkImage = dat["checkImage"]
    finally: return checkImage

def check_textfile():
    try: checkTextfile = checkTextfile
    except UnboundLocalError:
        with open("./conf.json", "r") as f: dat = json.load(f); checkTextfile = dat["checkTextfile"]
    finally: return checkTextfile

def check_attachments():
    try: checkFile = checkFile
    except UnboundLocalError:
        with open("./conf.json", "r") as f: dat = json.load(f); checkFile = dat["checkAttachments"]
    finally: return checkFile

def search(input): return bool(re.search(r"\b[a-zA-Z0-9\-\_]{24,26}\.[a-zA-Z0-9\-\_]{6}\.[a-zA-Z0-9\-\_]{38}", input))

def decoder_search(data): 
    try: content = data.decode("utf-8")
    except UnicodeDecodeError: return False
    else: return search(content)

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
    with open('./conf.json', 'r') as f: 
        data = json.load(f)
    if int(msg.author.id) not in data["ignored"]:
        if search(msg.content) == True: await delete(msg)
        else:
            if check_attachments() == True:
                if msg.attachments != []:
                    mime = magic.Magic(mime=True)
                    for i in msg.attachments:
                        resp = requests.get(i.url)
                        ft = mime.from_buffer(resp.content)
                        if ft.startswith("text"):
                            if check_textfile() == True:
                                if decoder_search(resp.content) == True: await delete(msg); break
                        elif ft.startswith("image"):
                            if check_image() == True:
                                pass#
                        elif ft.startswith("application"):
                            if check_archive() == True:
                                if ft.endswith("/zip"):
                                    try: z = zipfile.ZipFile(io.BytesIO(resp.content)); zdata = {name: z.read(name) for name in z.namelist()}
                                    except: pass
                                    else:
                                        for i in zdata:
                                            if decoder_search(zdata[i]) == True: await delete(msg); break
                                elif ft.endswith("/x-7z-compressed"):
                                    try: z = py7zr.SevenZipFile(io.BytesIO(resp.content)); zdata = z.readall()
                                    except: pass
                                    else:
                                        for i in zdata:
                                            if decoder_search(zdata[i].read()) == True: await delete(msg); break
                                elif ft.endswith("/x-rar"):
                                    try: z = rarfile.RarFile(io.BytesIO(resp.content))
                                    except Exception as e: print (e)
                                    else:
                                        for i in z.infolist():
                                            if decoder_search(z.read(i)) == True: await delete(msg); break
                                else:
                                    pass

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