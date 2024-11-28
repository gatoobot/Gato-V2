from config import *

import requests
import instaloader
import http.cookiejar
from datetime import datetime

# Fonction pour formater les nombres
def format_number(num):
    """Format a number to a compact representation (e.g., 1K, 1M, 1B)."""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)

@bot.group(name='insta', aliases=['instagram', 'ig'], invoke_without_command=True)
async def insta(ctx, username: str = None):
    """Fetch Instagram profile data with a username."""
    
    if username is None:
        embed = discord.Embed(
            title="Command name: Instagram",
            description="Fetches Instagram profile data for a given username.",
            color=discord.Color(0x808080)
        )
        
        embed.add_field(
            name="Aliases", 
            value="instagram, ig", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="username", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {ctx.prefix}insta <username>\n"
                  f"Example: {ctx.prefix}insta example_user```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 • Module: socials.py · {ctx.message.created_at.strftime('%H:%M')}"
        )
        
        await ctx.send(embed=embed)
        return

    # Crée un objet Instaloader
    L = instaloader.Instaloader()

    # Crée un CookieJar pour gérer les cookies
    cookies = http.cookiejar.CookieJar()

    # Ajoute les cookies manuellement
    cookie = http.cookiejar.Cookie(
        version=0,
        name="ds_user_id",
        value= os.getenv('DS_USER_ID'),
        port=None,
        port_specified=False,
        domain=".instagram.com",
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=True,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest={}
    )
    cookies.set_cookie(cookie)

    cookie = http.cookiejar.Cookie(
        version=0,
        name="sessionid",
        value= os.getenv('SESSION_ID'),
        port=None,
        port_specified=False,
        domain=".instagram.com",
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=True,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest={}
    )
    cookies.set_cookie(cookie)

    # Charge les cookies dans Instaloader
    L.context._session.cookies = cookies

    try:
        # Récupère le profil Instagram avec Instaloader
        profile = instaloader.Profile.from_username(L.context, username)

        # Récupère les informations du profil
        full_name = profile.full_name if profile.full_name else "N/A"
        followers = format_number(profile.followers)
        following = format_number(profile.followees)
        media_count = format_number(profile.mediacount)
        profile_picture = profile.profile_pic_url if profile.profile_pic_url else "https://via.placeholder.com/150"
        biography = profile.biography if profile.biography else "No biography available"

        # Créer l'embed avec les données du profil
        embed = discord.Embed(
            title=f"Instagram Profile of {username}",
            color=discord.Color(0x808080)
        )
        embed.set_thumbnail(url=profile_picture)
        embed.add_field(name="Followers", value=f"{followers}", inline=True)
        embed.add_field(name="Following", value=f"{following}", inline=True)
        embed.add_field(name="Posts", value=f"{media_count}", inline=True)
        embed.add_field(name="Biography", value=biography, inline=False)

        embed.set_author(
            name=f"{ctx.author.name}",
            icon_url=ctx.author.avatar.url
        )

        current_time = datetime.now().strftime("%H:%M")
        embed.set_footer(
            text=f"Instagram | Today at {current_time}",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred while fetching the Instagram profile for **{username}**: {str(e)}")


@insta.command(name="post")
@commands.cooldown(1, 20, commands.BucketType.user)
async def post(ctx, username: str):
    """Fetch the latest post from an Instagram account, supporting navigation for multi-posts."""
    embed_color = 0x808080  # Default embed color

    try:
        # Initialisation d'Instaloader avec les cookies
        L = instaloader.Instaloader()
        cookies = http.cookiejar.CookieJar()

        # Ajouter les cookies manuellement
        cookie = http.cookiejar.Cookie(
            version=0,
            name="ds_user_id",
            value= os.getenv('DS_USER_ID'),  # Remplace par la valeur de ton ds_user_id
            port=None,
            port_specified=False,
            domain=".instagram.com",
            domain_specified=True,
            domain_initial_dot=False,
            path="/",
            path_specified=True,
            secure=True,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest={}
        )
        cookies.set_cookie(cookie)

        cookie = http.cookiejar.Cookie(
            version=0,
            name="sessionid",
            value= os.getenv('SESSION_ID'),  # Remplace par la valeur de ton sessionid
            port=None,
            port_specified=False,
            domain=".instagram.com",
            domain_specified=True,
            domain_initial_dot=False,
            path="/",
            path_specified=True,
            secure=True,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest={}
        )
        cookies.set_cookie(cookie)
        L.context._session.cookies = cookies

        profile = instaloader.Profile.from_username(L.context, username)

        # Check if the account is private
        if profile.is_private:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : The account **{username}** is private. Unable to fetch the latest post.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        # Retrieve the latest post
        posts = profile.get_posts()
        last_post = next(posts, None)

        if last_post is None:
            embed = discord.Embed(
                description=f" <:warn:1297301606362251406> : The account **{username}** has no posts to display.",
                color=embed_color,
            )
            await ctx.send(embed=embed)
            return

        # Get media URLs (images/videos)
        media_urls = [media.display_url for media in last_post.get_sidecar_nodes()] if last_post.typename == "GraphSidecar" else [last_post.url]
        current_index = 0  # Index to track the current image
        total_images = len(media_urls)

        # Function to create the embed with the correct image
        def create_embed(index):
            embed = discord.Embed(
                title=f"Latest Post from @{username}",
                description=f"[View Post]({last_post.url})",
                color=embed_color,
            )
            embed.set_image(url=media_urls[index])  # Display the current image
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
            embed.set_footer(
                text=f"Image {index + 1}/{total_images} | Instagram | Today at {ctx.message.created_at.strftime('%H:%M')}",
                icon_url="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
            )
            return embed

        # Button system for navigation
        buttons = discord.ui.View(timeout=60)

        previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=True)
        next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(total_images == 1))
        close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

        async def update_embed(interaction):
            nonlocal current_index
            embed = create_embed(current_index)
            previous_button.disabled = (current_index == 0)
            next_button.disabled = (current_index == total_images - 1)
            await interaction.response.edit_message(embed=embed, view=buttons)

        async def previous_callback(interaction):
            nonlocal current_index
            if interaction.user == ctx.author:  # Check if interaction is from the author
                if current_index > 0:
                    current_index -= 1
                    await update_embed(interaction)
            else:
                embed_error = discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed_error, ephemeral=True)

        async def next_callback(interaction):
            nonlocal current_index
            if interaction.user == ctx.author:  # Check if interaction is from the author
                if current_index < total_images - 1:
                    current_index += 1
                    await update_embed(interaction)
            else:
                embed_error = discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed_error, ephemeral=True)

        async def close_callback(interaction):
            if interaction.user == ctx.author:  # Check if the user interacting is the one who executed the command
                await interaction.message.delete()
            else:
                embed_error = discord.Embed(
                    description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed_error, ephemeral=True)

        # Attach callbacks to buttons
        previous_button.callback = previous_callback
        next_button.callback = next_callback
        close_button.callback = close_callback

        buttons.add_item(previous_button)
        buttons.add_item(next_button)
        buttons.add_item(close_button)

        # Send the initial embed with the button view
        embed = create_embed(current_index)
        await ctx.send(embed=embed, view=buttons)

    except instaloader.exceptions.ProfileNotExistsException:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : The account **{username}** does not exist or is invalid.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : An error occurred: {str(e)}",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)


