from config import * 
from mango import *

import time
import random
from datetime import timedelta

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours > 0:
        return f"{hours} hours, {minutes} minutes, {remaining_seconds} seconds"
    elif minutes > 0:
        return f"{minutes} minutes, {remaining_seconds} seconds"
    else:
        return f"{remaining_seconds} seconds"


afk_collection = db['afk']  # Collection 'afk', MongoDB la crÃ©e automatiquement si elle n'existe pas

# Charger les donnÃ©es AFK depuis MongoDB
def load_afk_data_from_mongo():
    afk_users = {}
    # Charger tous les documents de la collection
    docs = afk_collection.find()  # .find() renvoie tous les documents
    for doc in docs:
        guild_id = doc['_id']  # L'id du document est le guild_id
        afk_users[guild_id] = doc.get('users', {})
    return afk_users

# Sauvegarder les donnÃ©es AFK dans MongoDB
def save_afk_data_to_mongo(data):
    for guild_id, users in data.items():
        # InsÃ©rer ou mettre Ã  jour un document pour chaque guilde
        afk_doc = {'_id': guild_id, 'users': users}
        afk_collection.update_one({'_id': guild_id}, {'$set': afk_doc}, upsert=True)  # 'upsert' crÃ©e un document si il n'existe pas

# Initialisation des donnÃ©es AFK
afk_users = {}

@bot.event
async def on_ready():
    # Charger les donnÃ©es AFK depuis MongoDB
    global afk_users
    afk_users = load_afk_data_from_mongo()
    for guild in bot.guilds:
        if str(guild.id) not in afk_users:
            afk_users[str(guild.id)] = {}  # Si pas de donnÃ©es pour cette guilde, on l'ajoute

