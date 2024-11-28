from config import *



import json
from discord.ext import tasks
from cachetools import TTLCache
from datetime import datetime, timedelta


snipe_cache = TTLCache(maxsize=100, ttl=7200)
CLEANUP_INTERVAL = 120 


def create_snipe_directory(guild_id):
    base_dir = 'snipe'
    guild_dir = os.path.join(base_dir, str(guild_id))
    if not os.path.exists(guild_dir):
        os.makedirs(guild_dir)
    return guild_dir


def load_snipes(guild_id):
    guild_dir = create_snipe_directory(guild_id)
    snipe_file = os.path.join(guild_dir, 'snipes.json')
    snipes = {}

    if os.path.exists(snipe_file):
        with open(snipe_file, 'r') as f:
            snipes = json.load(f)

        
        two_hours_ago = datetime.now() - timedelta(hours=2)
        for channel_id, snipe_list in list(snipes.items()):
            snipes[channel_id] = [
                snipe for snipe in snipe_list
                if datetime.fromisoformat(snipe['timestamp']) > two_hours_ago
            ]
            
            if not snipes[channel_id]:
                del snipes[channel_id]

        save_snipes(snipes, guild_id)  

    return snipes


def save_snipes(snipes, guild_id):
    guild_dir = create_snipe_directory(guild_id)
    snipe_file = os.path.join(guild_dir, 'snipes.json')
    with open(snipe_file, 'w') as f:
        json.dump(snipes, f, indent=4)


@tasks.loop(minutes=CLEANUP_INTERVAL)
async def cleanup_expired_snipes():
    for guild in bot.guilds:
        guild_id = guild.id
        snipes = load_snipes(guild_id)  
        save_snipes(snipes, guild_id)  


@bot.event
async def on_ready():
    cleanup_expired_snipes.start()

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    guild_id = message.guild.id  
    channel_id = str(message.channel.id)  

    
    snipes = snipe_cache.get(guild_id) or load_snipes(guild_id)

    if channel_id not in snipes:
        snipes[channel_id] = []  

    
    snipes[channel_id].append({
        'content': message.content,
        'author': str(message.author.id),  
        'attachments': [att.url for att in message.attachments],  
        'stickers': [str(sticker.url) for sticker in message.stickers],  
        'timestamp': datetime.now().isoformat()  
    })

    if len(snipes[channel_id]) > 100:
        snipes[channel_id].pop(0)

    snipe_cache[guild_id] = snipes  
    save_snipes(snipes, guild_id)  


@bot.command(name='s', aliases=['snipe'])
async def snipe(ctx, index: int = 1):



    channel_id = str(ctx.channel.id)
    snipes = snipe_cache.get(ctx.guild.id) or load_snipes(ctx.guild.id)

    if channel_id not in snipes or not snipes[channel_id]:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : There are no deleted messages to display in this channel.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return

    index -= 1  # Adjusting the index for list
    if index < 0 or index >= len(snipes[channel_id]):
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Invalid snipe index.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    current_time = datetime.now().strftime('%H:%M')

    # Fonction pour créer ou mettre à jour l'embed
    async def create_embed(snipe_data):
        nonlocal index
        author = await bot.fetch_user(int(snipe_data['author']))
        embed = discord.Embed(
            description=f"**Message sniped**: {snipe_data['content']}" if snipe_data['content'] else "No content.",
            color=discord.Color(0x808080)
        )
        embed.set_author(name=author.name, icon_url=author.avatar.url if author.avatar else None)

        # Gestion des attachements
        embed.set_image(url=None)  # Réinitialise l'image de l'embed
        if snipe_data['attachments']:
            attachment_url = snipe_data['attachments'][0]
            if attachment_url.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
                embed.set_image(url=attachment_url)
            else:
                embed.add_field(name="File", value=f"Download link: {attachment_url}")

        # Gestion des stickers
        elif snipe_data['stickers']:
            embed.set_image(url=snipe_data['stickers'][0])

        embed.set_footer(text=f"Page: {index + 1}/{len(snipes[channel_id])} • Today at {current_time}")
        return embed

    # Création des boutons pour la pagination
    buttons = View(timeout=60)
    previous_button = Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(index == 0))
    next_button = Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(index == len(snipes[channel_id]) - 1))
    close_button = Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    # Fonction pour la page précédente
    async def previous_callback(interaction):
        nonlocal index
        if interaction.user.id == ctx.author.id: 
            if index > 0:
                index -= 1
                embed = await create_embed(snipes[channel_id][-(index + 1)])
                previous_button.disabled = (index == 0)
                next_button.disabled = (index == len(snipes[channel_id]) - 1)
                await interaction.response.edit_message(embed=embed, view=buttons)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Fonction pour la page suivante
    async def next_callback(interaction):
        nonlocal index
        if interaction.user.id == ctx.author.id:
            if index < len(snipes[channel_id]) - 1:
                index += 1
                embed = await create_embed(snipes[channel_id][-(index + 1)])
                previous_button.disabled = (index == 0)
                next_button.disabled = (index == len(snipes[channel_id]) - 1)
                await interaction.response.edit_message(embed=embed, view=buttons)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Fonction pour fermer le message
    async def close_callback(interaction):
        if interaction.user.id == ctx.author.id:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Assigner les callbacks aux boutons
    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    # Ajouter les boutons à la vue
    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    # Envoyer le message avec l'embed et les boutons
    embed = await create_embed(snipes[channel_id][-(index + 1)])
    await ctx.send(embed=embed, view=buttons)


