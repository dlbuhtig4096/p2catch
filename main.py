
import os, json, base64, random, re, datetime, asyncio
from discord.ext import commands
from colorama import Fore, Style, init
import requests
import numpy as np
import cv2

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
CATCH = set(Config["catch"])
CHAT = set(Config["chat"])
FARMER = Config["farmers"]
HELPER = Config["helpers"]
PLAYER = Config["players"]
ASSIST = Config["assist"]

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

def evsolve(url):
    img = cv2.imdecode(
        np.frombuffer(requests.get(url).content, np.uint8),
        cv2.IMREAD_UNCHANGED
    )
    if img is None: return "ABCD"

    h, w, c = img.shape
    x = w >> 1
    y = h >> 1
    T = {
        "A": (
            max(img[ :y,   0, 3]),
            max(img[  0,  :x, 3]),
            max(img[ :y, x-1, 3]),
            max(img[y-1,  :x, 3])
        ),
        "B": (
            max(img[ :y,   x, 3]),
            max(img[  0,  x:, 3]),
            max(img[ :y, w-1, 3]),
            max(img[y-1,  x:, 3])
        ),
        "C": (
            max(img[ y:,   0, 3]),
            max(img[  y,  :x, 3]),
            max(img[ y:, x-1, 3]),
            max(img[h-1,  :x, 3])
        ),
        "D": (
            max(img[ y:,   x, 3]),
            max(img[ y,   x:, 3]),
            max(img[ y:, w-1, 3]),
            max(img[h-1,  x:, 3])
        )
    }
    R = []
    for a, b in [[0, 1], [1, 2], [0, 3], [2, 3]]:
        m = 256
        M = ""
        for k, v in T.items():
            n = max(v[a], v[b])
            if m < n: continue
            m = n
            M = k
        del T[M]
        R.append(M)
    ans = "".join(R)
    print(f"[{now()}] [INFO] - {Fore.YELLOW}Prdiction for ({h}, {w}, {c}) {url}: {ans}{Style.RESET_ALL}")
    return ans

async def channel_send(bot, channel_id, message):
    try:
        await bot.get_channel(channel_id).send(message)
    except Exception as e:
        print(f"[{now()}] [ERROR] - {Fore.RED}Error in channel_send: {e}{Style.RESET_ALL}")

async def guild_ack(bot, guild):
    try:
        await bot.get_guild(guild).ack()
    except Exception as e:
        print(f"[{now()}] [ERROR] - {Fore.RED}Error in ack: {e}{Style.RESET_ALL}")

def farmer(bots):
    if not bots: return ()
    
    wait = 3.0 / (len(bots) + 1.0)
    def proc(channel):
        async def main():
            for bot in repeat(bots):
                await asyncio.sleep(wait)
                await channel_send(bot, channel, base64.b64encode(os.urandom(15)).decode())
        return main
    
    return (proc(channel) for channel in CHAT)

def helper(bots):
    if not bots: return ()
    chain = repeat(bots)

    wild = {channel: False for channel in CATCH}
    hint = {channel: False for channel in CATCH}
    if ASSIST:
        wait = {channel: False for channel in CATCH}
        def proc(channel):
            async def main():
                nonlocal wait
                while True:
                    await asyncio.sleep(5.0)
                    if not wild[channel]: continue
                    if wait[channel]:
                        wait[channel] = False
                        continue
                    await channel_send(next(chain), channel, "<@%s> h" % POKETWO)
            return main
        
        @(bots[0]).event
        async def on_message(message):
            nonlocal wild, wait, hint
            try:
                channel = message.channel.id
                if channel not in CATCH: return
                if message.author.id == POKETWO:
                    if message.embeds and message.embeds[0].title.endswith("wild pokémon has appeared!"):
                        hint[channel] = False
                        wait[channel] = True
                        wild[channel] = True

                    elif message.content.startswith("The pokémon is "):
                        hint[channel] = True

                    elif message.content.startswith("Congratulations") and hint[channel]:
                        wild[channel] = False                    

                elif message.author.id == ASSIST:
                    hint[channel] = True

            except Exception as e:
                print(f"[{now()}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")

    else:
        def proc(channel):
            async def main():
                while True:
                    await asyncio.sleep(3.5)
                    if wild[channel]: await channel_send(next(chain), channel, "<@%s> h" % POKETWO)
            return main

        @(bots[0]).event
        async def on_message(message):
            nonlocal wild, hint
            try:
                channel = message.channel.id
                if channel not in CATCH: return

                if message.author.id != POKETWO: return
                if message.embeds and message.embeds[0].title.endswith("wild pokémon has appeared!"):
                    hint[channel] = False
                    wild[channel] = True
                    await channel_send(next(chain), channel, "<@%s> h" % POKETWO)

                elif message.content.startswith("The pokémon is "):
                    hint[channel] = True

                elif message.content.startswith("Congratulations") and hint[channel]:
                    wild[channel] = False

            except Exception as e:
                print(f"[{now()}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")
            
    return (proc(channel) for channel in CATCH)

def player(bots):
    if not bots: return ()
    chain = repeat(bots)

    got = {channel: None for channel in CATCH}

    @(bots[0]).event
    async def on_message(message):
        try:
            channel = message.channel.id
            if channel not in CATCH: return
            
            if message.author.id == POKETWO:
                content = message.content
                
                if content.startswith("The pokémon is "):
                    hint = content[15 : -1].strip().replace("\\", "")
                    print(f"[{now()}] [HINT] - {Fore.YELLOW}Pokemon Hint: {Style.RESET_ALL}{hint}")
                    result = Pokemon.find(hint)
                    if result:
                        bot = next(chain)
                        got[channel] = bot
                        await channel_send(bot, channel, "<@%s> c %s" % (POKETWO, result))
                        print(f"[{now()}] [HINT] - {Fore.LIGHTGREEN_EX}Search Result: {Style.RESET_ALL}{result}")
                    else:
                        print(f"[{now()}] [ERROR] - {Fore.RED}Pokemon Not Founded In Database{Style.RESET_ALL}")
                    
                elif content.startswith("Congratulations"):
                    match = re.search(r"Congratulations <@\d+>! (.+)", content)
                    if not match: return
                    hint = match.group(1)
                    print(f"[{now()}] [INFO] - {Fore.LIGHTGREEN_EX}{hint}{Style.RESET_ALL}")
                    await guild_ack(got[channel], message.guild.id)

                elif content.startswith("That is the wrong pokémon!"):
                    print(f"[{now()}] [INFO] - {Fore.RED}That is the wrong pokémon!{Style.RESET_ALL}")

                elif message.embeds and message.embeds[0].title.endswith("This pokémon appears to be glitched!"):
                    await channel_send(got[channel], channel, "<@%s> afd fix %s" % (POKETWO, evsolve(message.embeds[0].image.url)))
            
            if message.author.id == ASSIST:
                content = message.content

                if content.endswith("%"):
                    bot = next(chain)
                    got[channel] = bot
                    await channel_send(bot, channel, "<@%s> c %s" % (POKETWO, content.split(": ")[0]))

                elif content.startswith("##"):
                    bot = next(chain)
                    got[channel] = bot
                    if content.startswith("## <:"):
                        await channel_send(bot, channel, "<@%s> c %s" % (POKETWO, content[3:].split("> ")[-1].split("【")[0]))
                    else:
                        await channel_send(bot, channel, "<@%s> c %s" % (POKETWO, content[3:].split(" <:")[0]))

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