@bot.command(name='afk')
async def afk(ctx, *, reason: str = "AFK"):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)

    # Assurer que le dictionnaire a une sous-clÃ© pour chaque serveur
    if guild_id not in afk_users:
        afk_users[guild_id] = {}

    # VÃ©rifier si l'utilisateur est dÃ©jÃ  AFK
    if user_id in afk_users[guild_id]:
        await ctx.send(f"{ctx.author.mention} is already AFK.")
        return

    # Stocker le statut AFK, la raison et l'heure de dÃ©part pour l'utilisateur dans ce serveur
    afk_users[guild_id][user_id] = (reason, time.time())
    save_afk_data_to_mongo(afk_users)  # Sauvegarder immÃ©diatement les utilisateurs AFK dans le Gist

    embed = discord.Embed(
        description=f"💤 : {ctx.author.mention} is now AFK for the reason - **{reason}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

#triggers 

triggers_collection = db['triggers']

# Fonction pour charger les donnÃ©es du serveur depuis MongoDB
def load_server_data(guild_id):
    try:
        # RÃ©cupÃ©rer les donnÃ©es du document de la guilde
        doc = triggers_collection.find_one({"guild_id": str(guild_id)})
        
        if doc:
            return doc.get('data', {})  # Retourne les donnÃ©es sous forme de dictionnaire
        else:
            return {}  # Retourner un dictionnaire vide si aucune donnÃ©e n'existe pour cette guilde
    except Exception as e:
        print(f"Erreur lors de la rÃ©cupÃ©ration des donnÃ©es du serveur {guild_id}: {e}")
        return {}

# Fonction pour sauvegarder les donnÃ©es du serveur dans MongoDB
def save_server_data(guild_id, data):
    try:
        # Mettre Ã  jour les donnÃ©es pour le serveur spÃ©cifique
        result = triggers_collection.update_one(
            {"guild_id": str(guild_id)},  # Recherche du serveur
            {"$set": {"data": data}},  # Mise Ã  jour des donnÃ©es
            upsert=True  # CrÃ©e le document si il n'existe pas
        )
        if result.modified_count > 0:
            print(f"Les donnÃ©es du serveur {guild_id} ont Ã©tÃ© mises Ã  jour avec succÃ¨s dans MongoDB.")
        else:
            print(f"Aucune modification n'a Ã©tÃ© effectuÃ©e pour le serveur {guild_id}.")
    except Exception as e:
        print(f"Erreur lors de la mise Ã  jour des donnÃ©es du serveur {guild_id} dans MongoDB: {e}")


@bot.group(name='trigger', invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def set_trigger(ctx, phrase: str = None, *, role_name: str = None):
    current_prefix=load_prefix(ctx.guild.id)
    if not phrase or not role_name:
        def create_embed(page_title, page_description):
                    embed = discord.Embed(
                        title=page_title,
                        description=page_description,
                        color=discord.Color(0x808080)
                    )
                    embed.set_author(
                        name=f"{bot.user.name}",
                        icon_url=bot.user.avatar.url
                    )
                    embed.add_field(name="Aliases", value="N/A", inline=False)
                    embed.add_field(name="Parameters", value="channel", inline=False)
                    embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Admin**", inline=False)
                    return embed

                # Pages d'usage
        pages = [
                    {
                        "title": "Command name : trigger ",
                        "description": "Set a status trigger for assigning roles (1 role/phrase only).",
                        "usage": f"```Syntax: {current_prefix}trigger <phrase> <role>.\n"
                                f"Example: {current_prefix}trigger i love gato role.```",
                        "footer": "Page 1/3"
                    },
                    {
                        "title": "Command name: trigger remove",
                        "description": "Remove the trigger.",
                        "usage": f"```Syntax: {current_prefix}trigger remove <phrase>\n"
                                f"Example: {current_prefix}trigger remove i love gato```",
                        "footer": "Page 2/3"
                    },
                    {
                        "title": "Command name: trigger list",
                        "description": "List triggers in the server.",
                        "usage": f"```Syntax: {current_prefix}trigger list\n"
                                f"Example: {current_prefix}trigger list```",
                        "footer": "Page 3/3"
                    },
                

                ]

        async def update_embed(interaction, page_index):
                    embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
                    embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
                    embed.set_footer(text=f"{pages[page_index]['footer']} | Module: utilities.py  {current_time}")
                    await interaction.response.edit_message(embed=embed)

        buttons = await create_buttons(ctx, pages, update_embed, current_time)   

        initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
        initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
        initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: utilities.py  {current_time}")
        await ctx.send(embed=initial_embed, view=buttons)

        return

    guild_id = str(ctx.guild.id)

    # Find the role based on the name (partial match)
    role = find_role(ctx, role_name)

    if not role:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : No role found matching '{role_name}'.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Load the server data from MongoDB
    server_data = load_server_data(guild_id)

    # Save the trigger and role in the server data
    server_data['trigger'] = {
        "phrase": phrase,
        "role_id": role.id
    }
    save_server_data(guild_id, server_data)

    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Trigger set! Users with the phrase '{phrase}' in their status will receive the role '{role.name}'.",
        color=discord.Color(0x808080)
    )
    await ctx.send(embed=embed)


@set_trigger.command(name='remove')
@commands.has_permissions(administrator=True)
async def remove_trigger(ctx):
    guild_id = str(ctx.guild.id)

    # Charger les donnÃ©es du serveur depuis le Gist
    server_data = load_server_data(guild_id)

    # Si aucun trigger n'est dÃ©fini, envoyer un message
    if 'trigger' not in server_data:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : No trigger is currently set for this server.",
            color=discord.Color(0x808080)
        )
        await ctx.send(embed=embed)
        return

    # Supprimer le trigger
    server_data.pop('trigger', None)

    # Sauvegarder les donnÃ©es mises Ã  jour dans le Gist
    save_server_data(guild_id, server_data)

    embed = discord.Embed(
        description="<:approve:1297301591698706483> : Trigger removed successfully.",
        color=discord.Color(0x808080)
    )
    await ctx.send(embed=embed)


