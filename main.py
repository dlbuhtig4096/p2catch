from discord.ext import commands
from colorama import Fore, Style, init
import asyncio
import random
import json
import re
import datetime
import os
import base64

class Ticker:
    def __init__(self):
        self.N = 0
        self.M = 0

    def add(self):
        self.N += 1
        return self.N

    def tick(self):
        M = self.M + 1
        if M >= self.N: M = 0
        self.M = M
        return M

    def lock(self, n):
        return self.M != n

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
HELPER = Config["helpers"]
FARMER = Config["farmers"]

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
async def _send(bot, channel_id, message):
    try:
        channel = bot.get_channel(channel_id)
        await channel.send(message)
    except Exception as e:
        print(f"{Fore.RED}Error in _send: {e}{Style.RESET_ALL}")

async def _ack(bot):
    try:
        guild = bot.get_guild(GUILD)
        await guild.ack()
    except Exception as e:
        print(f"{Fore.RED}Error in ack: {e}{Style.RESET_ALL}")

def helper(loop):
    ticker = Ticker()
    wild = False

    def task():
        bot = commands.Bot(command_prefix = "!")
        lock = ticker.add()


        @bot.event
        async def on_ready():
            print(f"[{now()}] [INFO] - {Fore.LIGHTGREEN_EX}Logged on as {bot.user}{Style.RESET_ALL}")
            while True:
                await _send(bot, CHAT, base64.b64encode(os.urandom(15)).decode())
                await asyncio.sleep(random.uniform(1.5, 2.0))
                if not wild or ticker.lock(lock): continue 
                await _send(bot, CATCH, "<@%s> h" % POKETWO)
                await asyncio.sleep(2.5)
                ticker.tick()

        return bot

    bots = [task() for token in HELPER]
    if not bots: return

    @(bots[0]).event
    async def on_message(message):
        nonlocal wild
        
        try:
            if message.author.id == POKETWO and message.channel.id == CATCH:
                content = message.content
                if message.embeds:
                    embed_title = message.embeds[0].title
                    if "wild pokémon has appeared!" in embed_title: wild = True

                elif content.startswith("Congratulations"):
                    if re.search(r"Congratulations <@\d+>! (.+)", content): wild = False

        except Exception as e:
            print(f"[{now()}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")
            
    for token, bot in zip(HELPER, bots): loop.create_task(bot.start(token))

def farmer(loop):
    ticker = Ticker()

    def task():
        bot = commands.Bot(command_prefix = "!")
        lock = ticker.add()

        @bot.event
        async def on_ready():
            print(f"[{now()}] [INFO] - {Fore.LIGHTGREEN_EX}Logged on as {bot.user}{Style.RESET_ALL}")

        return bot
        
    bots = [task() for token in FARMER]
    if not bots: return

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
                        await _send(bots[ticker.tick()], CATCH, "<@%s> c %s" % (POKETWO, result))
                        print(f"[{now()}] [HINT] - {Fore.LIGHTGREEN_EX}Search Result: {Style.RESET_ALL}{result}")
                    else:
                        print(f"[{now()}] [ERROR] - {Fore.RED}Pokemon Not Founded In Database{Style.RESET_ALL}")

                elif content.startswith("Congratulations"):
                    match = re.search(r"Congratulations <@\d+>! (.+)", content)
                    if not match: return
                    hint = match.group(1)
                    print(f"[{now()}] [INFO] - {Fore.LIGHTGREEN_EX}{hint}{Style.RESET_ALL}")
                    for bot in bots: await _ack(bot)

                elif content.startswith("That is the wrong pokémon!"):
                    print(f"[{now()}] [INFO] - {Fore.RED}That is the wrong pokémon!{Style.RESET_ALL}")
                    
        except Exception as e:
            print(f"[{now()}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")

    for token, bot in zip(FARMER, bots): loop.create_task(bot.start(token))

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    helper(loop)
    farmer(loop)
    loop.run_forever()

if __name__ == "__main__": main()