editsnipes_cache = {}

EDIT_SNIPE_LIFETIME = timedelta(hours=2)


def load_editsnipes(guild_id):
    guild_dir = create_snipe_directory(guild_id)
    editsnipe_file = os.path.join(guild_dir, 'editsnipes.json')

    if os.path.exists(editsnipe_file):
        with open(editsnipe_file, 'r') as f:
            return json.load(f)
    return {}

def save_editsnipes(editsnipes, guild_id):
    guild_dir = create_snipe_directory(guild_id)
    editsnipe_file = os.path.join(guild_dir, 'editsnipes.json')

    with open(editsnipe_file, 'w') as f:
        json.dump(editsnipes, f)

def clean_editsnipes(editsnipes):
    current_time = datetime.now()
    for channel_id in list(editsnipes.keys()):
        editsnipes[channel_id] = [
            edit for edit in editsnipes[channel_id]
            if datetime.fromisoformat(edit['timestamp']) > (current_time - EDIT_SNIPE_LIFETIME)
        ]
        if not editsnipes[channel_id]:  
            del editsnipes[channel_id]
    return editsnipes


@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return

    guild_id = before.guild.id
    channel_id = str(before.channel.id)
    editsnipes = load_editsnipes(guild_id)
    editsnipes = clean_editsnipes(editsnipes)  

    if channel_id not in editsnipes:
        editsnipes[channel_id] = []

    editsnipes[channel_id].append({
        'author': str(before.author.id),
        'before': before.content,
        'after': after.content,
        'timestamp': datetime.now().isoformat()  
    })

    save_editsnipes(editsnipes, guild_id)

@bot.command(name='es', aliases=['editsnipe'])
async def editsnipe(ctx, index: int = 1):

    channel_id = str(ctx.channel.id)
    editsnipes = load_editsnipes(ctx.guild.id)
    editsnipes = clean_editsnipes(editsnipes)  

    if channel_id not in editsnipes or not editsnipes[channel_id]:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : There are no edited messages to display in this channel.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return

    index -= 1
    if index < 0 or index >= len(editsnipes[channel_id]):
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Invalid editsnipe index.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    edit_snipe = editsnipes[channel_id][-(index + 1)]
    author = await bot.fetch_user(int(edit_snipe['author']))

    embed = discord.Embed(
        description=f"**Message Before**: {edit_snipe['before']}\n\n**Message After**: {edit_snipe['after']}",
        color=discord.Color(0x808080)
    )
    embed.set_author(name=author.name, icon_url=author.avatar.url)

    current_time = datetime.now().strftime('%H:%M')
    embed.set_footer(text=f"Page: {index + 1}/{len(editsnipes[channel_id])} • Today at {current_time}")

    buttons = View(timeout=60)

    previous_button = Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(index == 0))
    next_button = Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(index == len(editsnipes[channel_id]) - 1))
    close_button = Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def previous_callback(interaction):
        if interaction.user.id == ctx.author.id:
            nonlocal index
            if index > 0:
                index -= 1
                await update_embed(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    async def next_callback(interaction):
        if interaction.user.id == ctx.author.id:
            nonlocal index
            if index < len(editsnipes[channel_id]) - 1:
                index += 1
                await update_embed(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    async def close_callback(interaction):
        if interaction.user.id == ctx.author.id:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
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

    await ctx.send(embed=embed, view=buttons)

    async def update_embed(interaction):
        edit_snipe = editsnipes[channel_id][-(index + 1)]
        author = await bot.fetch_user(int(edit_snipe['author']))

        embed.set_author(name=author.name, icon_url=author.avatar.url)
        embed.description = f"**Message Before**: {edit_snipe['before']}\n\n**Message After**: {edit_snipe['after']}"
        embed.set_footer(text=f"Page: {index + 1}/{len(editsnipes[channel_id])} • Today at {current_time}")

        previous_button.disabled = (index == 0)
        next_button.disabled = (index == len(editsnipes[channel_id]) - 1)
        await interaction.response.edit_message(embed=embed, view=buttons)

    await update_embed(None)

#clear

@bot.command(name='cs', aliases=['clearsnipe'])
@commands.has_permissions(manage_messages=True)
async def clear_snipe(ctx):
    """
    Clear the snipe and editsnipe caches for the current channel.
    """
    guild_id = str(ctx.guild.id)


    channel_id = str(ctx.channel.id)
    snipes = snipe_cache.get(guild_id) or load_snipes(guild_id)
    editsnipes = editsnipes_cache.get(guild_id) or load_editsnipes(guild_id)

    snipes_deleted = channel_id in snipes
    editsnipes_deleted = channel_id in editsnipes

    if snipes_deleted:
        del snipes[channel_id]
    if editsnipes_deleted:
        del editsnipes[channel_id]

    snipe_cache[guild_id] = snipes
    editsnipes_cache[guild_id] = editsnipes
    save_snipes(snipes, guild_id)
    save_editsnipes(editsnipes, guild_id)

    if snipes_deleted or editsnipes_deleted:
        await ctx.message.add_reaction("✅")
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : There are no snipes to delete.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)



