import colorama
import datetime
colorama.init(autoreset=True)
from colorama import Fore, Back
from telethon import TelegramClient, events

api_id = 000000
api_hash = ""
#These two variables can be found at https://my.telegram.org/

import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

selfbot = TelegramClient("session_id", api_id, api_hash, lang_code='ru')
selfbot.start("PHONE NUMBER", 'CLOUD PASSWORD')
#If you don't have a cloud password, just remove this field, leaving selfbot.start("PHONE NUMBER")

def log(user):
    try:
        date = datetime.datetime.now().strftime("%d.%m.%y %H:%M")
        user_name = user.first_name
        try:
            if user.last_name:
                user_name = f"{user.first_name} {user.last_name}"
        except:
            pass
        try:
            user_username = user.username
        except:
            user_username = "None"
        print(f"{Fore.CYAN}[{date}]{Fore.YELLOW} VOICE {Fore.WHITE}от {user_name} [{Fore.YELLOW}@{user_username}{Fore.WHITE}]")
    except Exception as gh:
        print(Fore.RED + "Ошибка логгирования. " + Back.WHITE + Fore.WHITE + str(gh))
    return

@selfbot.on(events.NewMessage(incoming=True))
async def my_event_handler(event):
    sender = await event.get_sender()
    try:
        if (event.chat_id > 0) and (event.message.voice != None):
            log(sender)
    except Exception as exlog:
        print(Fore.RED + "Ошибка обработки лога. " + Back.WHITE + Fore.WHITE + str(exlog))
    try:
        if event.chat_id > 0:
            if (event.message.voice) and (event.message.voice.attributes[0].duration < 10):
                await event.respond('__Пользователь ограничил функцию голосовых сообщений.__')
                await selfbot.delete_messages(event.chat_id, [event.id])
    except Exception as rf:
        print(Fore.RED + "Ошибка обработки сообщения. " + Back.WHITE + Fore.WHITE + str(rf))

selfbot.run_until_disconnected()
