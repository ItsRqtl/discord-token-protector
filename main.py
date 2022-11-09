import io
import re
import bz2
import json
import gzip
import yaml
import magic
import py7zr
import tarfile
import zipfile
import rarfile
import requests
from interactions import *
from interactions.ext.tasks import IntervalTrigger, create_task
from decouple import config as env

with open("./conf.json", "r") as f:
    dat = json.load(f)
    checkArchive = dat["checkArchive"]
    checkImage = dat["checkImage"]
    checkTextfile = dat["checkTextfile"]
    checkFile = dat["checkAttachments"]

client = Client(
    token=env("token"), intents=Intents.DEFAULT | Intents.GUILD_MESSAGE_CONTENT
)


async def new_guild(guild):
    with open("./locales/settings.json", "r") as f:
        data = json.load(f)
    data[f"{guild.id}"] = 0
    with open("./locales/settings.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=False)


@client.event
async def on_start():
    bot = await client._http.get_self()
    print(f'\nLogged in as\n{bot["username"]}#{bot["discriminator"]}\n{bot["id"]}\n')
    await client.change_presence(
        ClientPresence(
            activities=[
                PresenceActivity(
                    type=PresenceActivityType.WATCHING, name="Leaked Tokens"
                )
            ],
            status=StatusType.ONLINE,
        )
    )
    with open("./locales/settings.json", "r") as f:
        data = json.load(f)
    dblist = list(data.keys())
    for g in client.guilds:
        if str(g.id) not in dblist:
            await new_guild(g)


@client.event()
async def on_guild_create(guild):
    with open("./locales/settings.json", "r") as f:
        data = json.load(f)
    if str(guild.id) not in data.keys():
        await new_guild(guild)


@client.event()
async def on_guild_delete(guild):
    with open("./locales/settings.json", "r") as f:
        data = json.load(f)
    data.pop(int(guild.id))
    with open("./locales/settings.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=False)


def locale(key: str, guild_id):
    try:
        with open("./locales/settings.json", "r") as f:
            data = json.load(f)
            lang = data[str(guild_id)]
    except KeyError:
        lang = 0
    finally:
        if lang == 0:
            lang = "en-us"
        elif lang == 1:
            lang = "zh-hant"
        elif lang == 2:
            lang = "zh-hans"
        with open(f"./locales/{lang}.yml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data[key]


def search(input):
    return bool(
        re.search(
            r"\b[a-zA-Z0-9\-\_]{24,26}\.[a-zA-Z0-9\-\_]{6}\.[a-zA-Z0-9\-\_]{38}", input
        )
    )


def decoder_search(data):
    try:
        content = data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    else:
        return search(content)


async def delete(msg: Message):
    channel = await msg.get_channel()
    perms = await channel.get_permissions_for(
        await get(client, Member, guild_id=msg.guild_id, object_id=client.me.id)
    )
    if Permissions.MANAGE_MESSAGES in perms or Permissions.ALL in perms:
        await msg.reply(eval(f'f"""{locale("deleted", msg.guild_id)}"""'))
        await msg.delete()
    elif Permissions.SEND_MESSAGES in perms:
        await msg.reply(eval(f'f"""{locale("missing-del", msg.guild_id)}"""'))


@client.event
async def on_message_create(msg: Message):
    # check if not dm
    channel = await msg.get_channel()
    if channel.type != ChannelType.DM:
        # check if user prevent the bot from scanning messages
        with open("./conf.json", "r") as f:
            data = json.load(f)
        if int(msg.author.id) not in data["ignored"]:
            if search(msg.content) == True:
                await delete(msg)  # message content search
            elif checkFile == True and msg.attachments != []:
                # guess the type
                mime = magic.Magic(mime=True)
                for attach in msg.attachments:
                    resp = requests.get(attach.url)
                    ft = mime.from_buffer(resp.content)

                            # text file support
                    if ft.startswith("text"):
                        if (
                            checkTextfile == True
                            and decoder_search(resp.content) == True
                        ):
                            await delete(msg)
                            break

                    elif ft.startswith("image"):
                        pass
                    elif ft.startswith("application"):
                                    # zip support
                        if ft.endswith("/zip"):
                            if checkArchive == True:
                                try:
                                    z = zipfile.ZipFile(
                                        io.BytesIO(resp.content)
                                    )
                                except:
                                    pass
                                else:
                                    for i in z.namelist():
                                        if decoder_search(z.read(i)) == True:
                                            await delete(msg)
                                            break

                        elif ft.endswith("/x-7z-compressed"):
                            if checkArchive == True:
                                try:
                                    z = py7zr.SevenZipFile(
                                        io.BytesIO(resp.content)
                                    )
                                except:
                                    pass
                                else:
                                    for i in z.getnames():
                                        if (
                                            decoder_search(z.read(i)[i].read())
                                            == True
                                        ):
                                            await delete(msg)
                                            break

                        elif ft.endswith("/x-rar"):
                            if checkArchive == True:
                                try:
                                    z = rarfile.RarFile(
                                        io.BytesIO(resp.content)
                                    )
                                except:
                                    pass
                                else:
                                    for i in z.infolist():
                                        if decoder_search(z.read(i)) == True:
                                            await delete(msg)
                                            break

                        elif ft.endswith("/x-tar"):
                            if checkArchive == True and tarfile.is_tarfile(
                                io.BytesIO(resp.content)
                            ):
                                try:
                                    tarz = tarfile.open(
                                        fileobj=io.BytesIO(resp.content)
                                    )
                                except:
                                    pass
                                else:
                                    for i in tarz.getmembers():
                                        if (
                                            decoder_search(
                                                tarz.extractfile(i).read()
                                            )
                                            == True
                                        ):
                                            await delete(msg)
                                            break

                        elif ft.endswith("/gzip") or ft.endswith("/x-gzip"):
                            if checkArchive == True:
                                try:
                                    zdata = gzip.decompress(resp.content)
                                except:
                                    pass
                                else:
                                    if tarfile.is_tarfile(io.BytesIO(zdata)):
                                        try:
                                            tarz = tarfile.open(
                                                fileobj=io.BytesIO(zdata)
                                            )
                                        except:
                                            pass
                                        else:
                                            for i in tarz.getmembers():
                                                if (
                                                    decoder_search(
                                                        tarz.extractfile(
                                                            i
                                                        ).read()
                                                    )
                                                    == True
                                                ):
                                                    await delete(msg)
                                                    break
                                    elif decoder_search(zdata) == True:
                                        await delete(msg)
                                        break

                        elif ft.endswith("x-bzip2"):
                            if checkArchive == True:
                                try:
                                    zdata = bz2.decompress(resp.content)
                                except:
                                    pass
                                else:
                                    if tarfile.is_tarfile(io.BytesIO(zdata)):
                                        try:
                                            tarz = tarfile.open(
                                                fileobj=io.BytesIO(zdata)
                                            )
                                        except:
                                            pass
                                        else:
                                            for i in tarz.getmembers():
                                                if (
                                                    decoder_search(
                                                        tarz.extractfile(
                                                            i
                                                        ).read()
                                                    )
                                                    == True
                                                ):
                                                    await delete(msg)
                                                    break
                                    elif decoder_search(zdata) == True:
                                        await delete(msg)
                                        break


@client.command(
    name="language",
    name_localizations={Locale.CHINESE_TAIWAN: "語言", Locale.CHINESE_CHINA: "语言"},
    description="change the bot's language",
    description_localizations={
        Locale.CHINESE_TAIWAN: "更變機器人的語言",
        Locale.CHINESE_CHINA: "更变机器人的语言",
    },
    options=[
        Option(
            type=OptionType.INTEGER,
            name="language",
            name_localizations={
                Locale.CHINESE_TAIWAN: "語言",
                Locale.CHINESE_CHINA: "语言",
            },
            description="select the new language",
            description_localizations={
                Locale.CHINESE_TAIWAN: "選擇新語言",
                Locale.CHINESE_CHINA: "选择新语言",
            },
            required=True,
            choices=[
                Choice(
                    name="English (US)",
                    value=0,
                    name_localizations={
                        Locale.CHINESE_TAIWAN: "美式英文",
                        Locale.CHINESE_CHINA: "美式英文",
                    },
                ),
                Choice(
                    name="Chinese (TW)",
                    value=1,
                    name_localizations={
                        Locale.CHINESE_TAIWAN: "繁體中文",
                        Locale.CHINESE_CHINA: "繁体中文",
                    },
                ),
                Choice(
                    name="Chinese (CN)",
                    value=2,
                    name_localizations={
                        Locale.CHINESE_TAIWAN: "簡體中文",
                        Locale.CHINESE_CHINA: "简体中文",
                    },
                ),
            ],
        )
    ],
    default_member_permissions=Permissions.MANAGE_GUILD,
    dm_permission=False,
)
async def language(ctx: CommandContext, language: int):
    with open("./locales/settings.json", "r") as f:
        data = json.load(f)
    data[str(ctx.guild_id)] = language
    with open("./locales/settings.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=False)
    await ctx.send(
        eval(f'f"""{locale("langupdated", ctx.guild_id)}"""'), ephemeral=True
    )


@client.command(
    name="toggle",
    name_localizations={Locale.CHINESE_TAIWAN: "切換開關", Locale.CHINESE_CHINA: "切换开关"},
    description="toggle the bot for you",
    description_localizations={
        Locale.CHINESE_TAIWAN: "切換機器人的開關",
        Locale.CHINESE_CHINA: "切换机器人的开关",
    },
)
async def toggle(ctx: CommandContext):
    with open("./conf.json", "r") as f:
        data = json.load(f)
    if int(ctx.user.id) in data["ignored"]:
        data["ignored"].remove(int(ctx.user.id))
        await ctx.send(
            eval(f'f"""{locale("toggledAdded", ctx.guild_id)}"""'), ephemeral=True
        )
    else:
        data["ignored"].append(int(ctx.user.id))
        await ctx.send(
            eval(f'f"""{locale("toggledRemoved", ctx.guild_id)}"""'), ephemeral=True
        )
    with open("./conf.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=False)


client.start()
