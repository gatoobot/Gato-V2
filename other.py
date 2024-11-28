from config import *
from mango import *

import random
import subprocess

from fractions import Fraction
from sympy import series, solve, Rational, oo
from sympy import symbols, diff, sympify, sqrt, simplify, I,  SympifyError


#PING
@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Latence en ms

    # Liste de phrases randomisées
    phrases = [
        f"It took me **{latency} ms** to find some milfs around you.",
        f"My ping is **{latency} ms**, faster than you finding a girl.",
        f"Just a casual **{latency} ms** delay in finding goth girls.",
        f"It took me **{latency} ms** to hate you.",
        f"My response time is **{latency} ms**. You probably faster begging for a goth girl.",
        f"Surprisingly, it only took **{latency} ms** to find a crazy latina near you!",
        f"it took me **{latency} ms** to ping your mom",
        f"It took me **{latency} ms** ping no one.",
        f"It took me **{latency} ms** to find hot latina woman near you.",
        f"It took me **{latency} ms** to tell you to find a job.",
        f"It took me **{latency} ms** to idk i swear.",
        f"It took me **{latency} ms** to say fuck the capitalism"

    
    ]

    # Sélectionner une phrase aléatoire
    selected_phrase = random.choice(phrases)

    # Création de l'embed avec la phrase sélectionnée
    embed = discord.Embed(
        description=selected_phrase,
        color=discord.Color(0x808080)  # Vous pouvez changer la couleur selon vos préférences
    )
    
    await ctx.send(embed=embed)  # Envoi de l'embed


#welcome 

welcome_collection = db['welcome']  # Collection 'welcome' pour les paramètres de bienvenue

# Fonction pour récupérer les paramètres de bienvenue depuis MongoDB
def load_welcome_settings(guild_id):
    # Rechercher les paramètres pour le serveur dans MongoDB
    doc = welcome_collection.find_one({"guild_id": str(guild_id)})

    # Si aucun document trouvé, retourner des paramètres par défaut
    if not doc:
        return {"enabled": False, "channel": None}

    return doc  # Retourner les paramètres sous forme de dictionnaire

# Fonction pour sauvegarder les paramètres de bienvenue dans MongoDB
def save_welcome_settings(guild_id, settings):
    # Mettre à jour ou insérer les paramètres pour ce serveur
    welcome_collection.update_one(
        {"guild_id": str(guild_id)},
        {"$set": settings},
        upsert=True
    )
    print("Welcome settings successfully saved to MongoDB.")

# Événement lorsqu'un membre rejoint le serveur
@bot.event
async def on_member_join(member):
    welcome_settings = load_welcome_settings(member.guild.id)
    if welcome_settings.get("enabled") and welcome_settings.get("channel"):
        channel = bot.get_channel(int(welcome_settings["channel"]))
        if channel:
            try:
                # Message de bienvenue en texte brut
                welcome_message = await channel.send(
                    f"<a:1137545879742578699:1297307264008327228> <a:1260683932517666876:1297307297550307358> Welcome to {member.mention}, in {member.guild.name}!"
                )
                await welcome_message.delete(delay=15)  # Supprime le message après 15 secondes
            except discord.Forbidden:
                print(f"<:warn:1297301606362251406> : I don't have permissions to send messages to {channel.name}.")
            except Exception as e:
                print(f"<:warn:1297301606362251406>s : An error has occurred: {e}")

# Événement lorsque quelqu'un rejoint le serveur
@bot.event
async def on_member_join(member):
    welcome_settings = load_welcome_settings(member.guild.id)
    if welcome_settings["enabled"] and welcome_settings["channel"]:
        channel = bot.get_channel(int(welcome_settings["channel"]))
        if channel:
            try:
                # Message de bienvenue en texte brut
                welcome_message = await channel.send(f"<a:1137545879742578699:1297307264008327228> <a:1260683932517666876:1297307297550307358> Welcome to {member.mention}, in {member.guild.name} !")
                await welcome_message.delete(delay=15)  # Supprime le message après 15 secondes
            except discord.Forbidden:
                print(f"<:warn:1297301606362251406> : I don't have permissions to send messages to {channel.name}.")
            except Exception as e:
                print(f"<:warn:1297301606362251406> : An error has occurred: {e}")