@set_trigger.command(name="list")
async def set_trigger_list(ctx):
    """Affiche la liste des triggers dÃ©finis pour le serveur."""
    guild_id = str(ctx.guild.id)

    # Charger les donnÃ©es des triggers depuis MongoDB
    server_data = load_server_data(guild_id)

    # VÃ©rifier si des triggers existent
    if not server_data:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : No triggers defined for this server.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    # Construire une liste des triggers formatÃ©s
    trigger_entries = []
    for trigger_name, trigger_data in server_data.items():
        phrase = trigger_data.get("phrase", "Unknown phrase")
        role_id = trigger_data.get("role_id")
        role_mention = f"<@&{role_id}>" if role_id else "No role assigned"
        trigger_entries.append(f" Trigger : **{phrase}** - Role: {role_mention}")

    # CrÃ©er l'embed
    embed = discord.Embed(
        description="\n".join(trigger_entries),
        color=discord.Color(0x808080)
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")

    # Envoyer l'embed
    await ctx.send(embed=embed)

#autoreact 

autoreact_collection = db['autoreact']

# Fonction pour charger les triggers depuis MongoDB
def load_triggers(guild_id):
    try:
        # Récupérer le document pour la guilde donnée
        doc = autoreact_collection.find_one({"guild_id": str(guild_id)})

        if doc:
            return doc.get('triggers', {})  # Retourner les triggers sous forme de dictionnaire
        else:
            return {}  # Retourner un dictionnaire vide si aucun trigger trouvé
    except Exception as e:
        print(f"Erreur lors de la récupération des triggers pour la guilde {guild_id}: {e}")
        return {}

# Fonction pour sauvegarder les triggers dans MongoDB
def save_triggers(guild_id, triggers):
    try:
        # Mettre à jour les triggers pour le serveur spécifique
        result = autoreact_collection.update_one(
            {"guild_id": str(guild_id)},  # Recherche du serveur
            {"$set": {"triggers": triggers}},  # Mise à jour des triggers
            upsert=True  # Crée le document si il n'existe pas
        )

        if result.modified_count > 0:
            print(f"Les triggers de la guilde {guild_id} ont été sauvegardés avec succès dans MongoDB.")
        else:
            print(f"Aucune modification n'a été effectuée pour la guilde {guild_id}.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des triggers dans MongoDB pour la guilde {guild_id}: {e}")


async def validate_emoji(ctx, emoji):
    if emoji.startswith('<:') and emoji.endswith('>'):
        emoji_id = int(emoji.split(':')[2][:-1])
        return discord.utils.get(ctx.guild.emojis, id=emoji_id) is not None
    else:
        return is_unicode_emoji(emoji)

def is_unicode_emoji(emoji):
    try:
        emoji.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


@bot.group(name='autoreact', invoke_without_command=True)
async def autoreact(ctx):
    current_prefix = load_prefix(ctx.guild.id)  # You can load the prefix for each server if necessary
    def create_embed(page_title, page_description):
            embed = discord.Embed(
                title=page_title,
                description=page_description,
                color=discord.Color(0x808080)
            )

            embed.set_author(
                name=f"{bot.user.name}",
                icon_url=bot.user.avatar.url
            )
            
            embed.add_field(name="Aliases", value="N/A", inline=False)
            embed.add_field(name="Parameters", value="N/A", inline=False)
            embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Admin**", inline=False)

            return embed

        # Pages d'usage
    pages = [
            {
                "title": "Command name: autoreact add",
                "description": "Add a reaction to a word, up to two emojis.",
                "usage": f"```Syntax: {current_prefix}autoreact add <word> <emoji> \n"
                          f"Example: {current_prefix}autoreact add gato :emoji:```",
                "footer": "Page 1/3"
            },
            {
                "title": "Command name: autoreact remove",
                "description": "Remove reaction to the word.",
                "usage": f"```Syntax: {current_prefix}autoreact remove <word> \n"
                          f"Example: {current_prefix}autoreact remove gato```",
                "footer": "Page 2/3"
            },
            {
                "title": "Command name: autoreact list",
                "description": "Lists all the trigger words and their associated reactions in the server,.",
                "usage": f"```Syntax: {current_prefix}autoreact list \n"
                          f"Example: {current_prefix}autoreact list```",
                "footer": "Page 3/3"
            },
        ]

    async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: utilities.py â€¢ {current_time}")
            await interaction.response.edit_message(embed=embed)

    buttons = await create_buttons(ctx, pages, update_embed, current_time)

    initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
    initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
    initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: utilities.py â€¢ {current_time}")

    await ctx.send(embed=initial_embed, view=buttons)

@autoreact.command(name='add')
@commands.has_permissions(administrator=True)
async def set_trigger(ctx, word: str = None, *emojis: str):
    guild_id = str(ctx.guild.id)  # ID of the server
    triggers = load_triggers(guild_id)  # Load triggers for the guild

    # If word or emojis are not provided, show the help message
    if word is None or len(emojis) == 0:
        embed = discord.Embed(
            title="Command: add",
            description='Add a reaction to a specified word.',
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )

        embed.add_field(
            name="Aliases", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="word, emojis", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="<:warn:1297301606362251406> : **Admin**", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: add <word> <emoji1> <emoji2>\nExample: add gato 🐱 ❤️```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: utilities.py · {current_time}"
        )

        await ctx.send(embed=embed)
        return

    if len(emojis) > 2:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You can only add up to 2 emojis.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Validate emojis
    invalid_emojis = []
    for emoji in emojis:
        if not await validate_emoji(ctx, emoji):
            invalid_emojis.append(emoji)

    if invalid_emojis:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : The following emoji(s) are not available on this server or are invalid: {', '.join(invalid_emojis)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # If guild doesn't have triggers yet, initialize it
    if 'triggers' not in triggers:
        triggers['triggers'] = {}

    # Add the word and emojis to the triggers
    triggers['triggers'][word] = " ".join(emojis)

    # Save the updated triggers back to MongoDB
    save_triggers(guild_id, triggers)

    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Reaction added - The word `{word}` will react with the emoji(s) {', '.join(emojis)}.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@autoreact.command(name='remove')
@commands.has_permissions(administrator=True)
async def remove_trigger(ctx, word: str = None):
    current_prefix = load_prefix(ctx.guild.id)  # Modify according to your needs for your prefix

    # Check if the word is provided
    if word is None:
        embed = discord.Embed(
            title="Command name: remove",
            description='Remove a reaction associated with a specified word.',
            color=discord.Color(0x808080)  # Dark gray color
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Bot's name
            icon_url=bot.user.avatar.url  # Bot's avatar
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # No aliases for this command
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="word",  # Parameter for this command
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:approve:1297301591698706483> : **Admin**", 
            inline=False
        )

        # Combined Syntax and Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}remove <word>\n"
                  f"Example: {current_prefix}remove gato```",
            inline=False
        )

        # Modify footer with pagination, module, and time
        embed.set_footer(
            text=f"Page 1/1 | Module: utilities.py · {current_time}"
        )

        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    triggers = load_triggers(guild_id)  # Load existing triggers from MongoDB

    # Check if the word exists in the triggers for the guild
    if 'triggers' in triggers and word in triggers['triggers']:
        del triggers['triggers'][word]  # Remove the trigger for the word
        save_triggers(guild_id, triggers)  # Save updated triggers in MongoDB
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : The reaction is no longer added to the word `{word}`.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : No trigger found for the word `{word}`.",
            color=discord.Color.red()
        )

    await ctx.send(embed=embed)

