from config import *
from googledata import *

from datetime import timedelta 
from discord.utils import utcnow

#MODERATION

#PURGE 
@bot.command(name='purge')
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: str = None):
    current_prefix = load_prefix(ctx.guild.id)
    
    if amount is None:
        embed = discord.Embed(
            title=f"Command name : purge",
            description='Delete a certain number of messages in a channel. Can delete all up to 200.',  # Nom du bot dans le titre
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot dans l'auteur
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="clear", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:warn:1297301606362251406> : **Manage Messages**", 
            inline=False
        )

        # Bloc combiné pour Syntax et Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}purge <number|all>\n"
                  f"Example: {current_prefix}purge 10```",
            inline=False
        )

        # Modification du footer avec le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: moderation.py ·  {utcnow().strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)



    if amount.lower() == "all":
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : This will delete **all** the messages in the channel. Will you continue? (yes/no)",
            color=discord.Color.orange()
)
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

        try:
            response = await bot.wait_for("message", check=check, timeout=30)
            if response.content.lower() == "no":
                embed = discord.Embed(
                    description=f"<:warn:1297301606362251406> : **Purge canceled**, You have canceled message purging.",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed, delete_after=10)
                return
            elif response.content.lower() == "yes":
                await ctx.channel.purge()
                embed = discord.Embed(
                    description=f"<:approve:1297301591698706483> : **Purge successful**, All messages in the salon have been deleted by {ctx.author.mention}.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed, delete_after=10)
                return
        except TimeoutError:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : **Purge cancelled**, Response time has expired. Please try again.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=10)
            return

    try:
        amount = int(amount)
        if amount <= 0:
            embed = discord.Embed(
                description="<:warn:1297301606362251406> :  The number of messages to be deleted must be greater than zero.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 pour inclure la commande elle-même
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : **Purge successful**, {len(deleted) - 1} messages have been deleted by {ctx.author.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=10)  # Supprime l'embed après 10 secondes

    except ValueError:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : **Syntax error**, please specify a valid number or 'all' to delete all. Example: `{current_prefix}purge 10` or `{current_prefix}purge all`. ",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Gestion des erreurs de permission pour la commande purge
@purge.error
async def purge_error(ctx, error):
    current_prefix = load_prefix(ctx.guild.id)
    if isinstance(error, commands.MissingPermissions):
        await send_permission_error(ctx)  # Appel de la fonction ici
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : **Syntax error**, please specify the number of messages to delete or use 'all' to delete all. Example: `{current_prefix}purge 10` or `purge all`. ",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)


#JAIL SYSTEM

def load_jail_data(guild_id):
    doc_ref = db.collection("jail_data").document(str(guild_id))
    doc = doc_ref.get()
    
    if doc.exists:
        # Retourne les données existantes si le document est présent
        return doc.to_dict()
    else:
        # Initialisation des données de jail pour une nouvelle guilde
        initial_data = {"jailed_members": [], "jail_roles": {}}
        doc_ref.set(initial_data)
        return initial_data

# Fonction pour sauvegarder les données de jail dans le document de la guilde
def save_jail_data(guild_id, data):
    doc_ref = db.collection("jail_data").document(str(guild_id))
    doc_ref.set(data)


@bot.command(name='setjail')
@commands.has_permissions(administrator=True)
async def set_jail(ctx):
    current_prefix = load_prefix(ctx.guild.id)
    jail_role = discord.utils.get(ctx.guild.roles, name="jail")
    jail_channel = discord.utils.get(ctx.guild.text_channels, name="jail")

    if jail_role is not None and jail_channel is not None:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : The jail has already been configured. A jail role and a jail room already exist.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if jail_role is None:
        jail_role = await ctx.guild.create_role(name="jail", reason="Role created for members in jail", hoist=True)

    category = await ctx.guild.create_category("000", reason="Category for jail channel")

    if jail_channel is None:
        jail_channel = await ctx.guild.create_text_channel("jail", category=category, reason="Channel for members in jail")

        await jail_channel.set_permissions(ctx.guild.default_role, read_messages=False)
        await jail_channel.set_permissions(jail_role, read_messages=True, send_messages=True)

        for channel in ctx.guild.channels:
            if channel != jail_channel:
                await channel.set_permissions(jail_role, read_messages=False)

        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : The '{jail_role.name}' role and the '{jail_channel.name}' channel have been created in the '000' category.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : The `jail` role already exists, but the channel has not been created. You can continue to use `{current_prefix}jail`. ",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await send_permission_error(ctx)

@bot.command(name='jail')
@commands.has_permissions(manage_roles=True)
async def jail_member(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if member is None:
            # Fonction pour créer l'embed principal
            def create_embed(page_title):
                embed = discord.Embed(
                    title=page_title,
                    color=discord.Color(0x808080)
                )

                embed.set_author(
                    name=f"{bot.user.name}",
                    icon_url=bot.user.avatar.url   
                )

                embed.add_field(name="Aliases", value="N/A", inline=False)
                embed.add_field(name="Parameters", value="member, reason, time", inline=False)
                embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Manage_Roles**", inline=False)

                return embed

            # Pages d'usage
            pages = [
                {
                    "title": "Command name: jail",
                    "usage": f"```Syntax: {load_prefix(ctx.guild.id)}jail <member> [reason]\n"
                              f"Example: {load_prefix(ctx.guild.id)}jail @User spam```",
                    "footer": "Page 1/3"
                },
                {
                    "title": "Command name: unjail",
                    "usage": f"```Syntax: {load_prefix(ctx.guild.id)}unjail <member> [reason] \n"
                              f"Example: {load_prefix(ctx.guild.id)}unjail @User behave```",
                    "footer": "Page 2/3"
                },
                {
                    "title": "Command name: setjail",
                    "usage": f"```Syntax: {load_prefix(ctx.guild.id)}setjail\n"
                              f"Example: {load_prefix(ctx.guild.id)}setjail```",
                    "footer": "Page 3/3"
                },
            ]

            # Fonction pour changer d'embed
            async def update_embed(interaction, page_index):
                embed = create_embed(pages[page_index]["title"])  # Met à jour le titre
                embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
                embed.set_footer(text=f"{pages[page_index]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
                await interaction.response.edit_message(embed=embed)

            buttons = await create_buttons(ctx, pages, update_embed, current_time)

            # Envoi de l'embed initial
            initial_embed = create_embed(pages[0]["title"])
            initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
            initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
            await ctx.send(embed=initial_embed, view=buttons)
            return

    # Vérifie si l'utilisateur tente de se jail lui-même
    if member.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(color=0xffcc00, description="<:warn:1297301606362251406> : You can't jail yourself."))
        return

    # Vérifie si l'utilisateur a un rôle supérieur à celui du membre ciblé
    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
        await ctx.send(embed=discord.Embed(color=0xffcc00, description=f"<:warn:1297301606362251406> : You cannot jail {member.mention} because their role is higher or equal to yours."))
        return

    # Trouve le rôle "jail" et vérifie son existence
    jail_role = discord.utils.get(ctx.guild.roles, name="jail")
    if jail_role is None:
        await ctx.send(embed=discord.Embed(color=0xffcc00, description="<:warn:1297301606362251406> : Jail role not found. Please create it first."))
        return

    # Vérifie si le salon 'jail' existe
    jail_channel = discord.utils.get(ctx.guild.text_channels, name="jail")
    if jail_channel is None:
        await ctx.send(embed=discord.Embed(color=0xffcc00, description="<:warn:1297301606362251406> : Jail channel not found. Please create it first."))
        return

    # Charge les données de jail pour la guilde depuis Firestore
    jail_data = load_jail_data(ctx.guild.id)

    # Sauvegarde les rôles actuels du membre, excepté le rôle @everyone et boost
    roles_to_remove = [role for role in member.roles if role != ctx.guild.default_role and not role.is_premium_subscriber()]
    jail_data["jail_roles"][str(member.id)] = [role.id for role in roles_to_remove]
    jail_data["jailed_members"].append(member.id)

    # Retire les rôles du membre et ajoute le rôle de jail
    try:
        await member.remove_roles(*roles_to_remove)
        await member.add_roles(jail_role, reason=f"Jailed by {ctx.author} - {reason}")
        
        # Confirmation dans le serveur
        await ctx.send(embed=discord.Embed(color=0x00ff00, description=f"<:approve:1297301591698706483> : {member.mention} has been jailed for **{reason}**."))

        # Envoie un DM au membre pour l'informer de son emprisonnement
        try:
            dm_embed = discord.Embed(title="Jailed", color=0xff0000, description=f"You have been jailed in **{ctx.guild.name}**.")
            dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=True)
            dm_embed.set_footer(text=f"If you would like to dispute this punishment, contact a staff member.")
            if ctx.guild.icon:
                dm_embed.set_thumbnail(url=ctx.guild.icon.url)

            await member.send(embed=dm_embed)

        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(color=0xffcc00, description=f"<:warn:1297301606362251406> : Could not send DM to {member.mention}, they might have DMs disabled."))

        record_mod_action(ctx.author.id, 'jail', ctx.guild.id)
        record_history_action(member.id, 'jail', reason, ctx.author.id, ctx.guild.id)
        save_jail_data(ctx.guild.id, jail_data)

    except discord.Forbidden:
        await ctx.send(embed=discord.Embed(color=0xffcc00, description="<:warn:1297301606362251406> : I do not have permission to manage roles. Please check my role position and permissions."))

    except discord.HTTPException as e:
        await ctx.send(embed=discord.Embed(color=0xffcc00, description=f"<:warn:1297301606362251406> : An error occurred while jailing {member.mention}: {str(e)}"))
        print(f"Error in jail command: {str(e)}")