# Création d'un groupe de commandes pour le système de bienvenue
@bot.group(name='welcome', invoke_without_command=True)
async def welcome(ctx):
    current_prefix = load_prefix(ctx.guild.id)

    def create_embed(page_title, page_description):
        embed = discord.Embed(
            title=page_title,
            description=page_description,  # Ajout de la description sous le titre
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
            "title": "Command name : welcome toggle ",
            "description": "Activate the welcome system of the bot.",
            "usage": f"```Syntax: {current_prefix}welcome toggle.\n"
                      f"Example: {current_prefix}Welcome toggle.```",
            "footer": "Page 1/2"
        },
        {
            "title": "Command name: welcome setchannel",
            "description": "Configure the channel where the messages will be send.",
            "usage": f"```Syntax: {current_prefix}welcome setchannel <channel>\n"
                      f"Example: {current_prefix}welcome setchannel #welcome```",
            "footer": "Page 2/2"
        },
       
    ]

    # Fonction pour changer d'embed
    async def update_embed(interaction, page_index):
        embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
        embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
        embed.set_footer(text=f"{pages[page_index]['footer']} | Module: other.py • {ctx.message.created_at.strftime('%H:%M')}")
        await interaction.response.edit_message(embed=embed)


    buttons = await create_buttons(ctx, pages, update_embed, current_time)

    # Envoi de l'embed initial
    initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
    initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
    initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: other.py • {ctx.message.created_at.strftime('%H:%M')}")
    await ctx.send(embed=initial_embed, view=buttons)

@welcome.command(name='toggle')
@commands.has_permissions(administrator=True)
async def toggle_welcome(ctx):
    welcome_settings = load_welcome_settings(ctx.guild.id)
    welcome_settings["enabled"] = not welcome_settings["enabled"]
    save_welcome_settings(ctx.guild.id, welcome_settings)
    status = "enabled" if welcome_settings["enabled"] else "disabled"

    color = discord.Color.green() if welcome_settings["enabled"] else discord.Color.red()
    embed = discord.Embed(
        title="",
        description=f"👋 : The welcome system is now {status}.",
        color=color
    )
    await ctx.send(embed=embed)

