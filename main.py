# main.py
from config import bot, load_extensions,TOKEN
from keep_alive import keep_alive


from snipe import *
from afk import *
from other import * 
from moderation import * 
from fun import *
from miscellous import * 
from fm import *
from socials import *
from server import *


# Charger les extensions
load_extensions()

# Démarrer le bot
if __name__ == '__main__':
    keep_alive()
    bot.run(TOKEN)