# Événement quand un membre rejoint, vérifiant s'il doit être en jail
@bot.event
async def on_member_join(member):
    # Charge les données de jail pour la guilde depuis Firestore
    jail_data = load_jail_data(member.guild.id)

    # Vérifie si le membre est en jail
    if member.id in jail_data["jailed_members"]:
        jail_role = discord.utils.get(member.guild.roles, name="jail")
        if jail_role is not None:
            await member.add_roles(jail_role, reason="Return of jail after disconnection.")
            await member.send(embed=discord.Embed(color=0xff0000, description=f"<:warn:1297301606362251406> : You were reinstated in jail upon rejoining {member.guild.name}."))


@bot.command(name='unjail')
@commands.has_permissions(manage_roles=True)
async def unjail_member(ctx, member: discord.Member = None, *, reason: str = "**No reason provided**"):
    # Vérifie si le rôle "jail" existe
    jail_role = discord.utils.get(ctx.guild.roles, name="jail")

    # Si aucun membre n'est précisé, on considère que l'utilisateur se libère lui-même
    if member is None:
        member = ctx.author

    # Charge les données de jail pour la guilde depuis Firestore
    jail_data = load_jail_data(ctx.guild.id)
    jailed_members = jail_data.get("jailed_members", [])
    jail_roles = jail_data.get("jail_roles", {})

    # Vérifie si le membre est en jail
    if member.id not in jailed_members:
        if member == ctx.author:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : You're not in jail.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : {member.mention} isn't in jail.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        return

    # Retire le rôle 'jail'
    await member.remove_roles(jail_role)

    # Enregistre l'historique de l'action
    record_history_action(member.id, 'unjail', reason, ctx.author.id, ctx.guild.id)

    # Restaure les rôles précédemment enregistrés
    if str(member.id) in jail_roles:
        roles_to_restore = [discord.utils.get(ctx.guild.roles, id=role_id) for role_id in jail_roles[str(member.id)]]
        await member.add_roles(*roles_to_restore)

        # Supprime les informations des rôles sauvegardés (jail_roles)
        del jail_roles[str(member.id)]

    # Supprime le membre de la liste des membres en jail
    jailed_members.remove(member.id)

    # Met à jour et sauvegarde les données dans Firestore
    jail_data["jailed_members"] = jailed_members
    jail_data["jail_roles"] = jail_roles
    save_jail_data(ctx.guild.id, jail_data)

    # Confirmation de libération dans le serveur
    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : {member.mention} has been released from jail - **{reason}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

    # Envoi d'un message privé pour informer le membre
    try:
        dm_embed = discord.Embed(
            title="Released from Jail",
            color=0x00ff00,
            description=f"You have been released from jail in **{ctx.guild.name}**."
        )
        dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        dm_embed.add_field(name="Reason", value=reason, inline=True)
        dm_embed.set_footer(text=f"Your roles have been restored. • {ctx.message.created_at.strftime('%d/%m/%Y %H:%M')}")

        if ctx.guild.icon:
            dm_embed.set_thumbnail(url=ctx.guild.icon.url)

        await member.send(embed=dm_embed)
    except discord.Forbidden:
        embed = discord.Embed(
                color=0xffcc00,
                description=f"<:warn:1297301606362251406> : Could not send DM to {member.mention}, they might have DMs disabled."
            )
        await ctx.send(embed=embed)


#mute

# Vérification des permissions moderate_members
def has_mute_members():
    async def predicate(ctx):
        if ctx.author.guild_permissions.moderate_members:
            return True
        else:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return False
    return commands.check(predicate)


@bot.command(name='mute', aliases=['timeout'])
@has_mute_members()
async def mute(ctx, member: discord.Member = None, time: str = None, *, reason: str = "No reason provided"):
    current_prefix = load_prefix(ctx.guild.id)

    # Vérifie si un membre est mentionné
    if member is None:
        embed = discord.Embed(
            title="Command name : mute",  # Nom de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="timeout", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="member, reason, time", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:warn:1297301606362251406> : **Manage_Roles**", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}mute <member> [duration] [reason]\n"
                  f"Example: {current_prefix}mute @User 10m Spamming```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module : moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Prévenir le mute de soi-même
    if member.id == ctx.author.id:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You cannot mute yourself.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Vérifier si l'utilisateur a un rôle égal ou supérieur
    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You cannot mute this member because their role is equal to or higher than yours.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Analyse des arguments pour déterminer la durée et la raison
    default_time = "1h"  # Durée par défaut
    valid_time_suffixes = ["s", "m", "h", "d", "y"]

    if time and time[-1] in valid_time_suffixes:
        duration = time
    else:
        duration = default_time
        reason = time if time else reason

    # Validation de la durée
    duration_seconds = 3600  # Par défaut : 1h
    try:
        if duration.endswith("s"):
            duration_seconds = int(duration[:-1])
        elif duration.endswith("m"):
            duration_seconds = int(duration[:-1]) * 60
        elif duration.endswith("h"):
            duration_seconds = int(duration[:-1]) * 3600
        elif duration.endswith("d"):
            duration_seconds = int(duration[:-1]) * 86400
        elif duration.endswith("y"):
            duration_seconds = int(duration[:-1]) * 31536000
        else:
            raise ValueError("Invalid time format")

        if duration_seconds > 28 * 24 * 60 * 60:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : The maximum mute duration is 28 days.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
    except ValueError:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Incorrect time format. Correct usage: `10s`, `5m`, `1h`, `3d`, `2y`. Please use only numbers and appropriate suffixes.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Appliquer le mute
    try:
        await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(seconds=duration_seconds), reason=reason)

        record_mod_action(ctx.author.id, 'mute', ctx.guild.id)
        record_history_action(member.id, 'mute', reason, ctx.author.id, ctx.guild.id)

        # Confirmation dans le serveur
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : {member.mention} has been muted for {duration} - **{reason}**",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

        # Envoi d'un DM à l'utilisateur
        try:
            dm_embed = discord.Embed(
                title="Muted",
                color=0xff0000,
                description=f"You have been muted in **{ctx.guild.name}**."
            )
            dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=True)
            dm_embed.add_field(name="Duration", value=duration, inline=True)
            dm_embed.set_footer(text=f"If you would like to dispute this punishment, contact a staff member. • {ctx.message.created_at.strftime('%d/%m/%Y %H:%M')}")

            if ctx.guild.icon:
                dm_embed.set_thumbnail(url=ctx.guild.icon.url)

            await member.send(embed=dm_embed)
        except discord.Forbidden:
            embed = discord.Embed(
                color=0xffcc00,
                description=f"<:warn:1297301606362251406> : Could not send DM to {member.mention}, they might have DMs disabled."
            )
            await ctx.send(embed=embed)

    except discord.Forbidden:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : I do not have permission to mute this member.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)



@bot.command(name='unmute', aliases=['untimeout'])
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member = None, *, reason: str = "**No reason provided**"):
    current_prefix = load_prefix(ctx.guild.id)

    # Si aucun membre n'est mentionné, affiche le message d'aide
    if member is None:
        embed = discord.Embed(
            title="Command name : unmute",  # Titre de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="untimeout",  # Alias de la commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="member, reason",  # Paramètres de la commande
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:warn:1297301606362251406> : **Manage_Roles**", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}unmute <member> [reason]\n"
                  f"Example: {current_prefix}unmute @User```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module : moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Vérifie si le membre est déjà unmute
    if member.timed_out_until is None or member.timed_out_until <= discord.utils.utcnow():
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} isn't muted.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Retirer le timeout du membre
    try:
        await member.edit(timed_out_until=None, reason="Unmute by a moderator.")
        
        # Confirmation de démutage
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : {member.mention} has been unmuted - {reason}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        # Enregistrement de l'action
        record_history_action(member.id, 'unmute', reason, ctx.author.id, ctx.guild.id)

        # Envoi d'un DM à l'utilisateur pour le notifier
        try:
            dm_embed = discord.Embed(
                title="Unmuted",
                color=0xff0000,
                description=f"You have been unmuted in **{ctx.guild.name}**."
            )
            dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=True)
            dm_embed.set_footer(text=f"You have been unmuted. • {ctx.message.created_at.strftime('%d/%m/%Y %H:%M')}")

            # Ajoute l'icône du serveur uniquement dans le DM
            if ctx.guild.icon:
                dm_embed.set_thumbnail(url=ctx.guild.icon.url)

            await member.send(embed=dm_embed)

        except discord.Forbidden:
            # Message d'erreur si le DM échoue, mais sans renvoyer le message d'unmute
            error_embed = discord.Embed(
                color=0xffcc00,
                description=f"<:warn:1297301606362251406> : Could not send DM to {member.mention}, they might have DMs disabled."
            )
            await ctx.send(embed=error_embed)

    except discord.Forbidden:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : I do not have permission to unmute this member.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> An error has occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

#warn


def load_warn_data(guild_id):
    doc_ref = db.collection("warn_data").document(str(guild_id))
    doc = doc_ref.get()
    
    if doc.exists:
        # Retourne les données existantes si le document est présent
        return doc.to_dict()
    else:
        # Initialisation des données pour une nouvelle guilde
        initial_data = {"warned_members": {}}
        doc_ref.set(initial_data)
        return initial_data