@autoreact.command(name='list')
@commands.has_permissions(administrator=True)
async def list_triggers(ctx):
    guild_id = str(ctx.guild.id)  # ID of the server
    triggers = load_triggers(guild_id)  # Load triggers for the guild

    if "triggers" not in triggers or not triggers["triggers"]:
        # If no triggers are found for the guild
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : No triggers found for this server.",
            color=discord.Color.orange()  # Orange color for no triggers
        )
        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )
        await ctx.send(embed=embed)
        return

    # Get all the triggers (word - emoji)
    trigger_entries = []
    for word, emoji in triggers["triggers"].items():
        trigger_entries.append(f"#{len(trigger_entries) + 1} {word} - {emoji}")  # Show both word and emoji

    # Pagination
    items_per_page = 6
    total_pages = (len(trigger_entries) + items_per_page - 1) // items_per_page
    current_page = 0

    # Function to create paginated embed
    async def create_embed(entries, page, items_per_page, total_pages, author):
        start = page * items_per_page
        end = start + items_per_page
        page_entries = entries[start:end]
        embed = discord.Embed(
            title="Trigger List",
            description="\n".join(page_entries),
            color=discord.Color(0x808080)
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        embed.set_footer(text=f"Page {page + 1} of {total_pages} | Module: utilities.py")
        return embed

    embed = await create_embed(trigger_entries, current_page, items_per_page, total_pages, ctx.author)
    message = await ctx.send(embed=embed)

    # Pagination buttons
    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(current_page == 0))
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(current_page == total_pages - 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def update_embed():
        embed = await create_embed(trigger_entries, current_page, items_per_page, total_pages, ctx.author)
        await message.edit(embed=embed)

    # Previous page callback
    async def previous_callback(interaction):
        if interaction.user == ctx.author:
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                await update_embed()
                previous_button.disabled = (current_page == 0)
                next_button.disabled = (current_page == total_pages - 1)
                await interaction.response.edit_message(view=buttons)
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        description="<:warn:1297301606362251406> : You are not the author of this message.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    # Next page callback
    async def next_callback(interaction):
        if interaction.user == ctx.author:
            nonlocal current_page
            if current_page < total_pages - 1:
                current_page += 1
                await update_embed()
                previous_button.disabled = (current_page == 0)
                next_button.disabled = (current_page == total_pages - 1)
                await interaction.response.edit_message(view=buttons)
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        description="<:warn:1297301606362251406> : You are not the author of this message.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    # Close button callback
    async def close_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    await message.edit(view=buttons)

#automod 

words_collection = db["words"]

@bot.group(name="automod", invoke_without_command=True)
async def automod(ctx):
    current_prefix = load_prefix(ctx.guild.id)  # You can load the prefix for each server if necessary
    def create_embed(page_title, page_description):
            embed = discord.Embed(
                title=page_title,
                description=page_description,
                color=discord.Color(0x808080)
            )

            embed.set_author(
                name=f"{bot.user.name}",
                icon_url=bot.user.avatar.url
            )
            
            embed.add_field(name="Aliases", value="N/A", inline=False)
            embed.add_field(name="Parameters", value="mute,delete", inline=False)
            embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Admin**", inline=False)

            return embed

        # Pages d'usage
    pages = [
            {
                "title": "Command name: automod addword",
                "description": "Set up an automod for a word.",
                "usage": f"```Syntax: {current_prefix}automod addword <word> <action>\n"
                          f"Example: {current_prefix}automod addword nword mute```",
                "footer": "Page 1/3"
            },
            {
                "title": "Command name: automod removeword",
                "description": "Remove a word from the blacklist.",
                "usage": f"```Syntax: {current_prefix}automod removeword <word> \n"
                          f"Example: {current_prefix}automod removeword nword```",
                "footer": "Page 2/3"
            },
            {
                "title": "Command name: automod listword",
                "description": "Command to list all blacklisted words in the guild",
                "usage": f"```Syntax: {current_prefix}automod listword \n"
                          f"Example: {current_prefix}automod listword```",
                "footer": "Page 3/3"
            },
        ]

    async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: utilities.py  {current_time}")
            await interaction.response.edit_message(embed=embed)

    buttons = await create_buttons(ctx, pages, update_embed, current_time)

    initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
    initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
    initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: utilities.py {current_time}")

    await ctx.send(embed=initial_embed, view=buttons)


@automod.command(name='addword')
@commands.has_permissions(administrator=True)
async def addword(ctx, word: str, *, actions: str = "delete"):
    guild_id = str(ctx.guild.id)
    actions_list = [action.strip() for action in actions.split(',')]

    # Validation des actions
    valid_actions = []
    for action in actions_list:
        if action.startswith("mute"):
            try:
                # Vérifie si une durée est spécifiée
                duration = action.split()[1]
                valid_actions.append(f"mute {duration}")
            except IndexError:
                # Pas de durée, mute par défaut (1h)
                valid_actions.append("mute 1h")
        elif action == "delete":
            valid_actions.append("delete")
        else:
            # Action invalide
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : Invalid action `{action}`. Supported actions: `delete`, `mute <duration>`. ",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

    # Ajoute le mot avec ses actions dans la base de données
    guild_words = db['words']
    existing_word = guild_words.find_one({"guild_id": guild_id, "word": word})

    if existing_word:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : The word `{word}` already exists with actions: {', '.join(existing_word['actions'])}.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    guild_words.insert_one({"guild_id": guild_id, "word": word, "actions": valid_actions})
    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Word `{word}` added with actions: {', '.join(valid_actions)}.",
        color=discord.Color(0x808080)
    )
    await ctx.send(embed=embed)

