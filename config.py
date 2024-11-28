# config.py
import os

import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime 

from dotenv import load_dotenv
from prefix import get_prefix, register_prefix_commands,load_prefix

#send perms 
async def send_permission_error(ctx):
    embed = discord.Embed(
        description=f"<:warn:1297301606362251406> : You do not have permission to use this command.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

def has_manage_messages():
    async def predicate(ctx):
        if ctx.author.guild_permissions.manage_messages:
            return True
        else:
            embed = discord.Embed(
                title="",
                description=f"<:warn:1297301606362251406> : You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return False
    return commands.check(predicate)

#-----------------------------------------

current_time = datetime.now().strftime('%H:%M')

def find_role(ctx, role_name):
    role_name = role_name.lower()
    for role in ctx.guild.roles:
        if role_name in role.name.lower():
            return role
    return None


#time 

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    time_parts = []

    if hours > 0:
        time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0 or hours > 0:  # Si des heures sont présentes, on montre aussi les minutes même si elles sont à 0
        time_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if remaining_seconds > 0 or (hours == 0 and minutes == 0):  # Toujours afficher les secondes s'il n'y a ni heures ni minutes
        time_parts.append(f"{remaining_seconds} second{'s' if remaining_seconds > 1 else ''}")

    # Joindre toutes les parties avec des virgules
    return ", ".join(time_parts)

#------------------------------------

# Charger les variables d'environnement
load_dotenv()

# Charger le token depuis les variables d'environnement
TOKEN = os.getenv('TOKEN')

# Configurer les intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.guilds = True
intents.emojis = True
intents.voice_states = True
intents.presences = True 

# Créer l'instance du bot
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Fonction pour charger les extensions
def load_extensions():
    # Charger les extensions
    register_prefix_commands(bot)

#buttons 

async def create_buttons(ctx, pages, update_embed, current_time):
    buttons = View(timeout=60)
    index = 0

    previous_button = Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary)
    next_button = Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary)
    close_button = Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    # Callback pour le bouton précédent
    async def previous_callback(interaction):
        nonlocal index
        if interaction.user.id == ctx.author.id:
            # Si on est à la première page, on boucle à la dernière
            index = (index - 1) % len(pages)  # Utilisation du modulo pour boucler
            await update_embed(interaction, index)
            await interaction.message.edit(view=buttons)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Callback pour le bouton suivant
    async def next_callback(interaction):
        nonlocal index
        if interaction.user.id == ctx.author.id:
            # Si on est à la dernière page, on boucle à la première
            index = (index + 1) % len(pages)  # Utilisation du modulo pour boucler
            await update_embed(interaction, index)
            await interaction.message.edit(view=buttons)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Callback pour fermer l'embed
    async def close_callback(interaction):
        if interaction.user.id == ctx.author.id:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Attacher les callbacks aux boutons
    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    return buttons