# Fonction pour sauvegarder les avertissements dans Firestore
def save_warn_data(guild_id, data):
    doc_ref = db.collection("warn_data").document(str(guild_id))
    doc_ref.set(data)

@commands.group(name='warn', invoke_without_command=True)
@has_manage_messages()
async def warn(ctx, member: discord.Member = None, *, reason: str = None):
    index = 0  # Pour la pagination

    # Si un membre est mentionné, ajoute l'avertissement directement
    if member is not None:
        # Prévenir si l'utilisateur essaie de s'avertir lui-même
        if member == ctx.author:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : You cannot warn yourself.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Prévenir si l'utilisateur essaie d'avertir un membre avec un rôle supérieur ou égal
        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : You cannot warn this member as their role is equal to or higher than yours.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Charger les avertissements du fichier pour le serveur actuel
        warns = load_warn_data(ctx.guild.id)

        # Ajouter un avertissement pour le membre
        if str(member.id) not in warns:
            warns[str(member.id)] = []

        if reason is None:
            reason = "**No reason provided**"

        # Ajouter l'avertissement
        warns[str(member.id)].append({
            "reason": reason,
            "moderator": ctx.author.id,
            "timestamp": ctx.message.created_at.isoformat()  # Enregistrer l'heure dans un format standard
        })
        save_warn_data(ctx.guild.id, warns)

        # Enregistrer les actions du modérateur et l'historique
        record_mod_action(ctx.author.id, 'warn', ctx.guild.id)
        record_history_action(member.id, 'warn', reason, ctx.author.id, ctx.guild.id)

        # Confirmation de l'avertissement
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : {member.mention} has been warned (#{len(warns[str(member.id)])}) - **{reason}**",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

        # Envoyer un DM au membre averti
        try:
            dm_embed = discord.Embed(
                title="Warned",
                color=0xff0000,
                description=f"You have received a warning in **{ctx.guild.name}**."
            )
            dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=True)
            dm_embed.add_field(name="Total Warnings", value=len(warns[str(member.id)]), inline=True)
            dm_embed.set_footer(text=f"If you would like to dispute this punishment, contact a staff member. • {ctx.message.created_at.strftime('%d/%m/%Y %H:%M')}")

            if ctx.guild.icon:
                dm_embed.set_thumbnail(url=ctx.guild.icon.url)

            await member.send(embed=dm_embed)

        except discord.Forbidden:
    # Si l'envoi du DM échoue
            error_embed = discord.Embed(
                color=0xffcc00,
                description=f"<:warn:1297301606362251406> : Could not send DM to {member.mention}, they might have DMs disabled."
                
            )
        await ctx.send(embed=error_embed)
        return  

    #here
    if member is None:
            # Fonction pour créer l'embed principal
            def create_embed(page_title):
                embed = discord.Embed(
                    title=page_title,
                    color=discord.Color(0x808080)
                )

                embed.set_author(
                    name=f"{bot.user.name}",
                    icon_url=bot.user.avatar.url   
                )

                embed.add_field(name="Aliases", value="N/A", inline=False)
                embed.add_field(name="Parameters", value="member, reason, time", inline=False)
                embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Manage_Roles**", inline=False)

                return embed

            # Pages d'usage
            pages = [
                {
                    "title": "Command name: warn",
                    "usage": f"```Syntax: {load_prefix(ctx.guild.id)}warn <member> [reason]\n"
                              f"Example: {load_prefix(ctx.guild.id)}warn @User```",
                    "footer": "Page 1/4"
                },
                {
                    "title": "Command name: warn list",
                    "usage": f"```Syntax: {load_prefix(ctx.guild.id)}warn list <member>\n"
                              f"Example: {load_prefix(ctx.guild.id)}warn list @User```",
                    "footer": "Page 2/4"
                },
                {
                    "title": "Command name: warn remove",
                    "usage": f"```Syntax: {load_prefix(ctx.guild.id)}warn remove <member> <warn_number|all>\n"
                              f"Example: {load_prefix(ctx.guild.id)}warn remove @User 1```",
                    "footer": "Page 3/4"
                },
                {
                    "title": "Command name: warn clear",
                    "usage": f"```Syntax: {load_prefix(ctx.guild.id)}warn clear <member>\n"
                              f"Example: {load_prefix(ctx.guild.id)}warn clear @User```",
                    "footer": "Page 4/4"
                },
            ]

            # Fonction pour changer d'embed
            async def update_embed(interaction, page_index):
                embed = create_embed(pages[page_index]["title"])  # Met à jour le titre
                embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
                embed.set_footer(text=f"{pages[page_index]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
                await interaction.response.edit_message(embed=embed)

            buttons = await create_buttons(ctx, pages, update_embed, current_time)

            # Envoi de l'embed initial
            initial_embed = create_embed(pages[0]["title"])
            initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
            initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
            await ctx.send(embed=initial_embed, view=buttons)
            return
    
        
# Command to display the list of warns

@warn.command(name='list')
@has_manage_messages()
async def warn_list(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)
    
    # Si aucun membre n'est spécifié, affiche l'aide
    if member is None:
        embed = discord.Embed(
            title="Command name : Warn list",
            description='Show all warnings for a user.',
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members, reason, time", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:warn:1297301606362251406> : **Manage_Roles**", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}warn list <member>\n"
                  f"Example: {current_prefix}warn list @User```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Charger les avertissements depuis le fichier
    warns = load_warn_data(ctx.guild.id)
    
    # Si le membre n'a aucun avertissement
    if str(member.id) not in warns or len(warns[str(member.id)]) == 0:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} has no warnings.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        return

    # Pagination des avertissements
    warns_list = warns[str(member.id)]
    items_per_page = 3
    total_pages = (len(warns_list) + items_per_page - 1) // items_per_page
    current_page = 0

    # Fonction pour créer l'embed avec la page actuelle
    async def create_warn_embed():
        start_index = current_page * items_per_page
        end_index = start_index + items_per_page
        warns_to_display = warns_list[start_index:end_index]

        warn_descriptions = "\n\n".join(
            [
                f"**{i + 1 + start_index}.** Reason: **{warn['reason']}**\n"
                f"Moderator: <@{warn['moderator']}>\n"
                f"Date: {discord.utils.format_dt(discord.utils.parse_time(warn['timestamp']), style='F')}"
                for i, warn in enumerate(warns_to_display)
            ]
        )
        
        embed = discord.Embed(
            title=f"{member.display_name}'s warnings.",  # Titre avec le nom du membre
            description=warn_descriptions or "No warnings to display.",
            color=discord.Color(0x808080)  # Couleur grise
        )
        embed.set_author(name=member.name, icon_url=member.avatar.url)
        embed.set_footer(text=f"Page {current_page + 1}/{total_pages} • {ctx.message.created_at.strftime('%H:%M')}")
        
        return embed

    embed = await create_warn_embed()
    message = await ctx.send(embed=embed)

    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(current_page == 0))
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(current_page == total_pages - 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def update_buttons():
        previous_button.disabled = (current_page == 0)
        next_button.disabled = (current_page == total_pages - 1)
        await message.edit(view=buttons)

    async def previous_callback(interaction):
        nonlocal current_page
        if interaction.user == ctx.author:
            if current_page > 0:
                current_page -= 1
                embed = await create_warn_embed()
                await interaction.response.edit_message(embed=embed)
                await update_buttons()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    async def next_callback(interaction):
        nonlocal current_page
        if interaction.user == ctx.author:
            if current_page < total_pages - 1:
                current_page += 1
                embed = await create_warn_embed()
                await interaction.response.edit_message(embed=embed)
                await update_buttons()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
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

    await message.edit(view=buttons)


# Command to remove a specific warn or all warns

@warn.command(name='remove')
@has_manage_messages()
async def warn_remove(ctx, member: discord.Member = None, warn_number=None, reason: str = "**No reason provided**"):
    current_prefix = load_prefix(ctx.guild.id)
    
    # Embed d'aide si member ou warn_number n'est pas spécifié
    if member is None or warn_number is None:
        embed = discord.Embed(
            title="Command name : Warn remove",
            description='Remove a specific warn of a user.',
            color=discord.Color(0x808080)
        )
        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )
        embed.add_field(name="Aliases", value="N/A", inline=False)
        embed.add_field(name="Parameters", value="member, reason, time", inline=False)
        embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Manage_Roles**", inline=False)
        embed.add_field(
            name="Usage",
            value=f"```Syntax: {current_prefix}warn remove <member> <warn number|all>\n"
                  f"Example: {current_prefix}warn remove @User 1```",
            inline=False
        )
        embed.set_footer(text=f"Page 1/1 | Module: moderation.py · {ctx.message.created_at.strftime('%H:%M')}")

        await ctx.send(embed=embed)
        return

    # Charger les avertissements depuis la base de données pour la guilde actuelle
    warns = load_warn_data(ctx.guild.id)

    # Vérifier si le membre a des avertissements
    if str(member.id) not in warns or len(warns[str(member.id)]) == 0:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} has no warnings to remove.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        return

    # Retirer tous les avertissements
    if warn_number.lower() == "all":
        warns[str(member.id)] = []
        save_warn_data(ctx.guild.id, warns)
        embed = discord.Embed(
            title="",
            description=f"<:approve:1297301591698706483> : All warnings for {member.mention} have been removed.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        return

    # Retirer un avertissement spécifique
    try:
        warn_index = int(warn_number) - 1  # Convertir en index basé sur 0
        if warn_index < 0 or warn_index >= len(warns[str(member.id)]):
            raise ValueError

        # Extraire les détails du warning
        removed_warn = warns[str(member.id)].pop(warn_index)  # Retirer l'avertissement
        save_warn_data(ctx.guild.id, warns)  # Sauvegarder les changements dans la base de données

        # Format enrichi pour le warning supprimé
        removed_details = (
            f"**Reason:** {removed_warn['reason']}\n"
            f"**Date:** {discord.utils.format_dt(discord.utils.parse_time(removed_warn['timestamp']), style='F')}\n"
            f"**Moderator:** <@{removed_warn['moderator']}>"
        )

        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : The following warning has been removed from {member.mention}.\n\n{removed_details}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        # Enregistrer l'action de suppression dans l'historique
        record_history_action(member.id, 'warn remove', reason, ctx.author.id, ctx.guild.id)

    except ValueError:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : The specified warn number is invalid.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@warn.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def warn_clear(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)
    
    # Vérification si aucun membre n'est fourni
    if member is None:
        embed = discord.Embed(
            title="Command name : Warn clear",
            description='Remove all warnings of a user.',
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="member", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:warn:1297301606362251406> : **Manage_Roles**", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}warn clear <member>\n"
                  f"Example: {current_prefix}warn clear @User```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Charger les avertissements depuis la base de données de la guilde
    warns = load_warn_data(ctx.guild.id)

    # Vérifier si le membre a des avertissements
    if str(member.id) not in warns or len(warns[str(member.id)]) == 0:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} has no warnings to clear.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Effacer tous les avertissements pour ce membre
    cleared_warnings = warns[str(member.id)]  # Conserver les warnings effacés pour confirmation
    warns[str(member.id)] = []
    save_warn_data(ctx.guild.id, warns)  # Sauvegarder après effacement

    # Confirmation d'effacement
    embed = discord.Embed(
        description=(
            f"<:approve:1297301591698706483> : All warnings for {member.mention} have been cleared.\n"
        ),
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

bot.add_command(warn)


@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member = None, *, reason: str = "**No reason provided**"):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        embed = discord.Embed(
            title="Command name : Ban",  # Nom de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="member, reason", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:warn:1297301606362251406> : **Ban_members**", 
            inline=False
        )

        # Bloc combiné pour Syntax et Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}ban <member> [reason]\n"
                  f"Example: {current_prefix}ban @User Spamming```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module : moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Check if the user is trying to ban themselves or someone above them
    if member == ctx.author:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : You can't ban yourself.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : You can't ban this member because their role is equal or superior to yours.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # URL of the GIF, which you can easily change
    ban_gif_url = "https://media1.tenor.com/m/BrHJBHqAxWAAAAAd/andrew-tate-top-g.gif"  # Replace with your preferred GIF URL

    try:
        # Send a DM to the member being banned
        try:
            dm_embed = discord.Embed(
                title="Banned",
                color=0xff0000,
                description=f"You have been banned from **{ctx.guild.name}**."
            )
            dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=True)
            dm_embed.set_footer(text=f"If you would like to dispute this punishment, contact a staff member. • {ctx.message.created_at.strftime('%d/%m/%Y %H:%M')}")

            # Ajoute l'icône du serveur uniquement dans le DM
            if ctx.guild.icon:
                dm_embed.set_thumbnail(url=ctx.guild.icon.url)

            await member.send(embed=dm_embed)

        except discord.Forbidden:
            # En cas d'échec de l'envoi du DM, créer un autre embed et l'envoyer ici
            embed = discord.Embed(
                color=0xffcc00,
                description=f"<:warn:1297301606362251406> : Could not send DM to {member.mention}, they might have DMs disabled."
            )
            await ctx.send(embed=embed)

        # Ban the member après tentative d'envoi du DM
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="",
            description=f"<:approve:1297301591698706483> : {member.mention} has been banned - **{reason}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        # Send the GIF as a normal message
        await ctx.send(ban_gif_url)

        record_mod_action(ctx.author.id, 'ban', ctx.guild.id)

    except discord.Forbidden:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : I do not have permission to ban this member.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> An error occurred during banning : {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

#KICK        

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_member(ctx, member: discord.Member = None, *, reason: str = "**No reason provided**"):
    current_prefix = load_prefix(ctx.guild.id)
    
    if member is None:
        embed = discord.Embed(
            title="Command name : Kick",  # Nom de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="member, reason", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:warn:1297301606362251406> : **Kick_members**", 
            inline=False
        )

        # Bloc combiné pour Syntax et Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}kick <member> [reason]\n"
                  f"Example: {current_prefix}kick @User Spamming```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module : moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Check if the user is trying to kick themselves or someone above them
    if member == ctx.author:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : You can't kick yourself.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : You can't kick this member because their role is equal or superior to yours.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    try:
        # Send a DM to the member being kicked
        try:
            dm_embed = discord.Embed(
                title="Kicked",
                color=0xff0000,
                description=f"You have been kicked from **{ctx.guild.name}**."
            )
            dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=True)
            dm_embed.set_footer(text=f"If you would like to dispute this punishment, contact a staff member. • {ctx.message.created_at.strftime('%d/%m/%Y %H:%M')}")

            # Ajoute l'icône du serveur uniquement dans le DM
            if ctx.guild.icon:
                dm_embed.set_thumbnail(url=ctx.guild.icon.url)

            await member.send(embed=dm_embed)

        except discord.Forbidden:
            embed = discord.Embed(
                color=0xffcc00,
                description=f"<:warn:1297301606362251406> : Could not send DM to {member.mention}, they might have DMs disabled."
            )
        await ctx.send(embed=embed)

        
        # Kick the member
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="",
            description=f"<:approve:1297301591698706483> : {member.mention} has been kicked - **{reason}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)


    except discord.Forbidden:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : I don't have permission to kick this member.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> An error occurred during kick : {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Error handling for the kick command
