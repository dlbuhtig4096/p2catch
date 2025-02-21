from discord.ext import commands
from colorama import Fore, Style, init
import asyncio
import random
import json
import re
import datetime
import os
import base64

Config = json.load(
    open("config.json", "r", encoding = "utf-8")
)

POKETWO = 716390085896962058
SPAWN = Config["spawn"]
SPAM = Config["spam"]

class Repo(dict):
    _ = set()

    def __init__(self, data):
        super(Repo, self).__init__(self)
        for s in data:
            try:
                self[len(s)].add(s)
            except KeyError:
                self[len(s)] = {s}

    def find(self, key):
        for s in self.get(len(key), self._):
            for c, d in zip(s, key):
                if d != "_" and c != d: break
            else:
                return s

        return None

Pokemon = Repo(
    json.load(
        open("pokemon.json", "r", encoding = "utf-8")
    )
)

init()
current_datetime = datetime.datetime.now()
timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

print(
    Fore.YELLOW,
    """
  _____      _     __ _                 
 |  __ \    | |   /_/| |                
 | |__) |__ | | _____| |___      _____  
 |  ___/ _ \| |/ / _ \ __\ \ /\ / / _ \ 
 | |  | (_) |   <  __/ |_ \ V  V / (_) |
 |_|   \___/|_|\_\___|\__| \_/\_/ \___/ 
    """,
    Style.RESET_ALL
)

def helper():
    bot = commands.Bot(command_prefix = "!")
    pause = False

    async def send_message(channel_id, message):
        try:
            channel = bot.get_channel(channel_id)
            await channel.send(message)
        except Exception as e:
            print(f"{Fore.RED}Error in send_message: {e}{Style.RESET_ALL}")

    @bot.event
    async def on_ready():
        print(f"[{timestamp}] [INFO] - {Fore.LIGHTGREEN_EX}Logged on as {bot.user}{Style.RESET_ALL}")
        while True:
            t = 4.0
            if pause:
                await send_message(SPAWN, "<@%s> h" % POKETWO)
            else:
                await send_message(SPAM, base64.b64encode(os.urandom(15)).decode())
                t = random.uniform(1.5, 2.0)
            await asyncio.sleep(t)

    @bot.event
    async def on_message(message):
        nonlocal pause
        
        try:
            if message.author.id == POKETWO and message.channel.id == SPAWN:
                content = message.content
                if message.embeds:
                    embed_title = message.embeds[0].title
                    if "wild pokémon has appeared!" in embed_title: pause = True

                elif content.startswith("Congratulations"):
                    if re.search(r"Congratulations <@\d+>! (.+)", content): pause = False

        except Exception as e:
            print(f"[{timestamp}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")

    return bot

def farmer():
    bot = commands.Bot(command_prefix = "!")

    @bot.event
    async def on_ready():
        print(f"[{timestamp}] [INFO] - {Fore.LIGHTGREEN_EX}Logged on as {bot.user}{Style.RESET_ALL}")
        return

    @bot.event
    async def on_message(message):
        try:
            if message.author.id == POKETWO and message.channel.id == SPAWN:
                content = message.content
                if content.startswith("The pokémon is "):
                    hint = content[len("The pokémon is "):].strip(".").strip().replace("\\", "")
                    print(f"[{timestamp}] [HINT] - {Fore.YELLOW}Pokemon Hint: {Style.RESET_ALL}{hint}")
                    result = Pokemon.find(hint)
                    if result:
                        await message.channel.send("<@%s> c %s" % (POKETWO, result))
                        print(f"[{timestamp}] [HINT] - {Fore.LIGHTGREEN_EX}Search Result: {Style.RESET_ALL}{result}")
                    else:
                        print(f"[{timestamp}] [ERROR] - {Fore.RED}Pokemon Not Founded In Database{Style.RESET_ALL}")

                elif content.startswith("Congratulations"):
                    match = re.search(r"Congratulations <@\d+>! (.+)", content)
                    if match:
                        hint = match.group(1)
                        print(f"[{timestamp}] [INFO] - {Fore.LIGHTGREEN_EX}{hint}{Style.RESET_ALL}")
                    await message.guild.ack()

                elif content.startswith("That is the wrong pokémon!"):
                    print(f"[{timestamp}] [INFO] - {Fore.RED}That is the wrong pokémon!{Style.RESET_ALL}")


        except Exception as e:
            print(f"[{timestamp}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")

    return bot

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(helper().start(Config["help"]))
loop.create_task(farmer().start(Config["farm"]))
loop.run_forever()
