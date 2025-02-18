from banner import Banner
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
    open('config.json', 'r', encoding='utf-8')
)
poketwo = 716390085896962058

init()
current_datetime = datetime.datetime.now()
timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

def find_word(words, user_input):
    for word in words:
        if len(word) != len(user_input): continue
            
        for c, d in zip(word, user_input):
            if c != '_' and c != d: break
        else:
            return word

    return None

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.YELLOW, Banner.get_banner(), Style.RESET_ALL)

def helper():
    bot = commands.Bot(command_prefix='!')
    SPAWN = int(Config["spawn"])
    SPAM = Config["spam"]

    async def send_message(channel_id, message):
        try:
            channel = bot.get_channel(int(channel_id))
            await channel.send(message)
        except Exception as e:
            print(f"{Fore.RED}Error in send_message: {e}{Style.RESET_ALL}")

    @bot.event
    async def on_ready():
        print_banner()
        print(f'[{timestamp}] [INFO] - {Fore.LIGHTGREEN_EX}Logged on as {bot.user}{Style.RESET_ALL}')
        pause = False
        while True:
            if not pause:
                timer = random.uniform(1.5, 2)
                await send_message(SPAM, base64.b64encode(os.urandom(15)).decode())
                await asyncio.sleep(timer)
            else:
                await asyncio.sleep(5)
                pause = False

    @bot.event
    async def on_message(message):
        try:
            if message.channel.id == SPAWN:
                if message.author.id == int(poketwo):
                    if message.embeds:
                        embed_title = message.embeds[0].title
                        if 'wild pokémon has appeared!' in embed_title:
                            timer = random.uniform(1.5, 3)
                            await asyncio.sleep(timer)
                            await message.channel.send('<@%s> h' % poketwo)
                            pause = True

            if message.author.id == int(poketwo) and message.channel.id == SPAWN:
                if message.content.startswith('That is the wrong pokémon!'):
                    timer = random.uniform(3, 5)
                    await asyncio.sleep(timer)
                    await message.channel.send('<@%s> h' % poketwo)

        except Exception as e:
            print(f"[{timestamp}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")

    return bot

def farmer():
    bot = commands.Bot(command_prefix='!')
    SPAWN = int(Config["spawn"])
    SPAM = Config["spam"]

    async def send_message(channel_id, message):
        try:
            channel = bot.get_channel(int(channel_id))
            await channel.send(message)
        except Exception as e:
            print(f"{Fore.RED}Error in send_message: {e}{Style.RESET_ALL}")

    @bot.event
    async def on_ready():
        print_banner()
        print(f'[{timestamp}] [INFO] - {Fore.LIGHTGREEN_EX}Logged on as {bot.user}{Style.RESET_ALL}')
        return

    @bot.event
    async def on_message(message):
        try:
            if message.author.id == int(poketwo) and message.channel.id == SPAWN:
                if message.content.startswith('The pokémon is '):
                    extracted_word = message.content[len('The pokémon is '):].strip('.').strip().replace('\\', '')
                    print(f'[{timestamp}] [HINT] - {Fore.YELLOW}Pokemon Hint: {Style.RESET_ALL}{extracted_word}')
                    result = find_word(words, extracted_word)
                    if result:
                        await message.channel.send('<@%s> c %s' % (poketwo, result))
                        print(f"[{timestamp}] [HINT] - {Fore.LIGHTGREEN_EX}Search Result: {Style.RESET_ALL}{result}")
                    else:
                        print(f"[{timestamp}] [ERROR] - {Fore.RED}Pokemon Not Founded In Database{Style.RESET_ALL}")

            if message.author.id == int(poketwo) and message.channel.id == SPAWN:
                if message.content.startswith('Congratulations'):
                    match = re.search(r'Congratulations <@\d+>! (.+)', message.content)
                    if match:
                        extracted_message = match.group(1)
                        print(f'[{timestamp}] [INFO] - {Fore.LIGHTGREEN_EX}{extracted_message}{Style.RESET_ALL}')
                else:
                    print(f'[{timestamp}] [INFO] - {Fore.RED}That is the wrong pokémon!{Style.RESET_ALL}')

        except Exception as e:
            print(f"[{timestamp}] [ERROR] - {Fore.RED}Error in on_message: {Style.RESET_ALL}{e}")

    with open('pokemon.json', 'r', encoding='utf-8') as f:
        words = json.load(f)

    return bot

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(helper().start(Config["help"]))
loop.create_task(farmer().start(Config["token"]))
loop.run_forever()