@kick_member.error
async def kick_member_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await send_permission_error(ctx)


#unban

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_info(ctx, member: discord.User = None, *, reason: str = "**No reason provided**"):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        embed = discord.Embed(
            title="Command name : Unban",  # Nom de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="member, reason", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:warn:1297301606362251406> : **Ban_members**", 
            inline=False
        )

        # Bloc combiné pour Syntax et Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}unban <member|userId> [reason]\n"
                  f"Example: {current_prefix}unban @User/196784564523 Behaved```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module : moderation.py · {current_time}"
        )

        await ctx.send(embed=embed)
        return

    try:
        await ctx.guild.unban(member)

        # Embed pour l'unban du membre
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : {member.name} has been unbanned - Reason: **{reason}**",
            color=discord.Color.green()
        )

        await ctx.send(embed=embed, reference=ctx.message)

        # Envoi d'un DM au membre unbanni
        try:
            dm_embed = discord.Embed(
                title="Unbanned",
                color=discord.Color.green(),
                description=f"You have been unbanned from **{ctx.guild.name}**."
            )
            dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=True)
            dm_embed.set_footer(text=f"You have been unbanned from {ctx.guild.name}. Behave! • {ctx.message.created_at.strftime('%d/%m/%Y %H:%M')}")

            # Ajoute l'icône du serveur uniquement dans le DM
            if ctx.guild.icon:
                dm_embed.set_thumbnail(url=ctx.guild.icon.url)

            await member.send(embed=dm_embed)

        except discord.Forbidden:
            # Si l'envoi du DM échoue
            error_embed = discord.Embed(
                color=0xffcc00,
                description=f"<:warn:1297301606362251406> : Could not send DM to {member.mention}, they might have DMs disabled."
            )
            await ctx.send(embed=error_embed)

    except discord.Forbidden:
        error_embed = discord.Embed(
            color=0xff0000,
            description=f"<:warn:1297301606362251406> : Sorry, I don't have permission to unban {member.name}."
        )
        await ctx.send(embed=error_embed)
    except discord.NotFound:
        error_embed = discord.Embed(
            color=0xff0000,
            description=f"<:warn:1297301606362251406> : User {member.name} is not banned."
        )
        await ctx.send(embed=error_embed)
    except Exception as e:
        error_embed = discord.Embed(
            color=0xff0000,
            description=f"<:warn:1297301606362251406> : An error occurred: {e}"
        )
        await ctx.send(embed=error_embed)

#MODSTATS

def load_mod_stats(guild_id):
    # Référence au document de statistiques de la guilde
    doc_ref = db.collection("mod_stats").document(str(guild_id))
    
    # Récupérer le document
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()["mod_stats"]
        
        # Initialisation des données si elles sont manquantes
        for mod_id, stats in data.items():
            if "actions" not in stats:
                stats["actions"] = []
            if "all_time" not in stats:
                stats["all_time"] = {
                    "mute": 0,
                    "jail": 0,
                    "ban": 0,
                    "warn": 0
                }
        return data
    else:
        # Si le document n'existe pas, initialiser les données
        initial_data = {}
        doc_ref.set({"mod_stats": initial_data})  # Crée le document avec un champ mod_stats vide
        return initial_data

# Fonction pour sauvegarder les statistiques dans Firestore
def save_mod_stats(guild_id, data):
    # Référence au document de statistiques de la guilde
    doc_ref = db.collection("mod_stats").document(str(guild_id))
    
    # Mise à jour du document
    doc_ref.update({"mod_stats": data})
    return True

