from config import *
from mango import *
from fm import *

import asyncio
from datetime import timedelta
from discord.utils import format_dt


from moderation import role, find_role, format_time 
from fmconfig import get_lastfm_current_track, get_user_track_playcount


temprole_collection = db["temprole"] 

#role command 

@role.command(name="temp")
async def role_temp(ctx, member: discord.Member, time: str, *, roles: str):
    """Attribue temporairement un rôle à un utilisateur pour un temps donné."""
    
    # Convertir le temps en secondes
    time_in_seconds = 0
    if time.endswith("s"):
        time_in_seconds = int(time[:-1])  # Retirer 's' et convertir en int
    elif time.endswith("m"):
        time_in_seconds = int(time[:-1]) * 60  # Multiplier par 60 pour minutes
    elif time.endswith("h"):
        time_in_seconds = int(time[:-1]) * 3600  # Multiplier par 3600 pour heures
    elif time.endswith("d"):
        time_in_seconds = int(time[:-1]) * 86400  # Multiplier par 86400 pour jours
    else:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : Invalid time format. Please use seconds (s), minutes (m), hours (h), or days (d).",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Vérifier si le temps dépasse 28 jours
    max_seconds = 28 * 86400  # 28 jours en secondes
    if time_in_seconds > max_seconds:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : The maximum allowed duration is 28 days.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Vérifier les rôles et les attribuer
    role_names = [role.strip() for role in roles.split(',')]  # Divise les rôles séparés par une virgule
    roles_to_add = []

    for role_name in role_names:
        role = find_role(ctx, role_name)  # Cherche le rôle via la fonction find_role
        if role:
            roles_to_add.append(role)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : Role '{role_name}' not found or no match found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_error)
            return

    # Ajouter les rôles à l'utilisateur
    for role in roles_to_add:
        await member.add_roles(role)

    # Enregistrer l'information du rôle temporaire dans MongoDB
    expiration_time = datetime.utcnow() + timedelta(seconds=time_in_seconds)
    guild_id = str(ctx.guild.id)
    data = {
        "guild_id": guild_id,
        "user_id": str(member.id),
        "roles": [role.name for role in roles_to_add],
        "expiration": expiration_time.isoformat()  # Stockage en format ISO
    }
    
    # Ajouter à la collection temprole ou mettre à jour s'il existe déjà
    temprole_collection.update_one(
        {"guild_id": guild_id, "user_id": str(member.id)},
        {"$set": data},
        upsert=True
    )

    # Création de l'embed de confirmation
    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : {member.mention} has been given the role(s): {', '.join([role.name for role in roles_to_add])} for {format_time(time_in_seconds)}.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

    # Retirer les rôles après le délai spécifié
    await asyncio.sleep(time_in_seconds)

    # Retirer les rôles de l'utilisateur
    for role in roles_to_add:
        await member.remove_roles(role)

    # Supprimer les données de la base de données après la suppression des rôles
    temprole_collection.delete_one({"guild_id": guild_id, "user_id": str(member.id)})


@role.command(name="templist")
async def role_templist(ctx):
    """Affiche tous les rôles temporaires actifs dans le serveur avec un système de pagination."""
    guild_id = str(ctx.guild.id)

    try:
        # Récupérer tous les rôles temporaires pour le serveur actuel
        active_roles = list(temprole_collection.find({"guild_id": guild_id}))

        if not active_roles:
            embed = discord.Embed(
                description="<:warn:1297301606362251406> : No active temporary roles in this server.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        # Préparer les données des rôles temporaires
        role_entries = []
        for role_data in active_roles:
            user_id = int(role_data["user_id"])
            user = ctx.guild.get_member(user_id)
            roles = role_data["roles"]

            expiration_time = datetime.fromisoformat(role_data["expiration"])
            current_utc = datetime.utcnow()

            # Calculer le temps restant
            remaining_time = expiration_time - current_utc
            remaining_seconds = remaining_time.total_seconds()

            if remaining_seconds > 0:
                if remaining_seconds < 60:
                    expiration_str = f"{int(remaining_seconds)} seconds"
                elif remaining_seconds < 3600:
                    expiration_str = f"{int(remaining_seconds // 60)} minutes"
                elif remaining_seconds < 86400:
                    expiration_str = f"{int(remaining_seconds // 3600)} hours"
                else:
                    expiration_str = f"{int(remaining_seconds // 86400)} days"
            else:
                expiration_str = "**Expired**"

            if user:
                role_entries.append(
                    f"**{user.mention}** - Roles: {', '.join(roles)} - Expires in {expiration_str}"
                )
            else:
                role_entries.append(
                    f"**[Unknown User ID: {user_id}]** - Roles: {', '.join(roles)} - Expires in {expiration_str}"
                )

        # Pagination
        items_per_page = 6
        total_pages = (len(role_entries) + items_per_page - 1) // items_per_page
        current_page = 0

        # Fonction pour créer un embed paginé
        async def create_embed(entries, page, items_per_page, total_pages, author):
            start = page * items_per_page
            end = start + items_per_page
            page_entries = entries[start:end]
            embed = discord.Embed(
                title=f"Temporary Roles",
                description="\n".join(page_entries),
                color=discord.Color(0x808080)
            )
            embed.set_author(name=author.display_name, icon_url=author.avatar.url)
            embed.set_footer(text=f"Page {page + 1} of {total_pages} | Module: moderation.py")
            return embed

        embed = await create_embed(role_entries, current_page, items_per_page, total_pages, ctx.author)
        message = await ctx.send(embed=embed)

        # Configuration des boutons
        buttons = discord.ui.View(timeout=60)

        previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(current_page == 0))
        next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(current_page == total_pages - 1))
        close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

        async def update_embed():
            embed = await create_embed(role_entries, current_page, items_per_page, total_pages, ctx.author)
            await message.edit(embed=embed)

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

    except Exception as e:
        # Gestion des erreurs
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