@welcome.command(name='setchannel')
@commands.has_permissions(administrator=True)
async def set_welcome_channel(ctx, channel: discord.TextChannel = None):
    welcome_settings = load_welcome_settings(ctx.guild.id)

    if channel is None:
        if welcome_settings["channel"]:
            existing_channel = bot.get_channel(int(welcome_settings["channel"]))
            embed = discord.Embed(
                title="",
                description=f"<:warn:1297301606362251406> : A channel is already configured for welcome messages: {existing_channel.mention}. "
                            f"If you want to change this, type `welcome setchannel <channel>`. ",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : Please specify a valid channel to send welcome messages to. Use `#` before the channel name or mention the channel directly!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Vérifie si un salon est mentionné
    if isinstance(channel, discord.TextChannel):
        welcome_settings["channel"] = str(channel.id)
        save_welcome_settings(ctx.guild.id, welcome_settings)
        embed = discord.Embed(
            title="",
            description=f"<:approve:1297301591698706483> : Configured welcome channel, welcome messages will be sent to {channel.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : Channel not found. Make sure the channel exists and that the name is correct.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


#leave

leave_settings_collection = db["leave_settings"]

# Fonction pour charger les paramètres de départ depuis MongoDB
def load_leave_settings(guild_id):
    settings = leave_settings_collection.find_one({"guild_id": guild_id})
    if settings:
        return settings
    else:
        return {"enabled": False, "channel": None}

# Fonction pour sauvegarder les paramètres de départ dans MongoDB
def save_leave_settings(guild_id, settings):
    leave_settings_collection.update_one(
        {"guild_id": guild_id},
        {"$set": settings},
        upsert=True
    )
    print(f"Leave settings successfully saved for guild {guild_id}.")

# Événement lorsque quelqu'un quitte le serveur
@bot.event
async def on_member_remove(member):
    leave_settings = load_leave_settings(member.guild.id)
    if leave_settings["enabled"] and leave_settings["channel"]:
        channel = bot.get_channel(int(leave_settings["channel"]))
        if channel:
            try:
                # Message de départ en texte brut
                await channel.send(f"{member.name} has left the server.")
            except discord.Forbidden:
                print(f"<:warn:1297301606362251406> : I don't have permissions to send messages to {channel.name}.")
            except Exception as e:
                print(f"<:warn:1297301606362251406> : An error has occurred: {e}")

# Fonction pour envoyer un message d'erreur si le système de départ n'est pas activé
async def send_leave_disabled_error(ctx):
    current_prefix = load_prefix(ctx.guild.id)
    
    embed = discord.Embed(
        description=f"<:warn:1297301606362251406> : The leaving system is deactivated. Please activate it with `{current_prefix}leave toggle`.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# Fonction pour gérer les permissions insuffisantes
async def send_permission_error(ctx):
    embed = discord.Embed(
        description=f"<:warn:1297301606362251406> : You do not have permission to use this command.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# Commande de groupe pour gérer les paramètres de départ
@bot.group(name='leave', invoke_without_command=True)
async def leave(ctx):
    current_prefix = load_prefix(ctx.guild.id)

    def create_embed(page_title, page_description):
            embed = discord.Embed(
                title=page_title,
                description=page_description,  # Ajout de la description sous le titre
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
                "title": "Command name : leave toggle ",
                "description": "Activate the leave system of the bot.",
                "usage": f"```Syntax: {current_prefix}leave toggle.\n"
                        f"Example: {current_prefix}leave toggle.```",
                "footer": "Page 1/2"
            },
            {
                "title": "Command name: leave setchannel",
                "description": "Configure the channel where the messages will be send.",
                "usage": f"```Syntax: {current_prefix}leave setchannel <channel>\n"
                        f"Example: {current_prefix}leave setchannel #leave```",
                "footer": "Page 2/2"
            },
        
        ]

        # Fonction pour changer d'embed
    async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: other.py • {ctx.message.created_at.strftime('%H:%M')}")
            await interaction.response.edit_message(embed=embed)

        # Boutons de navigation
    buttons = await create_buttons(ctx, pages, update_embed, current_time)

        # Envoi de l'embed initial
    initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
    initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
    initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: other.py • {ctx.message.created_at.strftime('%H:%M')}")
    await ctx.send(embed=initial_embed, view=buttons)

@leave.command(name='toggle')
@commands.has_permissions(administrator=True)
async def toggle_leave(ctx):
    leave_settings = load_leave_settings(ctx.guild.id)
    leave_settings["enabled"] = not leave_settings["enabled"]
    save_leave_settings(ctx.guild.id, leave_settings)
    status = "enabled" if leave_settings["enabled"] else "disabled"

    color = discord.Color.green() if leave_settings["enabled"] else discord.Color.red()
    embed = discord.Embed(
        title="",
        description=f"<:approve:1297301591698706483> : The leaving system is now {status}.",
        color=color
    )
    await ctx.send(embed=embed)

# Sous-commande pour configurer le salon de départ
@leave.command(name='setchannel')
@commands.has_permissions(manage_channels=True)
async def set_leave_channel(ctx, channel: discord.TextChannel = None):
    leave_settings = load_leave_settings(ctx.guild.id)
    
    if not leave_settings["enabled"]:
        await send_leave_disabled_error(ctx)
        return

    if channel is None:
        if leave_settings["channel"]:
            existing_channel = bot.get_channel(int(leave_settings["channel"]))
            embed = discord.Embed(
                title="",
                description=f"The current leaving channel is {existing_channel.mention}. "
                            f"To change the channel, use the command with another channel.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="",
                description=f"<:warn:1297301606362251406> : No leaving channel is configured. Please specify a valid channel to send departure messages to. "
                            "Use `#` before the channel's name or mention the channel directly!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        return

    if isinstance(channel, discord.TextChannel):
        leave_settings["channel"] = str(channel.id)
        save_leave_settings(ctx.guild.id, leave_settings)
        embed = discord.Embed(
            title="",
            description=f"<:approve:1297301591698706483> : Leaving messages will be sent in {channel.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : Channel not found. Make sure the channel exists and that the name is correct.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        description="You can find all available bot commands on this site.",
        color=0x808080 
    )
    embed.add_field(name="Documentation Site", value="[Click here to access the site](https://gatoobot.github.io/Gato-web/)", inline=False)
    embed.set_footer(text="Use the commands as shown on the site for more information.")

    await ctx.send(embed=embed)


#education 

@bot.group(name="solve", invoke_without_command=True)
async def solve(ctx):
    current_prefix = load_prefix(ctx.guild.id)

    def create_embed(page_title, page_description, aliases):
        embed = discord.Embed(
            title=page_title,
            description=page_description,
            color=discord.Color(0x808080)
        )
        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )
        embed.add_field(name="Aliases", value=aliases, inline=False)
        embed.add_field(name="Parameters", value="channel", inline=False)
        embed.add_field(name="Permissions", value="N/A", inline=False)
        return embed

    # Pages d'usage avec des alias spécifiques pour chaque commande
    pages = [
        {
            "title": "Command name: quadratic",
            "description": "Calculate the roots of a quadratic equation of the form `ax^2 + bx + c = 0`.",
            "aliases": "N/A",
            "usage": f"```Syntax: {current_prefix}solve quadratic <a> <b> <c>\n"
                     f"Example: {current_prefix}solve quadratic 1 -3 2```",
            "footer": "Page 1/3"
        },
        {
            "title": "Command name: derivative",
            "description": "Calculate the derivative of a given function in terms of x.",
            "aliases": "dx, derivate",
            "usage": f"```Syntax: {current_prefix}solve derivative <function>\n"
                     f"Example: {current_prefix}solve derivative x^2 + sin(x)/x```",
            "footer": "Page 2/3"
        },
        {
            "title": "Command name: dl",
            "description": "Calculate the limited development of a function around a default point of `0` up to a specified degree.",
            "aliases": "N/A",
            "usage": f"```Syntax: {current_prefix}solve dl <function> <degree>\n"
                     f"Example: {current_prefix}solve dl cos(x) 3```",
            "footer": "Page 3/3"
        },
    ]

    # Fonction pour changer d'embed
    async def update_embed(interaction, page_index):
        page = pages[page_index]
        embed = create_embed(page["title"], page["description"], page["aliases"])
        embed.add_field(name="Usage", value=page["usage"], inline=False)
        embed.set_footer(text=f"{page['footer']} | Module: other.py • {ctx.message.created_at.strftime('%H:%M')}")
        await interaction.response.edit_message(embed=embed)

    buttons = await create_buttons(ctx, pages, update_embed, current_time)

    # Envoi de l'embed initial
    initial_page = pages[0]
    initial_embed = create_embed(initial_page["title"], initial_page["description"], initial_page["aliases"])
    initial_embed.add_field(name="Usage", value=initial_page["usage"], inline=False)
    initial_embed.set_footer(text=f"{initial_page['footer']} | Module: other.py • {ctx.message.created_at.strftime('%H:%M')}")

    await ctx.send(embed=initial_embed, view=buttons)


@solve.command(name='quadratic')
async def quadratic(ctx, a: float = None, b: float = None, c: float = None):
    current_prefix = load_prefix(ctx.guild.id)
    if a is None or b is None or c is None:
        embed = discord.Embed(
            title="Command name: quadratic",
            description="Calculate the roots of a quadratic equation of the form `ax^2 + bx + c = 0`.",
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )

        embed.add_field(name="Aliases", value="N/A", inline=False)
        embed.add_field(name="Parameters", value="a, b, c", inline=False)
        embed.add_field(name="Permissions", value="N/A", inline=False)

        embed.add_field(
            name="Usage",
            value=f"```Syntax: {current_prefix}solve quadratic <a> <b> <c>\n"
                  f"Example: {current_prefix}solve quadratic 1 -3 2```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: math.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    x = symbols('x')  # Déclaration de la variable

    # Convertir les coefficients en Rational pour des calculs exacts
    a, b, c = Rational(a), Rational(b), Rational(c)

    # Calculer le discriminant
    discriminant = b**2 - 4 * a * c

    # Calculer les racines exactes, en autorisant les solutions complexes
    root1 = simplify((-b + sqrt(discriminant)) / (2 * a))
    root2 = simplify((-b - sqrt(discriminant)) / (2 * a))

    # Affichage des résultats
    result_embed = discord.Embed(
        title="Quadratic Equation Solution",
        color=discord.Color(0x808080)
    )
    result_embed.add_field(name="Equation", value=f"`{a}x² + {b}x + {c} = 0`", inline=False)
    result_embed.add_field(name="Root 1", value=f"`{root1}`", inline=False)
    result_embed.add_field(name="Root 2", value=f"`{root2}`", inline=False)

    result_embed.set_footer(text=f"Module: math.py • {ctx.message.created_at.strftime('%H:%M')}")

    await ctx.send(embed=result_embed)


@solve.command(name='derivative', aliases=['dx', 'derivate'])
async def derivative(ctx, *, function: str = None):
    current_prefix= load_prefix(ctx.guild.id)
    if function is None:
        embed = discord.Embed(
            title="Command name: derivative",
            description="Calculate the derivative of a given function in terms of x.",
            color=discord.Color(0x808080)
        )
        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )
        embed.add_field(
            name="Aliases",
            value="dx, derivate",
            inline=False
        )
        embed.add_field(
            name="Parameters",
            value="function",
            inline=False
        )
        embed.add_field(
            name="Permissions",
            value="N/A",
            inline=False
        )
        embed.add_field(
            name="Usage",
            value=f"```Syntax: {current_prefix}solve derivative <function>\nExample: {current_prefix}solve derivative x**2 + sin(x)/x```",
            inline=False
        )
        await ctx.send(embed=embed)
        return

    # Variable pour la différentiation
    x = symbols('x')
    try:
        # Conversion en expression SymPy
        expr = sympify(function)
        derivative_expr = diff(expr, x)
        
        # Embed pour le résultat
        embed = discord.Embed(
            title="Derivative Calculation",
            color=discord.Color(0x808080)
        )
        embed.add_field(name="Function", value=f"`{function}`", inline=True)
        embed.add_field(name="Derivative", value=f"`{derivative_expr}`", inline=True)
        
        await ctx.send(embed=embed)
        
    except SympifyError:
        await ctx.send("Invalid function format. Please enter a valid mathematical expression.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@solve.command(name="dl")
async def dl(ctx, function: str = None, degree: int = 2):
    current_prefix = load_prefix(ctx.guild.id)
    x = symbols('x')  # Déclaration de la variable

    # Si aucun paramètre n'est fourni, afficher l'embed d'explication
    if function is None:
        embed = discord.Embed(
            title="Command name: dl",
            description="Calculate the limited development of a function around a default point of `0` up to a specified degree.",
            color=discord.Color(0x808080)
        )
        embed.set_author(name=f"{bot.user.name}", icon_url=bot.user.avatar.url)
        embed.add_field(name="Aliases", value="N/A", inline=False)
        embed.add_field(name="Parameters", value="function, degree", inline=False)
        embed.add_field(name="Permissions", value="N/A", inline=False)
        embed.add_field(
            name="Usage",
            value=f"```Syntax: {current_prefix}solve dl <function> <degree>\n"
                  f"Example: {current_prefix}solve dl sin(x) 5```",
            inline=False
        )
        embed.set_footer(text=f"Page 1/1 | Module: math.py • {ctx.message.created_at.strftime('%H:%M')}")
        await ctx.send(embed=embed)
        return

    try:
        # Convertir l'expression en SymPy
        expr = sympify(function)
        
        # Si la fonction est un produit de plusieurs termes (détecter le produit par '*')
        if '*' in function:
            # Séparer les termes du produit
            parts = function.split('*')
            product_series = 1

            # Calculer le développement limité pour chaque terme du produit
            for part in parts:
                expr_part = sympify(part.strip())  # Chaque partie du produit
                dl_part = series(expr_part, x, 0, degree + 1).removeO()  # Développement limité de chaque partie
                product_series *= dl_part  # Multiplier les séries

            # Trier et formater les termes dans l'ordre croissant du degré
            sorted_terms = sorted(product_series.as_ordered_terms(), key=lambda term: term.as_poly(x).degree())
            formatted_series = " + ".join([str(term) for term in sorted_terms])

        else:
            # Sinon, calculer simplement le développement limité d'une fonction seule
            dl_series = series(expr, x, 0, degree + 1).removeO()
            sorted_terms = sorted(dl_series.as_ordered_terms(), key=lambda term: term.as_poly(x).degree())
            formatted_series = " + ".join([str(term) for term in sorted_terms])

        # Création de l'embed pour afficher le résultat
        embed = discord.Embed(
            title="Limited Development",
            color=discord.Color(0x808080)
        )
        embed.add_field(name="Function", value=f"`{function}`", inline=True)
        embed.add_field(name="Degree", value=f"{degree}", inline=True)
        embed.add_field(name="Result", value=f"`{formatted_series}`", inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


#code 

@bot.command(name="run_code")
async def run_code(ctx, language: str = None, *, code: str = None):
    """Execute code in Python, JavaScript, or C."""
    
    # If no code or language is provided, send a help embed
    if not language or not code:
        current_prefix = load_prefix(ctx.guild.id)

        embed = discord.Embed(
            title="Command name: run_code",
            description="Execute code in Python, JavaScript, or C.",
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )

        embed.add_field(
            name="Parameters", 
            value="language (py/js/c), code (code to execute)",
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}run_code <language> <code>\n"
                  f"Example: {current_prefix}run_code py print('Hello, World!')```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: other.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # For Python code
    if language.lower() == "py":
        try:
            # Execute Python code using exec
            exec_locals = {}
            exec(code, {}, exec_locals)

            output = "\n".join(f"{key}: {value}" for key, value in exec_locals.items())
            if not output:
                output = "No output returned from the executed code."
            embed = discord.Embed(
                title="Python Code Execution Result",
                description=f"**Output:**\n{output}",
                color=discord.Color(0x808080)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : Error executing Python code:\n{str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_error)
    
    # For JavaScript code (using Node.js)
    elif language.lower() == "js":
        try:
            # Write the JS code to a temporary file
            with open("temp_script.js", "w") as js_file:
                js_file.write(code)

            # Run the JavaScript code using Node.js
            result = subprocess.run(["node", "temp_script.js"], capture_output=True, text=True)
            output = result.stdout or result.stderr

            # Delete the temporary JS file
            os.remove("temp_script.js")

            embed = discord.Embed(
                title="JavaScript Code Execution Result",
                description=f"**Output:**\n{output}",
                color=discord.Color(0x808080)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : Error executing JavaScript code:\n{str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_error)

    # For C code (using GCC)
    elif language.lower() == "c":
        try:
            # Write the C code to a temporary file
            with open("temp_script.c", "w") as c_file:
                c_file.write(code)

            # Compile the C code using GCC
            result = subprocess.run(["gcc", "temp_script.c", "-o", "temp_script"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(result.stderr)

            # Run the compiled C program
            result = subprocess.run(["./temp_script"], capture_output=True, text=True)
            output = result.stdout or result.stderr

            # Delete the temporary C files
            os.remove("temp_script.c")
            os.remove("temp_script")

            embed = discord.Embed(
                title="C Code Execution Result",
                description=f"**Output:**\n{output}",
                color=discord.Color(0x808080)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : Error executing C code:\n{str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_error)

    else:
        embed_error = discord.Embed(
            description="<:warn:1297301606362251406> : Unsupported language. Please use 'py', 'js', or 'c'.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)

#IDK 

@bot.command(name='motivation')
async def motivation(ctx):
    # Liste de phrases randomisées
    phrases = [
        "You piece of shit waking up morning to be trash.",
        "Nobody want to date a broke yn.",
        "If you have 1000 haters, i'm one of em yn. If you have 10 haters i'm one of em and if u don't then its not true cuz i'm here.",
        "Just give up on life and become a full time alcoholic.",
        "You destined to be a failure and homeless give up on life.",
        "Lazy ass go find a job. ",
        "I hope my ex die ong.", 
        "Let be fr just give up", 
        "Ain't no way u become succesful"
    
    ]

    # Sélectionner une phrase aléatoire
    selected_phrase = random.choice(phrases)

    # Création de l'embed avec la phrase sélectionnée
    embed = discord.Embed(
        description=selected_phrase,
        color=discord.Color(0x808080)  # Vous pouvez changer la couleur selon vos préférences
    )
    
    await ctx.send(embed=embed)