# Enregistrer une action de modération
def record_mod_action(mod_id, action_type, guild_id):
    mod_id = str(mod_id)
    guild_id = str(guild_id)
    mod_stats = load_mod_stats(guild_id)

    if mod_id not in mod_stats:
        mod_stats[mod_id] = {
            "actions": [],
            "all_time": {
                "mute": 0,
                "jail": 0,
                "ban": 0,
                "warn": 0
            }
        }

    today = datetime.utcnow().strftime('%Y-%m-%d')
    mod_stats[mod_id]["actions"].append({
        "action": action_type,
        "date": today
    })

    if action_type in mod_stats[mod_id]["all_time"]:
        mod_stats[mod_id]["all_time"][action_type] += 1
    else:
        mod_stats[mod_id]["all_time"][action_type] = 1

    save_mod_stats(guild_id, mod_stats)

@bot.command(name='modstat', aliases=['modstats'])
@commands.has_permissions(manage_messages=True)
async def modstat(ctx, mod: discord.Member = None):
    if mod is None:
        mod = ctx.author

    stats = load_mod_stats(ctx.guild.id)
    mod_id = str(mod.id)

    if mod_id not in stats:
        stats[mod_id] = {
            "actions": [],
            "all_time": {
                "mute": 0,
                "jail": 0,
                "ban": 0,
                "warn": 0
            }
        }

    actions_7_days = {'mute': 0, 'jail': 0, 'ban': 0, 'warn': 0}
    today = datetime.utcnow()
    for action in stats[mod_id]['actions']:
        action_date = datetime.strptime(action['date'], '%Y-%m-%d')
        if (today - action_date).days <= 7:
            actions_7_days[action['action']] += 1

    embed = discord.Embed(
        title=f"Moderation statistics for {mod.display_name}",
        color=discord.Color(0x808080)
    )

    embed.add_field(name="7-day statistics", value=( 
        f"**Muted :** {actions_7_days['mute']}\n"
        f"**Jailed :** {actions_7_days['jail']}\n"
        f"**Banned :** {actions_7_days['ban']}\n"
        f"**Warned :** {actions_7_days['warn']}"
    ), inline=True)

    all_time_stats = stats[mod_id]['all_time']
    embed.add_field(name="All time statistics", value=( 
        f"**Muted :** {all_time_stats['mute']}\n"
        f"**Jailed :** {all_time_stats['jail']}\n"
        f"**Banned :** {all_time_stats['ban']}\n"
        f"**Warned :** {all_time_stats['warn']} "
    ), inline=True)

    await ctx.send(embed=embed)

#role command

@bot.group(name='role', aliases=['r'], invoke_without_command=True)
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member = None, *, role_names: str = None):
    current_prefix = load_prefix(ctx.guild.id)

    # Si aucun membre ou rôle n'est spécifié, on affiche l'aide
    if member is None:
        # Fonction pour créer l'embed principal
        def create_embed(page_title, page_description):
            embed = discord.Embed(
                title=page_title,
                description=page_description,  # Ajout de la description juste sous le titre
                color=discord.Color(0x808080)
            )

            embed.set_author(
                name=f"{bot.user.name}",
                icon_url=bot.user.avatar.url
            )
            
            embed.add_field(name="Aliases", value="r", inline=False)
            embed.add_field(name="Parameters", value="member", inline=False)
            embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Manage_Roles**", inline=False)

            return embed

        # Pages d'usage
        pages = [
            {
                "title": "Command name: role",
                "description": "Give a role or remove a role to a user.",
                "usage": f"```Syntax: {current_prefix}role user <role>\n"
                          f"Example: {current_prefix}role @user @role```",
                "footer": "Page 1/8"
            },
            {
                "title": "Command name: role list",
                "description": "List all roles available in the server.",
                "usage": f"```Syntax: {current_prefix}role list.\n"
                          f"Example: {current_prefix}role list```",
                "footer": "Page 2/8"
            },
            {
                "title": "Command name: role create",
                "description": "Create a new role in the server.",
                "usage": f"```Syntax: {current_prefix}role create <role>\n"
                          f"Example: {current_prefix}role create @role```",
                "footer": "Page 3/8"
            },
            {
                "title": "Command name: role delete",
                "description": "Delete an existing role from the server.",
                "usage": f"```Syntax: {current_prefix}role delete <role>\n"
                          f"Example: {current_prefix}role delete @role```",
                "footer": "Page 4/8"
            },
            {
                "title": "Command name: role in",
                "description": "Show the number of people who has a specific role.",
                "usage": f"```Syntax: {current_prefix}role in <role>\n"
                          f"Example: {current_prefix}role in @role```",
                "footer": "Page 5/8"
            },
            {
                "title": "Command name: role temp",
                "description": "Temporarily assigns a role to a user for a given period of time.",
                "usage": f"```Syntax: {current_prefix}role temp <user> <time> <role>\n"
                          f"Example: {current_prefix}role temp @gato 30s admin```",
                "footer": "Page 6/8"
            },
            {
                "title": "Command name: role templist",
                "description": "Show temporarily role assigned to a user for a given period of time.",
                "usage": f"```Syntax: {current_prefix}role templist \n"
                          f"Example: {current_prefix}role templist```",
                "footer": "Page 7/8"
            },
            {
                "title": "Command name: role strip",
                "description": "Strip important roles from a member based on their permissions",
                "usage": f"```Syntax: {current_prefix}role strip <member>  \n"
                          f"Example: {current_prefix}role strip @user```",
                "footer": "Page 8/8"
            },
        ]


        # Fonction pour changer d'embed
        async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])  # Utilise la description
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
            await interaction.response.edit_message(embed=embed)

        buttons = await create_buttons(ctx, pages, update_embed, current_time)

        # Envoi de l'embed initial
        initial_embed = create_embed(pages[0]["title"], pages[0]["description"])  # Utilise la description
        initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
        initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
        await ctx.send(embed=initial_embed, view=buttons)
        return


    # Si le rôle et le membre sont spécifiés, on applique la logique pour ajouter ou retirer le rôle
    role_names = [role.strip() for role in role_names.split(',')]  # Sépare les rôles par des virgules
    added_roles = []
    removed_roles = []
    errors = []

    for role_name in role_names:
        role = find_role(ctx, role_name)

        if role is None:
            errors.append(f"<:warn:1297301606362251406> : I didn't find the role **{role_name}**. Please check the role name and try again.")
            continue

        if role >= ctx.author.top_role:
            errors.append(f"<:warn:1297301606362251406> : You cannot manage the role **{role.mention}** which is higher or equal to your top role.")
            continue

        if role >= ctx.guild.me.top_role:
            errors.append(f"<:warn:1297301606362251406> : I cannot manage the role **{role.mention}** which is higher or equal to my top role.")
            continue

        # Si le membre a déjà le rôle, on le retire
        if role in member.roles:
            await member.remove_roles(role)
            removed_roles.append(role.mention)
        else:
            # Sinon, on l'ajoute
            await member.add_roles(role)
            added_roles.append(role.mention)

    # Créer l'embed de réponse
    embed_description = ""

    if added_roles or removed_roles:
        combined_roles = []

        if added_roles:
            combined_roles.extend([f"**+**{role}" for role in added_roles])  # Ajoute les rôles avec '+'

        if removed_roles:
            combined_roles.extend([f"**-**{role}" for role in removed_roles])  # Ajoute les rôles avec '-'

        # Crée une seule ligne avec les rôles modifiés
        embed_description += f"<:approve:1297301591698706483> : Edited roles - {', '.join(combined_roles)} for {member.mention}.\n"

    # En cas d'erreurs, ajoute-les à la description
    if errors:
        embed_description += "\n".join(errors)

    # Création de l'embed avec la description modifiée
    embed = discord.Embed(
        description=embed_description or "No changes were made.",
        color=discord.Color.green() if added_roles or removed_roles else discord.Color.red()
    )

    # Envoi de l'embed en réponse au message
    await ctx.send(embed=embed, reference=ctx.message)

# Fonction pour chercher un rôle
def find_role(ctx, role_name):
    role_name = role_name.lower()
    for role in ctx.guild.roles:
        if role_name in role.name.lower():
            return role
    return None

# Sous-commande pour lister les rôles

async def create_role_embed(roles, current_page, items_per_page, total_pages, author):
    start_index = current_page * items_per_page
    end_index = start_index + items_per_page
    roles_to_display = roles[start_index:end_index]

    description = "\n".join([f"{role.mention} - Position: {role.position}" for role in roles_to_display])

    embed = discord.Embed(
        title="Roles in this Server",
        description=description or "No roles to display.",
        color=discord.Color(0x808080)
    )
    embed.set_footer(text=f"Page {current_page + 1}/{total_pages} • Requested by {author.display_name}")

    return embed