#server 

#whois 

@bot.command(name='whois', aliases=['ui'])
async def whois(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        embed = discord.Embed(
            title="Command name : whois",
            description="Display all information about a user.",
            color=discord.Color(0x808080)
        )
        embed.set_author(name=f"{bot.user.name}", icon_url=bot.user.avatar.url)
        embed.add_field(name="Aliases", value="ui", inline=False)
        embed.add_field(name="Parameters", value="member", inline=False)
        embed.add_field(name="Permissions", value="N/A", inline=False)
        embed.add_field(
            name="Usage",
            value=f"```Syntax: {current_prefix}whois <member>\nExample: {current_prefix}whois @User```",
            inline=False
        )
        embed.set_footer(text=f"Page 1/1 | Module: server.py · {ctx.message.created_at.strftime('%H:%M')}")

        await ctx.send(embed=embed)
        return

    try:
        # Charger dynamiquement les utilisateurs Last.fm en fonction de la guilde actuelle
        lastfm_users = await load_lastfm_users(str(ctx.guild.id))  # Charger les utilisateurs pour cette guilde

        username = f"{member.name}#{member.discriminator}"
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        created_at = format_dt(member.created_at, style='F')
        joined_at = format_dt(member.joined_at, style='F')

        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        roles.reverse()
        roles_text = (
            ", ".join(roles[:5]) + f" and {len(roles) - 5} other role{'s' if len(roles) - 5 > 1 else ''}"
            if len(roles) > 5 else ", ".join(roles) if roles else "No roles assigned."
        )

        hypersquad_badges = []
        if member.public_flags.hypesquad_balance:
            hypersquad_badges.append(f"<:hypersquad_balance:1309629638170906716>")
        if member.public_flags.hypesquad_bravery:
            hypersquad_badges.append(f"<:hypersquad_bravery:1309629557048868925>")
        if member.public_flags.hypesquad_brilliance:
            hypersquad_badges.append(f"<:hypersquad_brilliance:1309629325951242250>")

        badges = []
        if hypersquad_badges:
            badges.append(" ".join(hypersquad_badges))
        
        if member.premium_since:
            badges.append(f"<:nitro_subscriber:1309629955315073196>")

        boost_since = None
        if member.premium_since:
            boost_since = format_dt(member.premium_since, style='F')
            badges.append(f"<:boostlvl_2:1309634425180520448>")

        embed = discord.Embed(title=f"Information on {username}", color=discord.Color(0x808080))
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=avatar_url)

        if badges:
            embed.add_field(name="", value=" ".join(badges), inline=False)

        user_id = str(member.id)
        if user_id in lastfm_users:  # Vérifie si l'utilisateur a un compte Last.fm lié pour cette guilde
            lastfm_username = lastfm_users[user_id]
            track_info = await get_lastfm_current_track(lastfm_username)  # Récupère la chanson actuelle
            if track_info:
                artist = track_info['artist']
                title = track_info['title']
                playcount = await get_user_track_playcount(lastfm_username, artist, title)  # Récupère le playcount
                embed.add_field(
                    name="<:lastfm_iconicons:1303143391533469786>",
                    value=(
                        f"Listening to **[{title}](https://www.last.fm/music/{urllib.parse.quote(artist)}/_/{urllib.parse.quote(title)})** by **[{artist}](https://www.last.fm/music/{urllib.parse.quote(artist)})**\n"
                    ),
                    inline=False
                )
            else:
                embed.add_field(
                    name="Last.fm",
                    value=f"[Last.fm profile](https://www.last.fm/user/{lastfm_username})",
                    inline=False
                )

        embed.set_footer(text=f"User ID: {member.id}")
        embed.add_field(name="Account creation date", value=created_at, inline=False)
        embed.add_field(name="Joined the server on", value=joined_at, inline=False)
        embed.add_field(name=f"Roles{[len(roles)]}", value=roles_text, inline=False)


        if boost_since:
            embed.add_field(name="Boosted the server since", value=boost_since, inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        embed_error = discord.Embed(
            description=f"<:warn:1297301606362251406> : {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)

#rs command 

@bot.command(name="rs", aliases=["reactions"])
async def rs(ctx):
    channel = ctx.channel
    try:
        messages = [message async for message in channel.history(limit=50)]
    except Exception as e:
        await ctx.send(f"Error fetching message history: {e}")
        return

    reactions_summary = []
    for message in messages:
        for reaction in message.reactions:
            try:
                users = [user async for user in reaction.users()]
                for user in users:
                    reactions_summary.append({
                        "user": user,
                        "emoji": reaction.emoji,
                        "message": message
                    })
            except Exception as e:
                return 

    if not reactions_summary:
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : No one has reacted with any emoji in this channel.",
            color=discord.Color.red()
        ))
        return

    # Trier par la réaction la plus récente
    reactions_summary.sort(key=lambda x: x["message"].created_at, reverse=True)

    # Pagination : 1 item par page
    pages = reactions_summary
    current_page = 0

    def create_embed(page_index):
        entry = pages[page_index]
        user = entry["user"]
        emoji = entry["emoji"]
        message = entry["message"]

        embed = discord.Embed(
            description=f"{user.mention} reacted with ``{emoji}`` **[here]({message.jump_url})**",
            color=discord.Color(0x808080)
        )
        embed.set_footer(text=f"Page {page_index + 1}/{len(pages)} | {len(pages)} total reactions")
        return embed

    async def update_embed(interaction, page_index):
        embed = create_embed(page_index)
        await interaction.response.edit_message(embed=embed)

    # Boutons pour naviguer
    buttons = discord.ui.View(timeout=60)
    
    previous_button = Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary)
    next_button = Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary)
    close_button = Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def previous_callback(interaction):
        nonlocal current_page  # Utilise la variable définie globalement
        if interaction.user.id == ctx.author.id:
            # Si on est à la première page, on boucle à la dernière
            current_page = (current_page - 1) % len(pages)  # Utilise current_page au lieu d'index
            await update_embed(interaction, current_page)
            await interaction.message.edit(view=buttons)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    async def next_callback(interaction):
        nonlocal current_page
        if interaction.user.id == ctx.author.id:
            # Si on est à la dernière page, on boucle à la première
            current_page = (current_page + 1) % len(pages)  # Utilisation du modulo pour boucler
            await update_embed(interaction, current_page)
            await interaction.message.edit(view=buttons)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
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

    # Envoi initial
    embed = create_embed(current_page)
    await ctx.send(embed=embed, view=buttons)