@automod.command(name="removeword")
async def removeword(ctx, word: str):
    guild_id = str(ctx.guild.id)

    # Suppression du mot dans MongoDB
    result = db['words'].delete_one({"guild_id": guild_id, "word": word})

    if result.deleted_count == 0:
        # Le mot n'existe pas
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : The word `{word}` does not exist in the automod configuration.",
            color=discord.Color.red()
        )
    else:
        # Le mot a été supprimé avec succès
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : The word `{word}` has been removed from automod.",
            color=discord.Color(0x808080)
        )

    # Envoi d'un seul message avec l'embed correspondant
    await ctx.send(embed=embed)

@automod.command()
async def listword(ctx):
    """Command to list all blacklisted words in the guild"""
    
    # Get the blacklisted words for the guild
    guild_id = str(ctx.guild.id)
    guild_words = db['words']
    forbidden_words = list(guild_words.find({"guild_id": guild_id}))

    # If no blacklisted words, send a message stating so
    if not forbidden_words:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : There are no blacklisted words in this guild.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    # Prepare the list of words and actions
    entries = []
    for word_entry in forbidden_words:
        word = word_entry.get('word', 'Unknown')
        actions = ', '.join(word_entry.get('actions', ['None']))
        entries.append(f"**{word}** - {actions}")

    # Pagination setup
    items_per_page = 6
    total_pages = (len(entries) + items_per_page - 1) // items_per_page
    current_page = 0

    # Function to create the embed with the current page
    async def create_embed(entries, page, items_per_page, total_pages, author):
        start = page * items_per_page
        end = start + items_per_page
        page_entries = entries[start:end]
        embed = discord.Embed(
            title="Blacklisted Words",
            description="\n".join(page_entries),
            color=discord.Color(0x808080)
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        embed.set_footer(text=f"Page {page + 1} of {total_pages} | Module: Utilities.py ")
        return embed

    # Initial embed creation
    embed = await create_embed(entries, current_page, items_per_page, total_pages, ctx.author)
    message = await ctx.send(embed=embed)

    # Pagination buttons
    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(current_page == 0))
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(current_page == total_pages - 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    # Function to update the embed on pagination
    async def update_embed():
        embed = await create_embed(entries, current_page, items_per_page, total_pages, ctx.author)
        await message.edit(embed=embed)

    # Previous page callback
    async def previous_callback(interaction):
        if interaction.user == ctx.author:
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                await update_embed()
                previous_button.disabled = (current_page == 0)
                next_button.disabled = (current_page == total_pages - 1)
                await interaction.response.edit_message(view=buttons)
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        description="<:warn:1297301606362251406> : You are not the author of this message.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    # Next page callback
    async def next_callback(interaction):
        if interaction.user == ctx.author:
            nonlocal current_page
            if current_page < total_pages - 1:
                current_page += 1
                await update_embed()
                previous_button.disabled = (current_page == 0)
                next_button.disabled = (current_page == total_pages - 1)
                await interaction.response.edit_message(view=buttons)
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        description="<:warn:1297301606362251406> : You are not the author of this message.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    # Close button callback
    async def close_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Set the button callbacks
    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    # Add the buttons to the view
    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    # Send the message with buttons
    await message.edit(view=buttons)

#----------------------------------------------------

#botevent

@bot.event
async def on_presence_update(before, after):
    guild = after.guild
    guild_id = str(guild.id)

    # Charger les donnÃ©es du serveur depuis le Gist
    server_data = load_server_data(guild_id)

    # Si aucun trigger n'est dÃ©fini pour ce serveur, sortir
    if 'trigger' not in server_data:
        return

    trigger_phrase = server_data['trigger']['phrase']
    role_id = server_data['trigger']['role_id']
    role = discord.utils.get(guild.roles, id=role_id)

    if not role:
        print(f"Role with ID {role_id} not found in guild {guild.name}.")
        return

    # VÃ©rifier si l'utilisateur est offline
    if after.status == discord.Status.offline:
        # Retirer le rÃ´le si l'utilisateur est offline
        if role in after.roles:
            await after.remove_roles(role)
            print(f"Removed role {role.name} from {after.name} (offline)")
        return

    # VÃ©rifier le statut personnalisÃ©
    custom_status = next((activity for activity in after.activities if isinstance(activity, discord.CustomActivity)), None)

    if custom_status and trigger_phrase in custom_status.name:
        # Ajouter le rÃ´le si la phrase est prÃ©sente dans le statut
        if role not in after.roles:
            await after.add_roles(role)
            print(f"Added role {role.name} to {after.name} (status contains trigger)")
    else:
        # Retirer le rÃ´le si la phrase n'est plus prÃ©sente
        if role in after.roles:
            await after.remove_roles(role)
            print(f"Removed role {role.name} from {after.name} (status doesn't contain trigger)")

@bot.event
async def on_message(message):
    
    if message.author.bot:
        return
    
    if isinstance(message.channel, discord.DMChannel):
        await handle_dm(message)  # Appelle une fonction séparée pour les DMs
        return

    guild_id = str(message.guild.id)
    user_id = str(message.author.id)

    # Charger les donnÃ©es AFK depuis le Gist pour le serveur
    if guild_id not in afk_users:
        afk_users[guild_id] = {}

    # Si l'utilisateur est AFK, on le retire et on envoie un message
    if user_id in afk_users[guild_id]:
        reason, start_time = afk_users[guild_id].pop(user_id)  # Retirer le statut AFK
        elapsed_time = round(time.time() - start_time)
        formatted_time = format_time(elapsed_time)

        # Sauvegarder immÃ©diatement dans le Gist aprÃ¨s suppression
        save_afk_data_to_mongo(afk_users)

        embed = discord.Embed(
            description=f"👋 : {message.author.mention}, you came back after **{formatted_time}**.",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)

    # VÃ©rifier si un utilisateur AFK est mentionnÃ© dans le message
    for afk_user_id, (reason, start_time) in afk_users[guild_id].items():
        user = bot.get_user(int(afk_user_id))
        if user is not None and (user in message.mentions or f'@{user.name}' in message.content):
            elapsed_time = round(time.time() - start_time)
            formatted_time = format_time(elapsed_time)

            embed = discord.Embed(
                description=f"👋 : {user.mention} is currently AFK since **{formatted_time}** ago - **{reason}**",
                color=discord.Color.orange()
            )
            await message.channel.send(embed=embed, reference=message)
            break


    if message.content.startswith(f'<@{bot.user.id}>'):
        current_prefix = load_prefix(message.guild.id)
        embed = discord.Embed(
            description=f"It's not just a call, it's a warning to them. Prefix - `{current_prefix}`.",
            color=discord.Color(0x808080)
        )
        embed.set_image(url="https://c.tenor.com/QJjJ7Oy5stoAAAAd/tenor.gif")
        await message.channel.send(embed=embed)


    guild_id = str(message.guild.id)
    triggers = load_triggers(guild_id)  

    if "triggers" in triggers:
        for word, emoji in triggers["triggers"].items():
            if word.lower() in message.content.lower():
                try:
                    await message.add_reaction(emoji)
                except discord.HTTPException:
                    embed = discord.Embed(
                        description=f"<:warn:1297301606362251406> : Unable to add reaction for `{word}`. The `{emoji}` emoji is not available on this server.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    return
                
    #automod
    
    # Load the prefix for the guild
    current_prefix = load_prefix(message.guild.id)

    # Check if the message is a command (i.e., starts with the prefix)
    if message.content.startswith(f"{current_prefix}automod removeword"):
        # Check if the user has the necessary permissions (administrator or manage_guild or manage_messages)
        if not (message.author.guild_permissions.manage_guild or
                message.author.guild_permissions.manage_messages or
                message.author.guild_permissions.administrator):
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : You don't have the required permissions to use this command.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return

        # Extract the word to remove from the command
        word_to_remove = message.content[len(f"{current_prefix}automod removeword "):].strip()

        # Retrieve the forbidden words for the guild
        guild_words = db['words']
        word_entry = guild_words.find_one({"guild_id": str(message.guild.id), "word": word_to_remove})

        if word_entry:
            guild_words.delete_one({"_id": word_entry["_id"]})
            embed = discord.Embed(
                description=f"<:approve:1297301591698706483> : The word {word_to_remove} has been removed from the forbidden words list.",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : The word {word_to_remove} was not found in the forbidden words list.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
        return  # Stop further message processing for this command

    # Process normal messages for automod functionality
    content = message.content.lower()
    guild_id = str(message.guild.id)

    # Retrieve forbidden words for the guild
    guild_words = db['words']
    forbidden_words = guild_words.find({"guild_id": guild_id})

    for word_entry in forbidden_words:
        if word_entry["word"] in content:
            actions = word_entry.get("actions", [])
            for action in actions:
                if action == "delete":
                    # Check if the author has permission to delete their message
                    if not (message.author.guild_permissions.manage_guild or
                            message.author.guild_permissions.manage_messages or
                            message.author.guild_permissions.administrator):
                        try:
                            # Only delete the message if the author does not have the required permissions
                            await message.delete()  # Delete the message
                        except Exception:
                            pass
                elif action.startswith("mute"):
                    # Apply the mute action
                    try:
                        # Duration in minutes (e.g., "mute 5m" for 5 minutes)
                        duration_str = action.split()[1]
                        duration = int(duration_str[:-1]) * 60  # Convert to seconds (if it's in minutes)

                        # Apply the timeout (mute)
                        await message.author.timeout(duration, reason="Automod: forbidden word")

                        # Send a DM to inform the user about the mute
                        try:
                            dm_embed = discord.Embed(
                                title="Muted",
                                color=0xff0000,
                                description=f"You have been muted in **{message.guild.name}**."
                            )
                            dm_embed.add_field(name="Moderator", value=message.author.mention, inline=True)
                            dm_embed.add_field(name="Reason", value="Automod: forbidden word", inline=True)
                            dm_embed.add_field(name="Duration", value=duration_str, inline=True)
                            dm_embed.set_footer(text=f"If you would like to dispute this punishment, contact a staff member. • {message.created_at.strftime('%d/%m/%Y %H:%M')}")

                            # Add server icon to the DM if available
                            if message.guild.icon:
                                dm_embed.set_thumbnail(url=message.guild.icon.url)

                            await message.author.send(embed=dm_embed)
                        except discord.Forbidden:
                            dm_embed = discord.Embed(
                                color=0xffcc00,
                                description=f"<:warn:1297301606362251406> : Could not send DM to {message.author.mention}, they might have DMs disabled."
                            )
                            await message.channel.send(embed=dm_embed)

                    except Exception:
                        pass  # Ignore any exceptions related to muting
            break  # Stop processing once the action is taken

    else:
        await bot.process_commands(message)

#handle dm 

async def handle_dm(message):
    responses = [
        "Violating my privacys bruh be serious.",
        "Ain't no way you dming me right now. Guess I'll warn ur ass.",
        "I don't care abt your life so if u can just leave my dms i would be glad.",
        "Am I gettting paid to listen to ur story or nah.",
        "Fine shii dming me gotta be crazyyy. Just take my credentials cards : 5342 3647 7382 7382 01/28 299 owner gato.",
        "Will you be my girl ? It's kinda hard being alone here.", 
        "Hello you, don't worry I'm not joe goldberg.", 
        "I'm just a chill guy.", 
        "Btw don' talk to me right now I'm self building.", 
        "I'm watching you through your windows pookie <3."
    ]
    response = random.choice(responses)
    await message.channel.send(response)

#----------------------------------------------------------------