@role.command(name='list')
@commands.has_permissions(manage_roles=True)
async def role_list(ctx):
    roles = ctx.guild.roles
    roles = sorted(roles, key=lambda r: r.position, reverse=True)  # Sort roles from lowest to highest

    items_per_page = 6
    total_pages = (len(roles) + items_per_page - 1) // items_per_page
    current_page = 0

    # Function to create the embed with roles and their position
    async def create_role_embed(roles, current_page, items_per_page, total_pages, author):
        start = current_page * items_per_page
        end = start + items_per_page
        page_roles = roles[start:end]
        embed = discord.Embed(
            title=f"Role List (Page {current_page + 1}/{total_pages})",
            color=discord.Color(0x808080)
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)

        # Calculate the correct position (highest role is 1)
        for index, role in enumerate(page_roles):
            role_index = (current_page * items_per_page) + index + 1
            embed.add_field(
                name=f"#{role_index}: {role.name}",  # Displaying role name without mention
                value=f"Members: {len(role.members)}",
                inline=False
            )
        embed.set_footer(text=f"Page {current_page + 1} of {total_pages} | Module : moderation.py")
        return embed

    embed = await create_role_embed(roles, current_page, items_per_page, total_pages, ctx.author)
    message = await ctx.send(embed=embed)

    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(current_page == 0))
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(current_page == total_pages - 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def update_embed():
        embed = await create_role_embed(roles, current_page, items_per_page, total_pages, ctx.author)
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
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
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
                    description=f"<:warn:1297301606362251406> : You are not the author of this message.",
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

    await message.edit(view=buttons)


@role.command(name='create')
@commands.has_permissions(manage_roles=True)
async def create_role(ctx, name: str, color: str):
    """Create a role with a specified name and color."""
    # Check if a role with the same name already exists
    existing_role = discord.utils.get(ctx.guild.roles, name=name)
    if existing_role:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : A role with the name **{name}** already exists.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Remove the '#' from the color if present
    if color.startswith('#'):
        color = color[1:]

    # Initialize role parameters
    kwargs = {
        'name': name,
        'color': discord.Color(int(color, 16))  # Convert hex color to Color object
    }

    # Create the role
    new_role = await ctx.guild.create_role(**kwargs)

    # Success message in gray embed
    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Role **{new_role.mention}** created successfully!",  # Use mention here
        color=discord.Color(0x808080)
    )
    await ctx.send(embed=embed)

# Error handling for `create`
@create_role.error
async def create_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You do not have permission to manage roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"An error occurred: {error}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@role.command(name='delete')
@commands.has_permissions(manage_roles=True)
async def delete_role(ctx, role: discord.Role):
    """Delete a specified role."""
    # Check if the role exists
    if role not in ctx.guild.roles:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : The role {role.mention} does not exist.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Check if the role is higher than the bot's highest role
    if role.position >= ctx.guild.me.top_role.position:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You cannot delete the role {role.mention} because it is higher than or equal to the bot's highest role.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Delete the role
    await role.delete()

    # Success message in gray embed
    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Role {role.mention} deleted successfully!",
        color=discord.Color(0x808080)
    )
    await ctx.send(embed=embed)

# Error handling for `delete`
@delete_role.error
async def delete_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You do not have permission to manage roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Please specify a valid role.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"An error occurred: {error}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@role.command(name="in")
async def role_in(ctx, *, role_name: str = None):
    current_prefix = load_prefix(ctx.guild.id)  # Assurez-vous de charger le préfixe correctement

    # Si aucun rôle n'est fourni, envoyer un message d'aide
    if not role_name:
        embed = discord.Embed(
            title="Command name: role in",
            description="Check who has a particular role in the server.",
            color=discord.Color(0x808080)  # Couleur gris foncé
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
            value="role",
            inline=False
        )

        embed.add_field(
            name="Permissions",
            value="N/A",
            inline=False
        )

        embed.add_field(
            name="Usage",
            value=f"```Syntax: {current_prefix}role in <role_name>\n"
                  f"Example: {current_prefix}role in moderator```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: role.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Rechercher un rôle partiellement en insensible à la casse
    role = discord.utils.find(lambda r: role_name.lower() in r.name.lower(), ctx.guild.roles)

    if not role:
        await ctx.send(embed=discord.Embed(description=f"<:warn:1297301606362251406> : The role containing '{role_name}' was not found.", color=discord.Color.red()))
        return
    
    members = [member for member in ctx.guild.members if role in member.roles]
    if not members:
        await ctx.send(embed=discord.Embed(description=f"<:warn:1297301606362251406> : No members found with the role '{role.name}'.", color=discord.Color.red()))
        return

    items_per_page = 8
    total_pages = (len(members) - 1) // items_per_page + 1
    current_page = 0

    # Fonction pour créer l'embed de la page
    async def create_role_embed(members, current_page, items_per_page, total_pages, author):
        start = current_page * items_per_page
        end = start + items_per_page
        page_members = members[start:end]
        embed = discord.Embed(
            title=f"Members with the role {role.name}",
            color=discord.Color(0x808080)
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        for member in page_members:
            embed.add_field(name=member.display_name, value=member.mention, inline=False)
        embed.set_footer(text=f"Page {current_page + 1} of {total_pages} | Module : moderation.py • {len(members)} members")
        return embed

    # Afficher la première page
    embed = await create_role_embed(members, current_page, items_per_page, total_pages, ctx.author)
    message = await ctx.send(embed=embed)

    # Configuration des boutons
    buttons = discord.ui.View(timeout=60)
    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(current_page == 0))
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(current_page == total_pages - 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    # Fonction de mise à jour de l'embed
    async def update_embed():
        embed = await create_role_embed(members, current_page, items_per_page, total_pages, ctx.author)
        await message.edit(embed=embed)

    # Callback pour le bouton "précédent"
    async def previous_callback(interaction):
        if interaction.user == ctx.author:  # Vérification de l'auteur
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                await update_embed()
                previous_button.disabled = (current_page == 0)
                next_button.disabled = (current_page == total_pages - 1)
                await interaction.response.edit_message(view=buttons)
        else:
            await interaction.response.send_message(embed=discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                color=discord.Color.red()), ephemeral=True)

    # Callback pour le bouton "suivant"
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
            await interaction.response.send_message(embed=discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                color=discord.Color.red()), ephemeral=True)

    # Callback pour le bouton "fermer"
    async def close_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(embed=discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                color=discord.Color.red()), ephemeral=True)

    # Assigner les callbacks aux boutons
    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    # Ajouter les boutons à la vue
    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    await message.edit(view=buttons)


def format_time(seconds):
    """Fonction pour formater le temps en fonction des unités."""
    if seconds >= 86400:  # Si la durée est en jours
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''}"
    elif seconds >= 3600:  # Si la durée est en heures
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif seconds >= 60:  # Si la durée est en minutes
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:  # Si la durée est en secondes
        return f"{seconds} second{'s' if seconds > 1 else ''}"


@role.command()
@commands.has_permissions(administrator=True)  # Cette commande est réservée aux administrateurs
async def strip(ctx, member: discord.Member= None):
    current_prefix = load_prefix(ctx.guild.id)
    """Sous-commande pour retirer les rôles importants d'un membre, basée sur les permissions."""
    
    # Vérification si le membre est None
    if member is None:
        embed = discord.Embed(
            title="Command name: strip",
            description='Strip important roles from a member based on their permissions.',
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{ctx.bot.user.name}",
            icon_url=ctx.bot.user.avatar.url
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="member", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="Administrator",
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}role strip <member>\n"
                  f"Example: {current_prefix}role strip @User```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Définir les permissions importantes (générales)
    important_permissions = [
        'administrator',
        'manage_roles',
        'manage_guild',
        'kick_members',
        'ban_members',
        'manage_messages',
        'manage_channels',
        'manage_webhooks',
    ]
    
    # Obtenir les rôles du membre
    roles_to_remove = []

    for role in member.roles:
        # Ignorer le rôle @everyone
        if role.name == "@everyone":
            continue
        
        # Vérifier si le rôle contient l'une des permissions importantes
        if any(getattr(role.permissions, perm, False) for perm in important_permissions):
            roles_to_remove.append(role)

    if not roles_to_remove:
        # Si aucun rôle important n'a été trouvé
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.display_name} does not have any important roles to remove.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Vérifier que l'auteur a des permissions suffisantes pour retirer des rôles
    higher_roles = [role for role in ctx.author.roles if role.position > member.top_role.position]
    if not higher_roles:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You cannot strip roles from this member because they have higher or equal roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Préparer les rôles à afficher
    roles_display = [role.mention for role in roles_to_remove]
    
    # Si plus de 3 rôles sont supprimés, n'afficher que les 3 premiers avec + X autres
    if len(roles_display) > 3:
        roles_display = roles_display[:3] + [f"+ {len(roles_display) - 3} others"]
    
    # Retirer les rôles
    for role in roles_to_remove:
        await member.remove_roles(role)
    
    # Embeds de confirmation
    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Successfully stripped the following important roles from {member.mention} -  {', '.join(roles_display)}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


#role temp is in specials file.

#role end 

#history 

def load_history_data(guild_id):
    doc_ref = db.collection("guild_history").document(str(guild_id))
    
    # Récupérer le document
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict().get("history", {})
    else:
        doc_ref.set({"history": {}})
        return {}

def save_history_data(guild_id, data):
    doc_ref = db.collection("guild_history").document(str(guild_id))
    
    doc_ref.update({"history": data})
    return True


def record_history_action(user_id, action_type, reason, moderator_id, guild_id):
    history_data = load_history_data(guild_id)

    if str(guild_id) not in history_data:
        history_data[str(guild_id)] = {}

    user_cases = history_data[str(guild_id)].get(str(user_id), {})
    case_number = str(len(user_cases) + 1)  # Numéro de cas
    entry = {
        'type': action_type,
        'reason': reason,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'moderator_id': moderator_id
    }

    if str(user_id) not in history_data[str(guild_id)]:
        history_data[str(guild_id)][str(user_id)] = {}

    history_data[str(guild_id)][str(user_id)][case_number] = entry

    save_history_data(guild_id, history_data)