@bot.command(name="seen")
async def seen(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)

    # Si aucun membre n'est mentionné, afficher la notice
    if not member:
        embed = discord.Embed(
            title="Command name: seen",
            description="Check the last time a user was active in the server.",
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(name=f"{bot.user.name}", icon_url=bot.user.avatar.url)

        embed.add_field(name="Aliases", value="N/A", inline=False)

        embed.add_field(name="Parameters", value="member", inline=False)

        embed.add_field(name="Permissions", value="N/A", inline=False)

        embed.add_field(
            name="Usage",
            value=f"```Syntax: {current_prefix}seen <member>\nExample: {current_prefix}seen @User```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Recherche de l'activité du membre
    last_message = None
    async for message in ctx.channel.history(limit=300):  # Parcours des 100 derniers messages
        if message.author == member:
            last_message = message
            break

    # Si aucun message n'est trouvé
    if not last_message:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} has not been seen recently in this channel.",
            color=discord.Color(0x808080)
        )
        embed.set_footer(
            text=f"Requested by {ctx.author} • {ctx.message.created_at.strftime('%H:%M')}"
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        description=f"{ctx.author.mention} : {member.mention} was last seen in this channel {format_dt(last_message.created_at, style='R')}, **[here]({last_message.jump_url})**",
        color=discord.Color(0x808080)
    )
    await ctx.send(embed=embed)


