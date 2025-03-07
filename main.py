from discord.ext import commands
from colorama import Fore, Style, init
import asyncio
import random
import json
import re
import datetime
import os
import base64

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

Config = json.load(
    open("config.json", "r", encoding = "utf-8")
)

POKETWO = 716390085896962058
GUILD = Config["guild"]
CATCH = Config["catch"]
CHAT = Config["chat"]
FARMER = Config["farmers"]
HELPER = Config["helpers"]
PLAYER = Config["players"]

init()

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

now = lambda : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def repeat(A):
    while True:
        for a in A: yield a

async def channel_send(bot, channel_id, message):
    try:
        await bot.get_channel(channel_id).send(message)
    except Exception as e:
        print(f"[{now()}] [ERROR] - {Fore.RED}Error in channel_send: {e}{Style.RESET_ALL}")

async def guild_ack(bot):
    try:
        await bot.get_guild(GUILD).ack()
    except Exception as e:
        print(f"[{now()}] [ERROR] - {Fore.RED}Error in ack: {e}{Style.RESET_ALL}")

def farmer(bots):
    if not bots: return ()
    
    wait = 3.0 / (len(bots) + 1.0)
    async def main():
        for bot in repeat(bots):
            await asyncio.sleep(wait)
            await channel_send(bot, CHAT, base64.b64encode(os.urandom(15)).decode())
    
    return (main, )

def helper(bots):
    if not bots: return ()
    chain = repeat(bots)

    wild = False
    async def main():
        while True:
            await asyncio.sleep(3.5)
            if wild: await channel_send(next(chain), CATCH, "<@%s> h" % POKETWO)

    @(bots[0]).event
    async def on_message(message):
        nonlocal wild
        try:
            if message.author.id != POKETWO or message.channel.id != CATCH: return
            if message.embeds and message.embeds[0].title.endswith("wild pokémon has appeared!"):
                wild = True
                await channel_send(next(chain), CATCH, "<@%s> h" % POKETWO)

            elif message.content.startswith("Congratulations"):
                wild = False

        except Exception as e:
            print(f"[{now()}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")
            
    return (main, )

def player(bots):
    if not bots: return ()
    chain = repeat(bots)

    @(bots[0]).event
    async def on_message(message):
        try:
            if message.author.id == POKETWO and message.channel.id == CATCH:
                content = message.content
                if content.startswith("The pokémon is "):
                    hint = content[15 : -1].strip().replace("\\", "")
                    print(f"[{now()}] [HINT] - {Fore.YELLOW}Pokemon Hint: {Style.RESET_ALL}{hint}")
                    result = Pokemon.find(hint)
                    if result:
                        await channel_send(next(chain), CATCH, "<@%s> c %s" % (POKETWO, result))
                        print(f"[{now()}] [HINT] - {Fore.LIGHTGREEN_EX}Search Result: {Style.RESET_ALL}{result}")
                    else:
                        print(f"[{now()}] [ERROR] - {Fore.RED}Pokemon Not Founded In Database{Style.RESET_ALL}")

                elif content.startswith("Congratulations"):
                    match = re.search(r"Congratulations <@\d+>! (.+)", content)
                    if not match: return
                    hint = match.group(1)
                    print(f"[{now()}] [INFO] - {Fore.LIGHTGREEN_EX}{hint}{Style.RESET_ALL}")
                    for bot in bots: await guild_ack(bot)

                elif content.startswith("That is the wrong pokémon!"):
                    print(f"[{now()}] [INFO] - {Fore.RED}That is the wrong pokémon!{Style.RESET_ALL}")
                    
        except Exception as e:
            print(f"[{now()}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")

    return ()

def main():
    bots = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for token in FARMER + HELPER + PLAYER:
        if token in bots: continue
        bots[token] = commands.Bot(command_prefix = "!")

    tasks = []
    for task in farmer([bots[token] for token in FARMER]): tasks.append(task)
    for task in helper([bots[token] for token in HELPER]): tasks.append(task)
    for task in player([bots[token] for token in PLAYER]): tasks.append(task)
    for token, bot in bots.items(): loop.create_task(bot.start(token))
    for task in tasks: loop.create_task(task())
    loop.run_forever()

if __name__ == "__main__": main()