@bot.group(name='history', invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def history(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        # Fonction pour créer l'embed principal
        def create_embed(page_title, page_description):
            embed = discord.Embed(
                title=page_title,
                description=page_description,  # Ajout de la description juste sous le titre
                color=discord.Color(0x808080)
            )

            embed.set_author(
                name=f"{bot.user.name}",
                icon_url=bot.user.avatar.url
            )
            
            embed.add_field(name="Aliases", value="N/A", inline=False)
            embed.add_field(name="Parameters", value="member", inline=False)
            embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Manage_Roles**", inline=False)

            return embed

        # Pages d'usage
        pages = [
            {
                "title": "Command name: history",
                "description": "Shows all the record action of an user.",
                "usage": f"```Syntax: {current_prefix}history <user> \n"
                          f"Example: {current_prefix}history @user ```",
                "footer": "Page 1/3"
            },
            {
                "title": "Command name: history clear",
                "description": "Clear all the record action of an user.",
                "usage": f"```Syntax: {current_prefix}history clear <user>.\n"
                          f"Example: {current_prefix}history clear @user```",
                "footer": "Page 2/3"
            },
            {
                "title": "Command name: history remove",
                "description": "Remove a specific record action of an user.",
                "usage": f"```Syntax: {current_prefix}history remove <user> <action_number>\n"
                          f"Example: {current_prefix}history remove @user 1```",
                "footer": "Page 3/3"
            },
            
        ]

        # Fonction pour changer d'embed
        async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])  # Utilise la description
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
            await interaction.response.edit_message(embed=embed)

        # Boutons de navigation
        buttons = await create_buttons(ctx, pages, update_embed, current_time)

        # Envoi de l'embed initial
        initial_embed = create_embed(pages[0]["title"], pages[0]["description"])  # Utilise la description
        initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
        initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
        await ctx.send(embed=initial_embed, view=buttons)
        return


    guild_id = str(ctx.guild.id)
    user_id = str(member.id)

    # Charger les données d'historique depuis le Gist
    history_data = load_history_data(guild_id)

    # Vérification que l'historique des sanctions existe pour le guild_id et user_id
    if guild_id not in history_data or user_id not in history_data[guild_id]:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} has no record of actions.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    history_entries = history_data[guild_id][user_id]

    # Si l'historique est vide
    if not history_entries:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : No actions recorded for {member.mention}.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Trier les entrées par la date pour afficher les plus récentes en premier
    # Assumer que 'date' est au format 'YYYY-MM-DD HH:MM:SS' ou un format comparable
    sorted_entries = sorted(
        history_entries.items(),
        key=lambda item: datetime.strptime(item[1]['date'], '%Y-%m-%d %H:%M:%S'),
        reverse=True
    )

    # Formatage des entrées triées
    entries_list = [
        f"\n**Case {case} :** {entry['type']}\n Reason : **{entry['reason']}** - Moderator : <@{entry['moderator_id']}>\n Punished : {discord.utils.format_dt(discord.utils.parse_time(entry['date']), style='F')}"
        for case, entry in sorted_entries
    ]

    # Pagination setup
    entries_per_page = 3
    total_pages = (len(entries_list) + entries_per_page - 1) // entries_per_page
    index = 0

    start_index = index * entries_per_page
    end_index = start_index + entries_per_page

    # Embed pour afficher l'historique
    embed = discord.Embed(
        title=f"History of {member.display_name}",
        description='\n'.join(entries_list[start_index:end_index]),
        color=discord.Color(0x808080)
    )
    embed.set_footer(text=f"Page: {index + 1}/{total_pages} • {ctx.message.created_at.strftime('%H:%M')}")


    buttons = View(timeout=60)
    
    previous_button = Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(index == 0))
    next_button = Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(total_pages <= 1))
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
                ephemeral=True  # Visible uniquement par l'utilisateur
            )

    async def next_callback(interaction):
        if interaction.user.id == ctx.author.id:
            nonlocal index
            if index < total_pages - 1:
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
        if interaction.user.id == ctx.author.id:  # Vérifie si l'utilisateur qui interagit est celui qui a exécuté la commande
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

    message = await ctx.send(embed=embed, view=buttons)

    async def update_embed(interaction):
        start_index = index * entries_per_page
        end_index = start_index + entries_per_page
        embed.title = f"History of {member.display_name}"
        embed.description = '\n'.join(entries_list[start_index:end_index])
        embed.set_footer(text=f"Page: {index + 1}/{total_pages}")
        await interaction.response.edit_message(embed=embed)
        previous_button.disabled = (index == 0)
        next_button.disabled = (index == total_pages - 1)
        await message.edit(view=buttons)

    await update_embed(None)

@history.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, member: discord.Member):
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)

    # Vérifier si l'historique existe dans le Gist
    history_data = load_history_data(guild_id)

    # Vérification de l'existence de l'historique pour le membre
    if guild_id not in history_data or user_id not in history_data[guild_id] or not history_data[guild_id][user_id]:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} has no history to clear.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Supprimer l'historique du membre
    del history_data[guild_id][user_id]

    # Sauvegarder les données mises à jour dans le Gist
    if save_history_data(guild_id, history_data):
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : Cleared all history for {member.mention}.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Failed to clear history for {member.mention}.",
            color=discord.Color.red()
        )

    await ctx.send(embed=embed)


@history.command(name='remove')
@commands.has_permissions(manage_messages=True)
async def remove(ctx, member: discord.Member, case_number: int):
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)

    # Vérifier si l'historique existe dans le Gist
    history_data = load_history_data(guild_id)

    # Vérifier si l'utilisateur et le cas existent
    if guild_id not in history_data or user_id not in history_data[guild_id] or case_number < 1:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} has no actions recorded.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    user_cases = history_data[guild_id][user_id]

    if str(case_number) not in user_cases:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Case number {case_number} does not exist for {member.mention}.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Supprimer le cas
    del user_cases[str(case_number)]

    # Si aucun cas n'est resté, supprimer l'utilisateur
    if not user_cases:
        del history_data[guild_id][user_id]

    # Sauvegarder les données mises à jour dans le Gist
    if save_history_data(guild_id, history_data):
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : Removed case number {case_number} from {member.mention}'s history.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Failed to remove case number {case_number} from {member.mention}'s history.",
            color=discord.Color.red()
        )

    await ctx.send(embed=embed)

# Gérer les erreurs de permission
@clear.error
@remove.error
async def history_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You do not have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)


#nickname

def load_locked_nicknames(guild_id):
    # Charger les données de Firestore pour une guilde spécifique
    doc_ref = db.collection("locked_nicknames").document(str(guild_id))
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict() or {}
    else:
        # Initialisation des données pour une nouvelle guilde
        initial_data = {}
        doc_ref.set(initial_data)
        return initial_data

def save_locked_nicknames(guild_id, data):
    # Sauvegarder les données dans Firestore pour une guilde spécifique
    doc_ref = db.collection("locked_nicknames").document(str(guild_id))
    doc_ref.set(data)

def get_server_locked_nicknames(guild_id):
    # Charger les données des pseudonymes verrouillés pour une guilde
    data = load_locked_nicknames(guild_id)  # Passer guild_id ici
    return data.get(str(guild_id), {})  # Retourner les données de la guilde spécifique

def update_server_locked_nicknames(guild_id, user_id, nickname):
    # Charger les données des pseudonymes verrouillés
    data = load_locked_nicknames(guild_id)  # Passer guild_id ici
    
    # Vérifier si la guilde existe, sinon l'ajouter
    if str(guild_id) not in data:
        data[str(guild_id)] = {}
    
    # Mettre à jour le pseudonyme verrouillé pour l'utilisateur
    data[str(guild_id)][str(user_id)] = nickname

    # Sauvegarder les données mises à jour dans Firestore
    save_locked_nicknames(guild_id, data)  # Passer guild_id ici


def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

@bot.group(name='nickname', invoke_without_command=True)
async def nickname(ctx):
    """Groupe de commandes pour les pseudonymes liés aux utilisateurs."""
    if ctx.invoked_subcommand is None:
        # Fonction pour créer l'embed principal
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
            embed.add_field(name="Parameters", value="member", inline=False)
            embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Admin**", inline=False)

            return embed

        # Pages d'usage
        pages = [
            {
                "title": "Command name: nickname lock",
                "description": "Locks a user's nickname to a specified name.",
                "usage": f"```Syntax: {ctx.prefix}nickname lock <user> <new_nickname> \n"
                          f"Example: {ctx.prefix}nickname lock @user NewNickname```",
                "footer": "Page 1/3"
            },
            {
                "title": "Command name: nickname unlock",
                "description": "Unlocks a user's nickname.",
                "usage": f"```Syntax: {ctx.prefix}nickname unlock <user> \n"
                          f"Example: {ctx.prefix}nickname unlock @user```",
                "footer": "Page 2/3"
            },
            {
                "title": "Command name: nickname list",
                "description": "list users with a locked nickname.",
                "usage": f"```Syntax: {ctx.prefix}nickname list \n"
                          f"Example: {ctx.prefix}nickname list```",
                "footer": "Page 3/3"
            },
        ]

        # Fonction pour changer d'embed
        async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
            await interaction.response.edit_message(embed=embed)

        buttons = await create_buttons(ctx, pages, update_embed, current_time)

        # Envoi de l'embed initial
        initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
        initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
        initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")

        await ctx.send(embed=initial_embed, view=buttons)


