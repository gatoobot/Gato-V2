from config import *
from mango import *


import io 
import re 
import pytz
import aiohttp
import requests 
import lyricsgenius
from PIL import Image
from discord.ext import tasks
from datetime import timedelta, datetime 
from pydub import AudioSegment
from google.cloud import speech
from timezonefinder import TimezoneFinder 
from google.oauth2 import service_account
from dateutil.relativedelta import relativedelta


load_dotenv()


@bot.command(name='avatar', aliases=['av'])
async def avatar(ctx, user: discord.Member = None):
    
    user = user or ctx.author  # Si aucun utilisateur n'est mentionné, prendre l'auteur du message.

    # Vérifier si l'utilisateur a un avatar
    if user.avatar:
        embed = discord.Embed(
            description=f"Avatar from {user.mention}",
            color=discord.Color(0x808080)  # Couleur par défaut
        )
        
        # Récupérer l'URL de l'avatar
        avatar_url = user.avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with Image.open(io.BytesIO(img_data)) as img:
                        img = img.convert('RGB')  # Convertir l'image en RGB
                        img = img.resize((100, 100))  # Redimensionner l'image pour le traitement
                        colors = img.getcolors(maxcolors=1000000)  # Récupérer les couleurs
                        

                        # Assurez-vous que la liste de couleurs n'est pas vide
                        if colors:
                            most_common_color = max(colors, key=lambda x: x[0])[1]  # Obtenir la couleur la plus fréquente
                        else:
                            most_common_color = (0, 0, 0)  # Valeur par défaut si aucune couleur trouvée


                    # Vérifier si most_common_color est bien un tuple de trois éléments
                    if isinstance(most_common_color, tuple) and len(most_common_color) == 3:
                        dominant_color = discord.Color.from_rgb(most_common_color[0], most_common_color[1], most_common_color[2])
                        embed.color = dominant_color  # Mettre à jour la couleur de l'embed
                    else:
                        embed.color = discord.Color(0x808080)  # Couleur par défaut si erreur

        embed.set_image(url=avatar_url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {user.mention} has no avatar configured.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command(name='sav', aliases=['serveravatar','savatar'])
async def sav(ctx, user: discord.Member = None):
    
    user = user or ctx.author  # Si aucun utilisateur n'est mentionné, prendre l'auteur du message.

    # Vérifier si l'utilisateur a un profil de serveur
    if user.guild_avatar:  # Vérifie si l'utilisateur a une image de profil de serveur
        embed = discord.Embed(
            description=f"Server avatar profile from {user.mention}",
            color=discord.Color(0x808080)  # Couleur par défaut
        )
        
        # Récupérer l'avatar et le traiter pour trouver la couleur dominante
        avatar_url = user.guild_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with Image.open(io.BytesIO(img_data)) as img:
                        img = img.convert('RGB')  # Convertir l'image en RGB
                        img = img.resize((100, 100))  # Redimensionner l'image pour le traitement
                        colors = img.getcolors(maxcolors=1000000)  # Récupérer les couleurs
                        

                        # Assurez-vous que la liste de couleurs n'est pas vide
                        if colors:
                            most_common_color = max(colors, key=lambda x: x[0])[1]  # Obtenir la couleur la plus fréquente
                        else:
                            most_common_color = (0, 0, 0)  # Valeur par défaut si aucune couleur trouvée


                    # Vérifier si most_common_color est bien un tuple de trois éléments
                    if isinstance(most_common_color, tuple) and len(most_common_color) == 3:
                        dominant_color = discord.Color.from_rgb(most_common_color[0], most_common_color[1], most_common_color[2])
                        embed.color = dominant_color  # Mettre à jour la couleur de l'embed
                    else:
                        embed.color = discord.Color(0x808080)  # Couleur par défaut si erreur

        embed.set_image(url=user.guild_avatar.url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {user.mention} has no server profile configured.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command(name='banner')
async def banner(ctx, user: discord.Member = None):
    
    user = user or ctx.author  # Si aucun utilisateur n'est mentionné, prendre l'auteur du message.

    # Récupérer les informations du profil de l'utilisateur
    user_info = await ctx.bot.fetch_user(user.id)

    # Vérifier si l'utilisateur a une bannière
    if user_info.banner:
        embed = discord.Embed(
            description=f"Banner from {user.mention}",
            color=discord.Color(0x808080)  # Couleur par défaut
        )
        
        # Récupérer l'URL de la bannière
        banner_url = user_info.banner.url
        async with aiohttp.ClientSession() as session:
            async with session.get(banner_url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with Image.open(io.BytesIO(img_data)) as img:
                        img = img.convert('RGB')  # Convertir l'image en RGB
                        img = img.resize((100, 100))  # Redimensionner l'image pour le traitement
                        colors = img.getcolors(maxcolors=1000000)  # Récupérer les couleurs
                                               

                        # Assurez-vous que la liste de couleurs n'est pas vide
                        if colors:
                            most_common_color = max(colors, key=lambda x: x[0])[1]  # Obtenir la couleur la plus fréquente
                        else:
                            most_common_color = (0, 0, 0)  # Valeur par défaut si aucune couleur trouvée

                    # Vérifier si most_common_color est bien un tuple de trois éléments
                    if isinstance(most_common_color, tuple) and len(most_common_color) == 3:
                        dominant_color = discord.Color.from_rgb(most_common_color[0], most_common_color[1], most_common_color[2])
                        embed.color = dominant_color  # Mettre à jour la couleur de l'embed
                    else:
                        embed.color = discord.Color(0x808080)  # Couleur par défaut si erreur

        embed.set_image(url=user_info.banner.url)
        await ctx.send(embed=embed)
    else:
        
        await ctx.send(embed=discord.Embed(
        description=f"<:warn:1297301606362251406> : {user.mention} has no defined banner.",
        color=discord.Color.red()
))


@bot.command(name='sbanner', aliases=['serverbanner'])
async def sbanner(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # Utiliser l'utilisateur qui exécute la commande si aucun membre n'est mentionné

    # Vérifier si l'utilisateur a une bannière de serveur
    if member.guild_banner:  # Cette méthode est supportée dans la version dev
        banner_url = member.guild_banner.url
        
        # Télécharger et analyser l'image de la bannière pour extraire la couleur dominante
        async with aiohttp.ClientSession() as session:
            async with session.get(banner_url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with Image.open(io.BytesIO(img_data)) as img:
                        img = img.convert('RGB')  # Convertir l'image en RGB
                        img = img.resize((100, 100))  # Redimensionner l'image pour optimiser le traitement
                        colors = img.getcolors(maxcolors=1000000)  # Récupérer les couleurs dominantes

                        if colors:
                            most_common_color = max(colors, key=lambda x: x[0])[1]  # Obtenir la couleur la plus fréquente
                        else:
                            most_common_color = (128, 128, 128)  # Couleur par défaut (gris)

                    # Vérifier si most_common_color est bien un tuple de trois éléments
                    if isinstance(most_common_color, tuple) and len(most_common_color) == 3:
                        dominant_color = discord.Color.from_rgb(most_common_color[0], most_common_color[1], most_common_color[2])
                    else:
                        dominant_color = discord.Color(0x808080)  # Couleur par défaut si erreur

        # Créer l'embed avec la couleur dominante
        embed = discord.Embed(title=f"{member.display_name}'s Server Banner", color=dominant_color)
        embed.set_image(url=banner_url)  # Ajouter l'URL de la bannière de serveur
        await ctx.send(embed=embed)

    else:
        # Ici, assurez-vous que ce bloc est bien indenté pour qu'il ne s'exécute que si l'utilisateur n'a pas de bannière
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.display_name} doesn't have a server banner.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


#IMG & LENS 

NSFW_REGEX = re.compile(r"\b(porn|nsfw|18\+|adult|xxx|nude|sex|explicit)\b", re.IGNORECASE)

def contains_nsfw(content):
    return NSFW_REGEX.search(content) is not None

@bot.command(name='img', aliases=['search', 'image'])
async def img(ctx, *, query=None):
    """Search for images based on the query, with NSFW filtering."""

    if not query:
        embed = discord.Embed(
            title="Command name: img",
            description='Search for images on Google based on a query.',
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )

        embed.add_field(
            name="Aliases", 
            value="search, image", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="query", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {ctx.prefix}img <query>\n"
                  f"Example: {ctx.prefix}img cats```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: misc.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return  # Terminer ici si aucun argument n'est fourni

    if contains_nsfw(query):
        if not ctx.channel.is_nsfw():
            embed_nsfw = discord.Embed(
                description=f"<:warn:1297301606362251406> : Blocked search. No NSFW allowed in this channel.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed_nsfw)

    # Appel à l'API Google Custom Search pour rechercher des images
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    all_results = []  # Stocker tous les résultats
    start = 1  # Le premier résultat commence à l'index 1

    while len(all_results) < 50:  # Limiter à 50 résultats
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "q": query,
                "searchType": "image",
                "key": api_key,
                "cx": cse_id,
                "safe": "high",  # SafeSearch activé
                "imgType": "photo",  # Recherche uniquement des photos (images réalistes)
                "start": start  # Paginer les résultats
            }
        )

        if response.status_code != 200:
            return await ctx.send(f"Error: {response.status_code} - {response.text}")

        data = response.json().get('items', [])
        if not data:
            break  # Arrêter si aucun résultat supplémentaire n'est disponible

        all_results.extend(data)  # Ajouter les résultats
        start += 10  # Passer au prochain bloc de 10 résultats

    if not all_results:
        return await ctx.send(f"No results were found for **{query}**")

    total_images = len(all_results)
    index = 0

    def get_embed_for_image(i):
        item = all_results[i]
        embed = discord.Embed(
            title=f"{ctx.author.display_name} | {item.get('title', 'No Title')}",
            url=item.get('link'),
            description=item.get('snippet', 'No description available.'),
            color=discord.Color(0x808080)
        )

        # Vérification de l'URL de l'image
        image_url = item.get('link')  # Utilisation de 'link' pour récupérer l'URL de l'image
        if image_url:
            embed.set_image(url=image_url)
        else:
            embed.set_footer(text="No valid image found.")

        embed.set_footer(
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/2048px-Google_%22G%22_logo.svg.png",
            text=f"Image {i + 1}/{total_images} - SafeSearch : On"
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        return embed

    # Créer la vue pour les boutons
    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary)
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary)
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def update_embed(interaction):
        nonlocal index
        embed = get_embed_for_image(index)
        await interaction.response.edit_message(embed=embed, view=buttons)

    async def previous_callback(interaction):
        nonlocal index
        if interaction.user == ctx.author:
            index = (index - 1) % total_images
            await update_embed(interaction)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    async def next_callback(interaction):
        nonlocal index
        if interaction.user == ctx.author:
            index = (index + 1) % total_images
            await update_embed(interaction)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    async def close_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.message.delete()
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    # Envoi initial de l'embed
    embed = get_embed_for_image(index)
    await ctx.send(embed=embed, view=buttons)


#lens


@bot.command(name='lens')
async def lens(ctx):
    current_prefix = load_prefix(ctx.guild.id)
    """Analyze an image from a quoted message or embed and search it on Google with interactive buttons."""
    
    # Si la commande est appelée sans citer un message
    if not ctx.message.reference:
        embed_help = discord.Embed(
            title="Command name: Lens",
            description='Analyze an image using Google Lens. Please quote a message with an image or embed containing an image.',
            color=discord.Color(0x808080)
        )

        embed_help.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed_help.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed_help.add_field(
            name="Parameters", 
            value="N/A",  # Pas de paramètres à part le message cité
            inline=False
        )

        embed_help.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        embed_help.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}lens <image>\n"
                  f"Example:{current_prefix}lens image ```",
            inline=False
        )

        # Ajout du footer avec l'heure et le module
        embed_help.set_footer(
            text=f"Page 1/1 | Module: misc.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed_help)
        return

    # Récupère le message cité
    quoted_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

    # Vérifie si le message cité contient une image directe dans les attachments
    image_url = None
    if quoted_message.attachments and quoted_message.attachments[0].url:
        image_url = quoted_message.attachments[0].url

    # Si aucune image n'a été trouvée dans les attachments, vérifie s'il s'agit d'un lien Discord
    if not image_url and quoted_message.content and "https://cdn.discordapp.com/" in quoted_message.content:
        image_url = quoted_message.content.strip()

    # Vérifie s'il y a un embed dans le message cité contenant une image
    if not image_url and quoted_message.embeds:
        for embed in quoted_message.embeds:
            if embed.image and embed.image.url:
                image_url = embed.image.url
                break

    # Si aucune image n'a été trouvée
    if not image_url:
        embed_no_image = discord.Embed(
            description=f"<:warn:1297301606362251406> : The quoted message does not contain any valid images.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed_no_image)

    # Appel à l'API SerpAPI pour analyser l'image
    response = requests.get(
        "https://serpapi.com/search",
        params={
            "engine": "google_lens",
            "url": image_url,
            "api_key": os.getenv("LENS_API"),  # Remplace par ta clé API
        },
    )

    if response.status_code != 200:
        embed_error = discord.Embed(
            description=f"<:warn:1297301606362251406> Error: {response.status_code} - {response.text}",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed_error)

    data = response.json().get('visual_matches', [])
    if not data:
        embed_no_matches = discord.Embed(
            description=f"<:warn:1297301606362251406> : No visual matches were found for the image.",
            color=discord.Color.orange()
        )
        return await ctx.send(embed=embed_no_matches)

    total_images = len(data)
    index = 0

    # Fonction pour créer l'embed avec la bonne image et l'utilisateur
    def get_embed_for_image(i):
        item = data[i]
        embed = discord.Embed(
            title=f"Google Lens Result {i + 1}/{total_images}",
            url=item.get('link'),
            description=item.get('title', 'No Title'),
            color=discord.Color(0x808080)
        ).set_image(url=item.get('thumbnail'))  # Utilise l'image du résultat ici
        embed.set_footer(text=f"Result {i + 1}/{total_images}")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        return embed

    # Créer la vue pour les boutons
    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=True)
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(total_images == 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def update_embed(interaction):
        nonlocal index
        embed = get_embed_for_image(index)
        previous_button.disabled = (index == 0)
        next_button.disabled = (index == total_images - 1)
        await interaction.response.edit_message(embed=embed, view=buttons)

    async def previous_callback(interaction):
        nonlocal index
        if interaction.user == ctx.author:  # Vérifie que l'interaction vient de l'auteur
            if index > 0:
                index -= 1
                await update_embed(interaction)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    async def next_callback(interaction):
        nonlocal index
        if interaction.user == ctx.author:  # Vérifie que l'interaction vient de l'auteur
            if index < total_images - 1:
                index += 1
                await update_embed(interaction)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    async def close_callback(interaction):
        if interaction.user == ctx.author:  # Vérifie si l'utilisateur qui interagit est celui qui a exécuté la commande
            await interaction.message.delete()
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    # Envoi initial de l'embed
    embed = get_embed_for_image(index)
    await ctx.send(embed=embed, view=buttons)

#Translator 

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")  # Remplace par ta clé API

@bot.command(name='translate', aliases=['tr'])
async def translate(ctx, lang: str = None, *, text: str = None):
    current_prefix = load_prefix(ctx.guild.id)

    # Afficher un message d'aide si aucun argument n'est fourni
    if lang is None and text is None:
        embed = discord.Embed(
            title="Command name: Translate",
            description='Translate a message from a language to another.',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="tr",  # Alias de la commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="lang, text", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        # Bloc combiné pour Syntax et Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}translate <language> <text>\n"
                  f"Example: {current_prefix}tr fr I love cats```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: misc.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return  # On arrête l'exécution ici si aucun argument n'est fourni

    # Vérifier si l'utilisateur a cité un message
    if ctx.message.reference:
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        text = referenced_message.content  # Utiliser le contenu du message cité si aucun texte n'est fourni

    if text is None:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : Please provide a text to be translated. Use the format: `{current_prefix}translate <language> <text>` or reply to a message.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return

    # Appel à l'API DeepL pour traduire le texte
    try:
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": lang.upper()  # Langue de destination (en majuscule, ex: 'FR' pour français)
        }
        
        response = requests.post(url, data=params)
        result = response.json()

        if "translations" in result:
            translation = result['translations'][0]['text']
            embed = discord.Embed(
                description=f"<:approve:1297301591698706483> : **Translated to {lang.upper()}** - {translation}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            raise Exception("Translation error")

    except Exception as e:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> An error has occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


#TIMEZONE 

# Configuration de MongoDB
OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')  # Remplace avec ta clé API Opencage

# Connexion à MongoDB
guild_collection = db['guild_timezones']

# Fonction pour charger le fuseau horaire de l'utilisateur depuis MongoDB
async def load_timezone(guild_id, user_id):
    guild_data = guild_collection.find_one({"guild_id": guild_id})
    if guild_data:
        user_timezone = guild_data.get('timezones', {}).get(str(user_id))
        return user_timezone
    return None

# Fonction pour sauvegarder le fuseau horaire de l'utilisateur dans MongoDB
async def save_timezone(guild_id, user_id, timezone_str):
    # On cherche si la guild existe déjà dans la base
    guild_data = guild_collection.find_one({"guild_id": guild_id})
    
    # Si la guild n'existe pas encore, on la crée avec un dictionnaire vide pour les fuseaux horaires
    if not guild_data:
        guild_data = {"guild_id": guild_id, "timezones": {}}
    
    # On met à jour ou on ajoute le fuseau horaire de l'utilisateur
    guild_data['timezones'][str(user_id)] = timezone_str
    
    # Mise à jour ou insertion dans MongoDB
    guild_collection.update_one({"guild_id": guild_id}, {"$set": guild_data}, upsert=True)

@bot.command(name='tz', aliases=['set_timezone', 'set_tz', 'timezone'])
async def timezone(ctx, user: discord.User = None, *, city: str = None):
    guild_id = str(ctx.guild.id)
    user_id = str(user.id if user else ctx.author.id)  # Utiliser l'ID de l'utilisateur mentionné ou celui de l'auteur
    
    current_prefix = load_prefix(ctx.guild.id)

    # Si une ville n'est pas spécifiée et un utilisateur est mentionné
    if city is None and user:
        timezone_str = await load_timezone(guild_id, user_id)
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)

            # Format de l'heure en anglais (AM/PM)
            time_str = now.strftime('%I:%M %p')
            # Format de la date en dd/mm/yyyy
            date_str = now.strftime('%d/%m/%Y')

            embed = discord.Embed(
                description=f"🕒 {user.mention}'s current date is **{date_str}**, **{time_str}**",
                color=discord.Color(0x808080)
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : {user.mention} has not defined their timezone yet.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        return

    # Si aucune ville n'est spécifiée (utilisateur actuel)
    if city is None:
        timezone_str = await load_timezone(guild_id, user_id)
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)

            # Format de l'heure en anglais (AM/PM)
            time_str = now.strftime('%I:%M %p')
            # Format de la date en dd/mm/yyyy
            date_str = now.strftime('%d/%m/%Y')

            embed = discord.Embed(
                description=f"🕒 Your current date is **{date_str}**, **{time_str}**",
                color=discord.Color(0x808080)
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : Please define your timezone using `{current_prefix}tz [city]`. Example: `{current_prefix}tz Paris`. ",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        return

    # Utilisation de l'API Opencage pour obtenir les informations de fuseau horaire
    url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={OPENCAGE_API_KEY}'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_data = await response.json()

    # Vérification de la réponse de l'API
    if response_data['results']:
        location = response_data['results'][0]['geometry']
        latitude = location['lat']
        longitude = location['lng']

        # Utilisation de TimezoneFinder pour récupérer le fuseau horaire en fonction de la latitude et longitude
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

        if timezone_str:
            await save_timezone(guild_id, user_id, timezone_str)
            
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)

            # Format de l'heure en anglais (AM/PM)
            time_str = now.strftime('%I:%M %p')
            # Format de la date en dd/mm/yyyy
            date_str = now.strftime('%d/%m/%Y')

            embed = discord.Embed(
                title="",
                description=f"🗺️ : {('Your' if user is None else user.mention + "'s")} timezone is now set to **{timezone_str}**.\n"
                            f"🕒 Current time : **{time_str}**\n"
                            f"📆 Current date : **{date_str}**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            error_embed = discord.Embed(
                title="",
                description=f"<:warn:1297301606362251406> : Could not determine timezone for {city}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
    else:
        error_embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : City not found. Please enter a valid city.",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)


#steal 
@bot.group(name="steal")
@commands.has_permissions(administrator=True)
async def steal(ctx, emoji: discord.PartialEmoji = None):
    current_prefix = load_prefix(ctx.guild.id)
    
    # Si l'emoji n'est pas fourni, afficher l'aide de la commande steal
    if not emoji:
        embed = discord.Embed(
                    title="Command name: steal",
                    description='Steal emoji from others servers and add them to yours.',
                    color=discord.Color(0x808080)  # Couleur gris foncé
                )

        embed.set_author(
                    name=f"{bot.user.name}",  # Nom du bot
                    icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
                )

        embed.add_field(
                    name="Aliases", 
                    value="N/A",  # Alias de la commande
                    inline=False
                )

        embed.add_field(
                    name="Parameters", 
                    value="emoji", 
                    inline=False
                )

        embed.add_field(
                    name="Permissions", 
                    value="N/A", 
                    inline=False
                )

                # Bloc combiné pour Syntax et Example
        embed.add_field(
                    name="Usage", 
                    value=f"```Syntax: {current_prefix}steal <emoji>\n"
                        f"Example: {current_prefix}steal emoji```",
                    inline=False
                )

                # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
                    text=f"Page 1/1 | Module: misc.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)            
        return

    # Essayez de voler et d'ajouter l'emoji personnalisé
    try:
        guild = ctx.guild  # Le serveur actuel
        emoji_url = emoji.url  # URL de l'emoji (basée sur son identifiant)
        emoji_name = emoji.name  # Nom de l'emoji

        # Récupération de l'image de l'emoji avec aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(str(emoji_url)) as response:
                if response.status == 200:
                    image_data = await response.read()
                    # Ajout de l'emoji au serveur avec le même nom
                    new_emoji = await guild.create_custom_emoji(name=emoji_name, image=image_data)

                    embed = discord.Embed(
                        description=f"<:approve:1297301591698706483> : The {new_emoji} emoji has been successfully added to the server!",
                        color=discord.Color.green()
                    )
                    await ctx.send(embed=embed)
                else:
                    raise Exception(f"<:warn:1297301606362251406> : Error retrieving emoji.")
    except discord.HTTPException:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Failed to add emoji. The server may have reached its emoji limit.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> An error has occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command(name='enlarge', aliases=['e'])
async def enlarge(ctx, emoji: str = None):
    if not emoji:
        # Create the help embed
        embed = discord.Embed(
            title="Command name: enlarge",
            description='Enlarge an emoji',
            color=discord.Color(0x808080)  # Dark gray color
        )

        embed.set_author(
            name=bot.user.name,  # Bot's name
            icon_url=bot.user.avatar.url  # Bot's avatar
        )

        embed.add_field(
            name="Aliases", 
            value="e",  # Alias for the command
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="emoji", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        # Combined block for Syntax and Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {ctx.prefix}enlarge <emoji>\n"
                  f"Example: {ctx.prefix}enlarge :smiley:```",
            inline=False
        )

        # Footer with pagination, module, and time
        embed.set_footer(
            text=f"Page 1/1 | Module: misc.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Extract the emoji ID from the input
    emoji_id = emoji.split(':')[-1][:-1]  # Extract ID
    guild_emoji = discord.utils.get(ctx.guild.emojis, id=int(emoji_id))

    if guild_emoji:
        # Determine if the emoji is animated
        if guild_emoji.animated:
            # Construct the URL for the enlarged animated emoji
            enlarged_emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif?size=1024"
        else:
            # Construct the URL for the enlarged static emoji
            enlarged_emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png?size=1024"

        # Send the enlarged emoji
        await ctx.send(enlarged_emoji_url)
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : This emoji does not exist on this server.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


genius_api_key = os.getenv("GENIUS_API_KEY")

@bot.command(name="lyrics")
async def lyrics(ctx, *, title):
    genius_api = lyricsgenius.Genius("genius_api_key")
    song = genius_api.search_song(title)
    
    if song:
        # Check the length of the lyrics
        lyrics_text = song.lyrics
        if len(lyrics_text) > 2000:
            # Send the first 2000 characters
            lyrics_text = lyrics_text[:2000] + "\n... (lyrics truncated)"
        
        embed = discord.Embed(title=song.title, description=lyrics_text, color=discord.Color(0x808080))
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(description="**Song not found.**", color=discord.Color.red()))


#bday

birthdays_collection = db["birthdays"]

@bot.group(name="birthday", aliases=["bday"], invoke_without_command=True)
async def birthday(ctx):
    current_prefix = load_prefix(ctx.guild.id)
    user_id = ctx.author.id
    user_birthday = birthdays_collection.find_one({"user_id": user_id})

    # Check if the user has set a birthday
    if not user_birthday:
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : You haven't set your birthday yet! Use `{current_prefix}birthday set dd/mm` to set it.",
            color=0xFF0000  # Error color
        ))
        return

    # Retrieve and display the birthday with days remaining
    bday_str = user_birthday["birthday"]
    bday_date = datetime.strptime(bday_str, "%d/%m")
    today = datetime.now()

    # Check if today is the user's birthday
    if today.day == bday_date.day and today.month == bday_date.month:
        embed = discord.Embed(
            description="🎉 Your birthday is today! **Happy Birthday!** 🎂",
            color=0xFFFF00  # Yellow for celebration
        )
        await ctx.send(embed=embed)
        return

    # Calculate days until next birthday
    next_bday = bday_date.replace(year=today.year)
    if next_bday < today:
        next_bday = next_bday.replace(year=today.year + 1)
    
    # Calculate the difference using relativedelta
    delta = relativedelta(next_bday, today)
    months_remaining = delta.months
    days_remaining = delta.days

    # Create a more intuitive description
    if months_remaining > 0 and days_remaining > 0:
        description = f"🎂 Your birthday is on **{bday_date.strftime('%d/%m')}**, it's in **{months_remaining} month{'s' if months_remaining > 1 else ''} and {days_remaining} day{'s' if days_remaining > 1 else ''}**!"
    elif months_remaining > 0:
        description = f"🎂 Your birthday is on **{bday_date.strftime('%d/%m')}**, it's in **{months_remaining} month{'s' if months_remaining > 1 else ''}**!"
    else:
        description = f"🎂 Your birthday is on **{bday_date.strftime('%d/%m')}**, it's in **{days_remaining} day{'s' if days_remaining > 1 else ''}**!"

    # Embed with improved format
    embed = discord.Embed(description=description, color=0x808080)
    await ctx.send(embed=embed)


# Subcommand to set the birthday
@birthday.command(name="set")
async def set_birthday(ctx, date: str):
    try:
        # Validate and parse the date
        bday_date = datetime.strptime(date, "%d/%m")
    except ValueError:
        await ctx.send(embed=discord.Embed(
            description="<:warn:1297301606362251406> : Invalid date format! Please use `dd/mm`.",
            color=0xFF0000  # Error color
        ))
        return

    # Update or insert user's birthday in the database
    birthdays_collection.update_one(
        {"user_id": ctx.author.id},
        {"$set": {"birthday": bday_date.strftime("%d/%m")}},
        upsert=True
    )

    await ctx.send(embed=discord.Embed(
        description=f"<:approve:1297301591698706483> : Your birthday has been set to {bday_date.strftime('%d/%m')}.",
        color=0x808080
    ))


#weather

WEATHER_API = os.getenv('WEATHER_API')

@bot.command(name="weather", aliases=["meteo"])
async def weather(ctx, *, city: str = None):
    """Commande pour obtenir la météo actuelle dans une ville spécifiée."""
    if city is None:
        # Embed d'aide pour la commande
        embed = discord.Embed(
            title="Command name: weather",
            description="Show weather in a city",
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=bot.user.name,  # Nom du bot
            icon_url=bot.user.avatar.url if bot.user.avatar else None  # Vérifie si l'avatar existe
        )

        embed.add_field(name="Aliases", value="meteo", inline=False)
        embed.add_field(name="Parameters", value="city", inline=False)
        embed.add_field(name="Permissions", value="N/A", inline=False)
        embed.add_field(
            name="Usage",
            value=f"```Syntax: {ctx.prefix}weather <city>\nExample: {ctx.prefix}weather Paris```",
            inline=False,
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: misc.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Requête API OpenWeather
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API,  # Clé API
        "units": "metric",        # Température en degrés Celsius
        "lang": "en"              # Langue de la description
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code == 200:
            # Extraire les données météo
            weather_main = data["weather"][0]["main"]  # Condition principale
            description = data["weather"][0]["description"].capitalize()  # Description détaillée
            temp = data["main"]["temp"]  # Température
            timezone_offset = data["timezone"]  # Décalage horaire en secondes
            city_name = data["name"]  # Nom de la ville
            country = data["sys"]["country"]  # Pays

            # Déterminer s'il fait nuit ou jour
            current_utc = datetime.utcnow() + timedelta(seconds=timezone_offset)
            sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"] + timezone_offset)
            sunset = datetime.utcfromtimestamp(data["sys"]["sunset"] + timezone_offset)
            is_night = current_utc < sunrise or current_utc > sunset

            # Définir les emojis
            emoji_mapping = {
                "Clear": "🌕" if is_night else "☀️",
                "Clouds": "☁️",
                "Drizzle": "🌦️",
                "Rain": "🌧️",
                "Thunderstorm": "⛈️",
                "Snow": "❄️",
                "Mist": "🌫️",
                "Fog": "🌁",
                "Smoke": "💨",
                "Dust": "🌪️",
                "Ash": "🌋",
                "Squall": "🌬️",
                "Tornado": "🌪️",
            }

            emoji = emoji_mapping.get(weather_main, "🌍")

            # Création de l'embed
            embed = discord.Embed(
                title=f"Weather in {city_name}, {country}",
                description=f"{emoji} **{description}**",
                color=discord.Color(0x808080),
            )
            embed.add_field(name="Temperature", value=f"{temp}°C", inline=True)
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name} · Local time: {current_utc.strftime('%H:%M')}"
            )

            await ctx.send(embed=embed)
        else:
            # Gérer les erreurs API (ville introuvable ou autre)
            error_message = data.get("message", "An error occurred.")
            await ctx.send(f"<:warn:1297301606362251406> : Error: {error_message}")

    except Exception as e:
        # Gérer les erreurs inattendues
        await ctx.send(f"<:warn:1297301606362251406> : An unexpected error occurred: {e}")


#define

@bot.command(name="define", aliases=["définir", "defineword"])
async def define(ctx, *, word: str):
    """Commande pour obtenir la définition d'un mot en anglais."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    
    try:
        # Envoie de la requête API
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            definition = data[0]["meanings"][0]["definitions"][0]["definition"]
            part_of_speech = data[0]["meanings"][0]["partOfSpeech"]

            # Création de l'embed
            embed = discord.Embed(
                title=f"Definition of {word.capitalize()}",
                description=f"**{part_of_speech.capitalize()}**\n{definition}",
                color=discord.Color(0x808080)
            )

            # Envoi de l'embed
            await ctx.send(embed=embed)

        else:
            # En cas d'erreur (mot introuvable)
            await ctx.send(f"<:warn:1297301606362251406> Could not find a definition for `{word}`. Please try another word.")
    
    except Exception as e:
        # En cas d'erreur dans la requête ou traitement
        await ctx.send(f"<:warn:1297301606362251406> An error occurred: {e}")

#transcript

credentials = service_account.Credentials.from_service_account_file("client_secret.json")
client = speech.SpeechClient(credentials=credentials)

@bot.command(name="transcribe")
async def transcribe(ctx):
    """Transcribes a quoted audio message into text using Google Cloud Speech-to-Text."""

    # Check if the user quoted a message with an attachment (audio file)
    if not ctx.message.reference:
        embed_error = discord.Embed(
            description="<:warn:1297301606362251406> : Please quote an audio message to transcribe it.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Get the referenced message (the quoted message)
    quoted_message = await ctx.fetch_message(ctx.message.reference.message_id)

    # Check if the quoted message contains an attachment (audio file)
    if len(quoted_message.attachments) == 0:
        embed_error = discord.Embed(
            description="<:warn:1297301606362251406> : The quoted message doesn't contain an audio file.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        return

    # Download the audio file
    audio_url = quoted_message.attachments[0].url
    
    audio_file = await quoted_message.attachments[0].to_file()

    # Save the audio file temporarily
    audio_file_path = "temp_audio.ogg"
    with open(audio_file_path, "wb") as f:
        f.write(audio_file.fp.read())

    # Convert the .ogg file to .wav using pydub with 16-bit depth
    try:
        audio = AudioSegment.from_ogg(audio_file_path)
        wav_audio_path = "temp_audio.wav"
        audio = audio.set_sample_width(2)  # Set sample width to 2 bytes (16-bit)
        audio.export(wav_audio_path, format="wav")
    except Exception as e:
        embed_error = discord.Embed(
            description="<:warn:1297301606362251406> : Sorry, there was an error converting the audio file.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        os.remove(audio_file_path)
        return

    # Get the sample rate of the audio
    sample_rate = audio.frame_rate

    # Read the converted audio file and send it to Google Cloud Speech-to-Text
    with io.open(wav_audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    # Configure the recognition parameters
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,  # Use the actual sample rate from the audio file
        language_code="en-US",  # You can change the language if needed
        audio_channel_count=1,
        enable_automatic_punctuation=True,
    )

    # Send the request to Google Cloud Speech-to-Text
    try:
        response = client.recognize(config=config, audio=audio)
    except Exception as e:
        embed_error = discord.Embed(
            description="<:warn:1297301606362251406> : Sorry, there was an error with the transcription request.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
        os.remove(audio_file_path)
        os.remove(wav_audio_path)
        return

    # If the response contains transcriptions
    if response.results:
        transcript = response.results[0].alternatives[0].transcript
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : **Transcription of the audio - **\n{transcript}",
            color=discord.Color(0x808080)
        )
        await ctx.send(embed=embed)
    else:
        embed_error = discord.Embed(
            description="<:warn:1297301606362251406> : Sorry, I couldn't transcribe the audio.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)

    # Delete the temporary audio files after processing
    os.remove(audio_file_path)
    os.remove(wav_audio_path)


#reminder 

reminders_collection = db["reminder"]

# Commande reminder avec sous-commandes
@bot.group(name="reminder", invoke_without_command=True)
async def reminder(ctx, duration: str = None):
    """Set a reminder for the given duration"""

    if duration is None:
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
            embed.add_field(name="Parameters", value="duration", inline=False)
            embed.add_field(name="Permissions", value=f"N/A", inline=False)

            return embed

        # Pages d'usage
        pages = [
            {
                "title": "Command name: reminder",
                "description": "Set a reminder for the given duration.",
                "usage": f"```Syntax: {ctx.prefix}reminder <duration> <sentence>  \n"
                          f"Example: {ctx.prefix}reminder 1h cook```",
                "footer": "Page 1/2"
            },
            {
                "title": "Command name: reminder delete",
                "description": "Delete the reminder for the user.",
                "usage": f"```Syntax: {ctx.prefix}reminder delete \n"
                          f"Example: {ctx.prefix}reminder delete```",
                "footer": "Page 2/2"
            },
        ]

        # Fonction pour changer d'embed
        async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: misc.py • {ctx.message.created_at.strftime('%H:%M')}")
            await interaction.response.edit_message(embed=embed)

        buttons = await create_buttons(ctx, pages, update_embed, current_time)

        # Envoi de l'embed initial
        initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
        initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
        initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: misc.py • {ctx.message.created_at.strftime('%H:%M')}")

        await ctx.send(embed=initial_embed, view=buttons)
        return

    # Si une durée est donnée, on l'utilise pour créer ou mettre à jour un rappel
    try:
        # Convertir la durée en secondes (gestion des jours, heures, minutes)
        days = 0
        hours = 0
        minutes = 0
        seconds = 0

        if "d" in duration:
            days = int(duration.split("d")[0])  # Extraire les jours
            duration = duration.split("d")[1]  # Enlever les jours

        if "h" in duration:
            hours = int(duration.split("h")[0])  # Extraire les heures
            duration = duration.split("h")[1]  # Enlever les heures

        if "m" in duration:
            minutes = int(duration.split("m")[0])  # Extraire les minutes
            duration = duration.split("m")[1]  # Enlever les minutes

        if "s" in duration:
            seconds = int(duration.split("s")[0])  # Extraire les secondes

        total_seconds = (days * 86400) + (hours * 3600) + (minutes * 60) + seconds  # Conversion en secondes

        # Vérification si la durée dépasse 28 jours (28 jours = 28 * 24 * 3600 = 2419200 secondes)
        if total_seconds > 2419200:
            embed_error = discord.Embed(
                description="<:warn:1297301606362251406> :  Error: Your reminder cannot exceed 28 days.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_error)
            return

        # Vérifier si l'utilisateur a déjà un rappel et le supprimer s'il existe
        existing_reminder = reminders_collection.find_one({"guild_id": str(ctx.guild.id), "user_id": str(ctx.author.id)})

        if existing_reminder:
            # Supprimer l'ancien rappel
            reminders_collection.delete_one({"_id": existing_reminder["_id"]})

        # Ajouter le rappel dans la base de données
        reminder_time = datetime.utcnow() + timedelta(seconds=total_seconds)
        reminder_data = {
            "guild_id": str(ctx.guild.id),
            "user_id": str(ctx.author.id),
            "reminder_time": reminder_time,
            "created_at": datetime.utcnow()
        }

        # Insérer dans MongoDB
        reminders_collection.insert_one(reminder_data)

        # Réponse de confirmation avec la durée relative
        embed = discord.Embed(
            title="Reminder Set",
            description=f"Your reminder has been set for **{format_time(total_seconds)}**!",
            color=discord.Color(0x808080)
        )
        embed.add_field(
            name="Reminder in",
            value=f"Your reminder will trigger in: **{format_time(total_seconds)}**",
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed_error = discord.Embed(
            description=f"<:warn:1297301606362251406> :  {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)

# Sous-commande delete pour supprimer un rappel
@reminder.command(name="delete")
async def delete_reminder(ctx):
    """Delete the reminder for the user"""

    # Rechercher un rappel existant pour cet utilisateur
    existing_reminder = reminders_collection.find_one({"guild_id": str(ctx.guild.id), "user_id": str(ctx.author.id)})

    if existing_reminder:
        # Supprimer le rappel
        reminders_collection.delete_one({"_id": existing_reminder["_id"]})

        embed = discord.Embed(
            description="<:approve:1297301591698706483> : Your reminder has been successfully deleted.",
            color=discord.Color(0x808080)
        )
        await ctx.send(embed=embed)
    else:
        embed_error = discord.Embed(
            description=f"<:warn:1297301606362251406> : Error: You don't have any active reminder.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_error)