#tiktok

@bot.command(name="tiktok", aliases=["tt"])
async def fetch_tiktok_profile(ctx, username: str = None):
    if not username:

        embed = discord.Embed(
            title="Command name: Tiktok",
            description="Fetches Tiktok profile data for a given username.",
            color=discord.Color(0x808080)
        )
        
        embed.add_field(
            name="Aliases", 
            value="tt", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="username", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {ctx.prefix}tiktok <username>\n"
                  f"Example: {ctx.prefix}tiktok example_user```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 • Module: socials.py · {ctx.message.created_at.strftime('%H:%M')}"
        )
        
        await ctx.send(embed=embed)
        return
        

    url = "https://tiktok-api23.p.rapidapi.com/api/user/info"
    
    # Ajouter le paramètre 'uniqueId' avec la valeur du nom d'utilisateur TikTok
    querystring = {"uniqueId": username}

    headers = {
        "x-rapidapi-key": "f4058aeb55msh5f6c8fff8c7e96cp1a088fjsna1b11e305db5",
        "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        if response.status_code != 200 or "userInfo" not in data:
            await ctx.send(f"Error fetching data for {username}: {data.get('message', 'Unknown error')}")
            return

        user_info = data["userInfo"]["user"]
        stats = data["userInfo"]["stats"]

        embed = discord.Embed(
            title=f"{user_info['nickname']}'s TikTok Stats",
            color=0x808080,
        )
        embed.set_thumbnail(url=user_info['avatarLarger'])
        embed.add_field(name="Username", value=f"[@{user_info['uniqueId']}](" + f"https://www.tiktok.com/@{user_info['uniqueId']})", inline=False)
        embed.add_field(name="Followers", value=f"{stats['followerCount']:,}", inline=False)
        embed.add_field(name="Following", value=f"{stats['followingCount']:,}", inline=False)
        embed.add_field(name="Likes", value=f"{stats['heartCount']:,}", inline=False)
        embed.add_field(name="Videos", value=f"{stats['videoCount']:,}", inline=False)

        embed.set_author(
            name=f"{ctx.author.name}",
            icon_url=ctx.author.avatar.url
        )

        current_time = datetime.now().strftime("%H:%M")
        embed.set_footer(
            text=f"Tiktok | Today at {current_time}",
            icon_url="https://get-picto.com/wp-content/uploads/2024/02/tiktok-logo-noir-et-blanc.webp"
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")