command_status = db["command_status"]

@bot.group(name="command", invoke_without_command=True)
async def command(ctx):
    """
    Affiche une notice si la commande principale est utilisée sans sous-commande.
    """
    current_prefix = load_prefix(ctx.guild.id)

    #
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
                "title": "Command name: command enable",
                "description": "Enable a specific command for the guild, including its aliases",
                "usage": f"```Syntax: {current_prefix}command enable <command name> \n"
                          f"Example: {current_prefix}command enable warn```",
                "footer": "Page 1/2"
            },
            {
                "title": "Command name: command disable",
                "description": "Disable a specific command for the guild, including its aliases.",
                "usage": f"```Syntax: {current_prefix}command disable <command name> \n"
                          f"Example: {current_prefix}command disable warn```",
                "footer": "Page 2/2"
            },
        ]

    async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: utilities.py • {current_time}")
            await interaction.response.edit_message(embed=embed)

    buttons = await create_buttons(ctx, pages, update_embed, current_time)

    initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
    initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
    initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: utilities.py • {current_time}")

    await ctx.send(embed=initial_embed, view=buttons)


@command.command(name="enable")
@commands.has_permissions(administrator=True)
async def command_enable(ctx, command_name: str = None):
    """
    Enable a specific command for the guild, including its aliases.
    This removes the command from the database to free space.
    """
    if not command_name:
        await ctx.send(embed=discord.Embed(
            description="<:warn:1297301606362251406> : Please specify the command you want to enable.",
            color=discord.Color.orange()
        ))
        return

    # Check if the command exists
    cmd = bot.get_command(command_name)
    if not cmd:
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : The command `{command_name}` does not exist. Please check the syntax.",
            color=discord.Color.orange()
        ))
        return

    guild_id = str(ctx.guild.id)
    command_name_main = cmd.name
    command_aliases = cmd.aliases

    # Fetch guild's command settings
    guild_settings = command_status.find_one({"_id": guild_id}) or {"_id": guild_id, "commands": {}}

    # Check if the command is already enabled
    command_data = guild_settings["commands"].get(command_name_main, {})
    if command_data.get("enabled", True):  # Default is enabled
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : The command `{command_name_main}` is already enabled.",
            color=discord.Color.orange()
        ))
        return

    # Enable the command and update aliases (command reappears)
    guild_settings["commands"][command_name_main] = {"enabled": True, "aliases": command_aliases}
    command_status.update_one(
        {"_id": guild_id},
        {"$set": {"commands": guild_settings["commands"]}},
        upsert=True
    )

    # Delete the command from the database to free space (it will be automatically re-added as enabled)
    command_status.update_one(
        {"_id": guild_id},
        {"$unset": {f"commands.{command_name_main}": ""}},
    )

    await ctx.send(embed=discord.Embed(
        description=f"<:approve:1297301591698706483> : The command `{command_name_main}` has been enabled.",
        color=discord.Color.green()
    ))


@command.command(name="disable")
@commands.has_permissions(administrator=True)
async def command_disable(ctx, command_name: str = None):
    """
    Disable a specific command for the guild, including its aliases.
    This adds the command to the database to track its disabled state.
    """
    if not command_name:
        await ctx.send(embed=discord.Embed(
            description="<:warn:1297301606362251406> : Please specify the command you want to disable.",
            color=discord.Color.orange()
        ))
        return

    # Check if the command exists
    cmd = bot.get_command(command_name)
    if not cmd:
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : The command `{command_name}` does not exist. Please check the syntax.",
            color=discord.Color.orange()
        ))
        return

    guild_id = str(ctx.guild.id)
    command_name_main = cmd.name
    command_aliases = cmd.aliases

    # Fetch guild's command settings
    guild_settings = command_status.find_one({"_id": guild_id}) or {"_id": guild_id, "commands": {}}

    # Check if the command is already disabled
    command_data = guild_settings["commands"].get(command_name_main, {})
    if not command_data.get("enabled", True):  # Default is enabled
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : The command `{command_name_main}` is already disabled.",
            color=discord.Color.orange()
        ))
        return

    # Disable the command and update aliases
    guild_settings["commands"][command_name_main] = {"enabled": False, "aliases": command_aliases}
    command_status.update_one(
        {"_id": guild_id},
        {"$set": {"commands": guild_settings["commands"]}},
        upsert=True
    )

    await ctx.send(embed=discord.Embed(
        description=f"<:approve:1297301591698706483> : The command `{command_name_main}` has been disabled.",
        color=discord.Color.green()
    ))