@nickname.command(name='lock')
@is_admin()
async def lock_nickname(ctx, member: discord.Member = None, *, new_nickname: str = None):
    """Verrouille le pseudonyme d'un membre et définit un nouveau pseudo."""
    
    if not ctx.author.guild_permissions.manage_nicknames:
        await send_permission_error(ctx)  # Utilise la fonction send_permission_error
        return
    
    # Charger les pseudonymes verrouillés pour le serveur depuis Firestore
    locked_nicknames = get_server_locked_nicknames(ctx.guild.id)

    if member is None or new_nickname is None:
        embed = discord.Embed(
            title="Command name: nickname lock",
            description="Locks a user's nickname to a specified name.",
            color=discord.Color(0x808080)
        )
        
        embed.add_field(
            name="Aliases", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="username", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="<:warn:1297301606362251406> : **Admin**", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {ctx.prefix}nickname lock <user> <new nickname>\n"
                  f"Example: {ctx.prefix}nickname lock @user gatolover```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 • Module: moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )
        
        await ctx.send(embed=embed)
        return

    # Enregistrer le nouveau pseudo dans le dictionnaire, en remplaçant l'ancien
    locked_nicknames[str(member.id)] = new_nickname
    update_server_locked_nicknames(ctx.guild.id, member.id, new_nickname)  # Sauvegarder les modifications dans Firestore

    # Modifier le pseudo du membre
    try:
        await member.edit(nick=new_nickname)
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : {member.mention}'s nickname has been locked to **{new_nickname}**.",
            color=discord.Color(0x808080)  # Couleur grise pour l'embed
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : I don't have permission to change that user's nickname.",
            color=discord.Color(0x808080)  # Couleur grise pour l'embed
        )
        await ctx.send(embed=embed, reference=ctx.message)
    except discord.HTTPException:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : Failed to change the nickname due to an unexpected error.",
            color=discord.Color(0x808080)  # Couleur grise pour l'embed
        )
        await ctx.send(embed=embed, reference=ctx.message)


# Listener pour appliquer le pseudonyme verrouillé quand un utilisateur rejoint à nouveau
@bot.event
async def on_member_join(member):
    # Charger les données des pseudonymes verrouillés depuis Firestore
    locked_nicknames = load_locked_nicknames(member.guild.id)
    
    # Obtenir les données spécifiques au serveur
    server_data = locked_nicknames.get(str(member.guild.id), {})
    
    # Obtenir le pseudo verrouillé pour le membre, s'il existe
    locked_nickname = server_data.get(str(member.id))  
    
    if locked_nickname:
        try:
            await member.edit(nick=locked_nickname)
        except discord.Forbidden:
            print(f"Can't change my pookie {member}'s name.")
        except discord.HTTPException:
            print("Guess who can't change the pseudo lol.")

@nickname.command(name='unlock')
@is_admin()
async def unlock_nickname(ctx, member: discord.Member = None):
    """Déverrouille le pseudonyme d'un membre."""
    
    if not ctx.author.guild_permissions.manage_nicknames:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You cannot use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return
    
    # Charger les pseudonymes verrouillés depuis Firestore
    locked_nicknames = load_locked_nicknames(ctx.guild.id)  # Passer guild_id ici

    server_data = locked_nicknames.get(str(ctx.guild.id), {})  # Obtenir les données pour ce serveur
    if member is None:
        embed = discord.Embed(
            title="Command name: nickname lock",
            description="Unlocks a user's nickname.",
            color=discord.Color(0x808080)
        )
        
        embed.add_field(
            name="Aliases", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="username", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="<:warn:1297301606362251406> : **Admin**", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {ctx.prefix}nickname unlock <user>\n"
                  f"Example: {ctx.prefix}nickname unlock @user```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 • Module: moderation.py · {ctx.message.created_at.strftime('%H:%M')}"
        )
        
        await ctx.send(embed=embed)
        return

    if str(member.id) in server_data:
        # Retirer le pseudonyme verrouillé
        del server_data[str(member.id)]
        locked_nicknames[str(ctx.guild.id)] = server_data  # Sauvegarder les modifications dans les données globales
        save_locked_nicknames(ctx.guild.id, locked_nicknames)  # Sauvegarder dans Firestore en utilisant guild_id
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : {member.mention}'s nickname has been unlocked.",
            color=discord.Color(0x808080)  # Couleur grise pour l'embed
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.mention} doesn't have a locked nickname.",
            color=discord.Color(0x808080)  # Couleur grise pour l'embed
        )
        await ctx.send(embed=embed, reference=ctx.message)


@nickname.command(name="list")
async def nickname_list(ctx):
    """Affiche la liste des pseudonymes verrouillés pour le serveur."""
    guild_id = str(ctx.guild.id)

    # Charger les données des pseudonymes verrouillés
    locked_nicknames = load_locked_nicknames(guild_id)

    # Vérifier si des pseudonymes sont verrouillés pour ce serveur
    if not locked_nicknames:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : No locked nicknames in this server.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    # Construire une liste des utilisateurs et pseudonymes verrouillés
    nickname_entries = []
    for user_id, sub_data in locked_nicknames.items():
        for target_user_id, nickname in sub_data.items():
            try:
                member = ctx.guild.get_member(int(target_user_id))
                if member:
                    nickname_entries.append(f"**{member.mention}** - `{nickname}`")
                else:
                    nickname_entries.append(f"**[Unknown User ID: {target_user_id}]** - `{nickname}`")
            except Exception as e:
                nickname_entries.append(f"Error processing user {target_user_id}: {e}")

    # Pagination
    items_per_page = 6
    total_pages = (len(nickname_entries) + items_per_page - 1) // items_per_page
    current_page = 0

    # Fonction pour créer un embed paginé
    async def create_embed(entries, page, items_per_page, total_pages, author):
        start = page * items_per_page
        end = start + items_per_page
        page_entries = entries[start:end]
        embed = discord.Embed(
            title=f"Locked Nicknames",
            description="\n".join(page_entries),
            color=discord.Color(0x808080)
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        embed.set_footer(text=f"Page {page + 1} of {total_pages} | Module: moderation.py")
        return embed

    # Envoyer le premier embed
    embed = await create_embed(nickname_entries, current_page, items_per_page, total_pages, ctx.author)
    message = await ctx.send(embed=embed)

    # Configuration des boutons
    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(current_page == 0))
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(current_page == total_pages - 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def update_embed():
        embed = await create_embed(nickname_entries, current_page, items_per_page, total_pages, ctx.author)
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



@bot.event
async def on_member_update(before, after):
    # Charger les pseudonymes verrouillés depuis Firestore pour la guilde spécifique
    locked_nicknames = load_locked_nicknames(after.guild.id)  # Passer guild_id ici

    server_data = locked_nicknames.get(str(after.guild.id), {})  # Obtenir les données pour ce serveur
    if str(before.id) in server_data:
        # Si le pseudonyme a été changé et que l'utilisateur est dans la liste des pseudonymes verrouillés
        if before.nick != after.nick:
            try:
                # Restaurer le pseudonyme verrouillé
                await after.edit(nick=server_data[str(before.id)])

                # Envoyer un message dans les logs (optionnel)
                log_channel = discord.utils.get(after.guild.text_channels, name="logs")
                if log_channel:
                    await log_channel.send(f"🔒 {after.mention}'s nickname was changed and automatically restored to **{server_data[str(before.id)]}**.")

            except discord.Forbidden:
                # Gestion des permissions
                if log_channel:
                    await log_channel.send(f"<:warn:1297301606362251406> : I don't have permission to change {after.mention}'s nickname back.")
            except discord.HTTPException:
                if log_channel:
                    await log_channel.send(f"<:warn:1297301606362251406> : Failed to restore {after.mention}'s nickname.")

#lock and unlock channel channel



def has_manage_roles():
    async def predicate(ctx):
        return ctx.author.guild_permissions.manage_roles
    return commands.check(predicate)


# Commande pour verrouiller un channel
@bot.command(name="lock")
@has_manage_roles()
async def lock_channel(ctx, channel: discord.TextChannel = None):
    # Si aucun channel n'est spécifié, verrouiller le channel actuel
    if channel is None:
        channel = ctx.channel

    overwrite = channel.overwrites_for(ctx.guild.default_role)  # Permissions par défaut pour @everyone
    overwrite.send_messages = False  # Interdire l'envoi de messages

    try:
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.message.add_reaction("✅")  # Ajouter une réaction verte en cas de succès
    except discord.Forbidden:
        await ctx.message.add_reaction("❌")  # Ajouter une réaction rouge si le bot n'a pas les permissions

# Commande pour déverrouiller un channel
@bot.command(name="unlock")
@has_manage_roles()
async def unlock_channel(ctx, channel: discord.TextChannel = None):
    # Si aucun channel n'est spécifié, déverrouiller le channel actuel
    if channel is None:
        channel = ctx.channel

    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True  # Autoriser l'envoi de messages

    try:
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.message.add_reaction("✅")  # Ajouter une réaction verte en cas de succès
    except discord.Forbidden:
        await ctx.message.add_reaction("❌")  # Ajouter une réaction rouge si le bot n'a pas les permissions

# Gestion des erreurs pour les commandes lock/unlock
@lock_channel.error
@unlock_channel.error
async def lock_unlock_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await send_permission_error(ctx)
