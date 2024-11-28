from config import *
from fmconfig import *
from mango import *

import json
import asyncio
import aiohttp

lastfm_ref = db["lastfm_users"]  

async def load_lastfm_users(guild_id):
    doc = lastfm_ref.find_one({"_id": guild_id})
    if doc:
        return json.loads(doc.get('users', '{}'))
    else:
        return {}

async def save_lastfm_users(guild_id, users):
    data = {
        "users": json.dumps(users)
    }
    lastfm_ref.update_one({"_id": guild_id}, {"$set": data}, upsert=True)
    return True

is_ready = False
lastfm_users = {} 

async def some_async_function(bot, guild_id):
    users = await load_lastfm_users(guild_id)

@bot.event
async def on_ready():
    global lastfm_users, is_ready
    if not is_ready:
        lastfm_users = {}

        for guild in bot.guilds:
            guild_id = str(guild.id)  
            lastfm_users[guild_id] = await load_lastfm_users(guild_id) 

        await bot.change_presence(status=discord.Status.idle, activity=discord.Game("Listening to Last.fm"))

        is_ready = True

#Fm start 
@bot.command(name="linkfm")
async def linkfm(ctx, username: str):
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    if guild_id not in lastfm_users:
        lastfm_users[guild_id] = {}

    lastfm_users[guild_id][user_id] = username
    await save_lastfm_users(guild_id, lastfm_users[guild_id])

    embed = discord.Embed(description=f"<:approve:1297301591698706483> : Your Last.fm account has been successfully linked! Username - {username}", color=0x808080)
    await ctx.send(embed=embed)

@bot.command(name="unlinkfm")
async def unlinkfm(ctx):
    current_prefix = load_prefix(ctx.guild.id)
    guild_id = str(ctx.guild.id)  
    user_id = str(ctx.author.id)

    if guild_id not in lastfm_users or user_id not in lastfm_users[guild_id]:
        embed = discord.Embed(color=0xff0000)
        embed.description = f"<:warn:1297301606362251406> : You haven't linked your Last.fm account yet! Use `{current_prefix}linkfm <username>` to link it."
        await ctx.send(embed=embed)
        return

    del lastfm_users[guild_id][user_id]

    await save_lastfm_users(guild_id, lastfm_users[guild_id])

    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Your Last.fm account has been successfully unlinked!",
        color=0x00ff00
    )
    await ctx.send(embed=embed)


#fm command
@bot.group(name="fm", invoke_without_command=True)
async def fm(ctx, user: discord.User = None):
    current_prefix = load_prefix(ctx.guild.id)

    user = user or ctx.author
    user_id = str(user.id)
    guild_id = str(ctx.guild.id)

    if user_id not in lastfm_users.get(guild_id, {}):
        embed = discord.Embed(color=0xff0000)
        
        if user == ctx.author:
            embed.description = f"<:warn:1297301606362251406> : You have not linked your Last.fm account yet!"
        else:
            embed.description = f"<:warn:1297301606362251406> : {user.mention} hasn't linked their Last.fm account yet! Ask {user.display_name} to link it using `{current_prefix}linkfm <username>`."
        
        await ctx.send(embed=embed)
        return

    username = lastfm_users[guild_id][user_id]

    scrobbles = await get_total_scrobbles(username)
    if scrobbles is None:
        await ctx.send("Unable to fetch the total scrobbles.")
        return

    try:
        url = f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={lastfm_apikey}&format=json&limit=1"
        data = await fetch_with_retry(url)

        if 'recenttracks' not in data or not data['recenttracks']['track']:
            await ctx.send(f"{user.display_name} is not currently playing any track.")
            return

        track = data['recenttracks']['track'][0]
        artist = track['artist']['#text']
        title = track['name']

        user_playcount_task = get_user_track_playcount(username, artist, title)
        album_name_task = get_album_name_from_spotify(artist, title)
        album_cover_task = get_spotify_album_cover(artist, title)

        user_playcount, album_name, album_cover = await asyncio.gather(
            user_playcount_task,
            album_name_task,
            album_cover_task
        )

        embed = discord.Embed(color=0x808080)
        embed.set_author(name=user.display_name, icon_url=user.avatar.url)
        embed.add_field(name="Artist", value=f"[{artist}](https://www.last.fm/music/{urllib.parse.quote(artist)})", inline=True)
        embed.add_field(name="Title", value=f"[{title}](https://www.last.fm/music/{urllib.parse.quote(artist)}/_/{urllib.parse.quote(title)})", inline=True)

        if album_cover:
            embed.set_thumbnail(url=album_cover)
        else:
            embed.add_field(name="Album Cover", value="Unavailable via Spotify", inline=False)

        embed.set_footer(text=f"Play Count: {user_playcount} · Scrobbles: {scrobbles} | Album: {album_name}")

        message = await ctx.send(embed=embed)

        await message.add_reaction("🔥")
        await message.add_reaction("🗑️")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


#wk 

@fm.command(name="wk", aliases = ['whoknows'])
async def wk(ctx, *, artist: str):
    guild_id = str(ctx.guild.id)
    users = lastfm_users.get(guild_id, {})

    if not users:
        await ctx.send(embed=discord.Embed(
            description=f" <:warn:1297301606362251406> : No Last.fm accounts are linked in this server.",
            color=discord.Color.red()
        ))
        return

    leaderboard = []

    for username, lastfm_username in users.items():
        playcount = await get_artist_playcount(lastfm_username, artist)
        if playcount > 0:
            leaderboard.append({
                "username": username,
                "lastfm_username": lastfm_username,
                "playcount": playcount
            })

    if not leaderboard:
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : No one in this server has scrobbled **{artist}**.",
            color=discord.Color.red()
        ))
        return

    leaderboard.sort(key=lambda x: x['playcount'], reverse=True)

    # Pagination
    items_per_page = 8
    total_pages = (len(leaderboard) - 1) // items_per_page + 1
    current_page = 0

    artist_image_url = None
    try:
        results = spotify.search(q=artist, type='artist', limit=1)
        if results['artists']['items']:
            artist_image_url = results['artists']['items'][0]['images'][0]['url']
    except Exception as e:
        print(f"Erreur Spotify : {e}")

    async def create_leaderboard_embed(current_page, total_pages, author):
        start = current_page * items_per_page
        end = start + items_per_page
        page_data = leaderboard[start:end]

        embed = discord.Embed(
            title=f"Leaderboard for {artist}",
            color=discord.Color(0x808080)
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        for idx, user_data in enumerate(page_data, start=start + 1):
            profile_url = f"https://www.last.fm/user/{user_data['lastfm_username']}"
            embed.add_field(
                name=f"",
                value=f"``#{idx}`` **[{user_data['lastfm_username']}]({profile_url})**\n Playcount: {user_data['playcount']}",
                inline=False
            )

        if artist_image_url:
            embed.set_thumbnail(url=artist_image_url)

        embed.set_footer(text=f"Page {current_page + 1} of {total_pages} | {len(leaderboard)} total users")
        return embed

    embed = await create_leaderboard_embed(current_page, total_pages, ctx.author)
    message = await ctx.send(embed=embed)

    if len(leaderboard) > items_per_page:
        buttons = discord.ui.View(timeout=60)
        previous_button = discord.ui.Button(
            emoji="<:previous:1297292075221389347>", 
            style=discord.ButtonStyle.primary, 
            disabled=(current_page == 0)
        )
        next_button = discord.ui.Button(
            emoji="<:next:1297292115688292392>", 
            style=discord.ButtonStyle.primary, 
            disabled=(current_page == total_pages - 1)
        )
        close_button = discord.ui.Button(
            emoji="<:cancel:1297292129755861053>", 
            style=discord.ButtonStyle.danger
        )

    async def update_embed():
        embed = await create_leaderboard_embed(current_page, total_pages, ctx.author)
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
            await interaction.response.send_message(embed=discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                color=discord.Color.red()), ephemeral=True)

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

    async def close_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(embed=discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this message.",
                color=discord.Color.red()), ephemeral=True)

    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    await message.edit(view=buttons)


#cover 

@fm.command(name="cover")
async def fmcover(ctx, user: discord.User = None):
    current_prefix = load_prefix(ctx.guild.id)
    user = user or ctx.author
    user_id = str(user.id)
    guild_id = str(ctx.guild.id)

    if user_id not in lastfm_users.get(guild_id, {}):
        embed = discord.Embed(color=0xff0000)
        
        if user == ctx.author:
            embed.description = f"<:warn:1297301606362251406> : You have not linked your Last.fm account yet!"
        else:
            embed.description = f"<:warn:1297301606362251406> : {user.mention} hasn't linked their Last.fm account yet! Ask {user.display_name} to link it using `{current_prefix}linkfm <username>`."
        
        await ctx.send(embed=embed)
        return

    username = lastfm_users[guild_id][user_id]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={lastfm_apikey}&format=json&limit=1") as response:
            data = await response.json()

            if 'recenttracks' not in data or not data['recenttracks']['track']:
                await ctx.send(f"{user.mention} is not currently playing any track.")
                return

            track = data['recenttracks']['track'][0]
            artist = track['artist']['#text']
            title = track['name']

            album_cover = await get_spotify_album_cover(artist, title)

            embed = discord.Embed(color=0x808080)

            embed.set_author(name=username, icon_url=user.avatar.url)

            embed.add_field(name="Artist", value=f"[{artist}](https://www.last.fm/music/{urllib.parse.quote(artist)})", inline=True)
            embed.add_field(name="Title", value=f"[{title}](https://www.last.fm/music/{urllib.parse.quote(artist)}/_/{urllib.parse.quote(title)})", inline=True)

            if album_cover:
                embed.set_image(url=album_cover)
            else:
                embed.add_field(name="Album Cover", value="Album cover is unavailable via Spotify.", inline=False)

            footer_text = f"{ctx.author.name} | Module : fm.py"
            embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed)


#top artist

@fm.command(name="topartists", aliases=['topartist'])
async def fmtopartists(ctx, user: discord.User = None):
    current_prefix = load_prefix(ctx.guild.id)
    user = user or ctx.author  
    user_id = str(user.id)
    guild_id = str(ctx.guild.id)

    if user_id not in lastfm_users.get(guild_id, {}):
        embed = discord.Embed(color=0xff0000)
        
        if user == ctx.author:
            embed.description = f"<:warn:1297301606362251406> : You have not linked your Last.fm account yet!"
        else:
            embed.description = f"<:warn:1297301606362251406> : {user.mention} hasn't linked their Last.fm account yet! Ask {user.display_name} to link it using `{current_prefix}linkfm <username>`."
        
        await ctx.send(embed=embed)
        return

    username = lastfm_users[guild_id][user_id]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={username}&api_key={lastfm_apikey}&format=json&limit=5") as response:
            data = await response.json()

            if 'topartists' not in data or not data['topartists']['artist']:
                await ctx.send("Unable to retrieve the top artists.")
                return

            embed = discord.Embed(title=f"Top Artists of {username}", color=0x808080)

            top_artist = data['topartists']['artist'][0]
            top_artist_name = top_artist['name']
            artist_cover_url = await get_artist_cover(top_artist_name) 

            if artist_cover_url:
                embed.set_thumbnail(url=artist_cover_url)

            for i, artist in enumerate(data['topartists']['artist'][:5]):
                artist_name = artist['name']
                playcount = artist['playcount']
                
                artist_url = f"https://www.last.fm/fr/music/{urllib.parse.quote(artist_name)}"
                
                embed.add_field(
                    name=f"",
                    value=f"``#{i + 1}`` **[{artist_name}]({artist_url})** - Play Count: {playcount}",
                    inline=False
                )

            footer_text = f"{ctx.author.name} | Module : fm.py"
            embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed)


#toptrack

@fm.command(name="toptracks", aliases=["toptrack"])
async def fmtoptracks(ctx, user: discord.User = None):
    current_prefix = load_prefix(ctx.guild.id)
    user = user or ctx.author 
    user_id = str(user.id)
    guild_id = str(ctx.guild.id)

    if user_id not in lastfm_users.get(guild_id, {}):
        embed = discord.Embed(color=0xff0000)
        
        if user == ctx.author:
            embed.description = f"<:warn:1297301606362251406> : You have not linked your Last.fm account yet!"
        else:
            embed.description = f"<:warn:1297301606362251406> : {user.mention} hasn't linked their Last.fm account yet! Ask {user.display_name} to link it using `{current_prefix}linkfm <username>`."
        
        await ctx.send(embed=embed)
        return

    username = lastfm_users[guild_id][user_id]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={username}&api_key={lastfm_apikey}&format=json&limit=5") as response:
            data = await response.json()

            if 'toptracks' not in data or not data['toptracks']['track']:
                await ctx.send("Unable to retrieve the top tracks.")
                return

            embed = discord.Embed(title=f"Top Tracks of {username}", color=0x808080)

            for i, track in enumerate(data['toptracks']['track'][:5]):
                track_name = track['name']
                artist_name = track['artist']['name']
                playcount = track['playcount']

                track_info = f"**{track_name}** by **{artist_name}**\nPlay Count: {playcount}"

                track_url = f"https://www.last.fm/music/{urllib.parse.quote(artist_name)}/_/{urllib.parse.quote(track_name)}"
                artist_url = f"https://www.last.fm/music/{urllib.parse.quote(artist_name)}"

                embed.add_field(
                    name=f"",
                    value=f"``#{i + 1}`` **[{track_name}]({track_url})** by **[{artist_name}]({artist_url})**\nPlay Count: {playcount}",
                    inline=False
                )

            top_track = data['toptracks']['track'][0]
            top_artist = top_track['artist']['name']
            top_track_name = top_track['name']
            album_cover = await get_spotify_album_cover(top_artist, top_track_name)

            if album_cover:
                embed.set_thumbnail(url=album_cover)

            footer_text = f"{ctx.author.name} | Module : fm.py"
            embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed)


#topalbum 

@fm.command(name="topalbums", aliases=['topalbum'])
async def fmtopalbums(ctx, user: discord.User = None):
    current_prefix = load_prefix(ctx.guild.id)
    user = user or ctx.author  
    user_id = str(user.id) 
    guild_id = str(ctx.guild.id)

    if user_id not in lastfm_users.get(guild_id, {}):
        embed = discord.Embed(color=0xff0000)
        
        if user == ctx.author:
            embed.description = f"<:warn:1297301606362251406> : You have not linked your Last.fm account yet!"
        else:
            embed.description = f"<:warn:1297301606362251406> : {user.mention} hasn't linked their Last.fm account yet! Ask {user.display_name} to link it using `{current_prefix}linkfm <username>`."
        
        await ctx.send(embed=embed)
        return

    username = lastfm_users[guild_id][user_id]
    
    albums = await get_top_albums(username)

    if albums is None:
        embed = discord.Embed(color=0xff0000)
        embed.description = "Unable to retrieve the top listened albums."
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title=f"Top Albums by {user.name}", color=0x808080)

    for i, album in enumerate(albums[:5]):  
        album_name = album['name']
        artist_name = album['artist']['name']
        playcount = album['playcount']
        album_url = f"https://www.last.fm/music/{urllib.parse.quote(artist_name)}/_/{urllib.parse.quote(album_name)}"
        artist_url = f"https://www.last.fm/music/{urllib.parse.quote(artist_name)}"
        image_url = album['image'][3]['#text'] 

        if album_url:
            album_field = f"[**{album_name}**]({album_url}) by **[{artist_name}]({artist_url})**"
        else:
            album_field = f"**{album_name}** by **[{artist_name}]({artist_url})**" 

        embed.add_field(
            name=f"",
            value=f"``#{i + 1}``{album_field}\n Play Count: {playcount}",
            inline=False
        )

        if image_url and i == 0:
            embed.set_thumbnail(url=image_url)

    footer_text = f"{ctx.author.name} | Module : fm.py"
    embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


#user
@fm.command(name="user")
async def fmuser(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)
    target_user = member or ctx.author
    user_id = str(target_user.id)
    guild_id = str(ctx.guild.id)

    if user_id not in lastfm_users.get(guild_id, {}):
        embed = discord.Embed(color=0xff0000)
        
        if target_user == ctx.author:
            embed.description = f"<:warn:1297301606362251406> : You have not linked your Last.fm account yet!"
        else:
            embed.description = f"<:warn:1297301606362251406> : {target_user.mention} hasn't linked their Last.fm account yet! Ask {target_user.display_name} to link it using `{current_prefix}linkfm <username>`."
        
        await ctx.send(embed=embed)
        return

    username = lastfm_users[guild_id][user_id]

    user_info = await get_user_info(username)

    if user_info is None:
        embed = discord.Embed(color=0xff0000)
        embed.description = (f"<:warn:1297301606362251406> : Unable to retrieve Last.fm data for {target_user.mention}.")
        await ctx.send(embed=embed)
        return

    playcount = user_info.get('playcount', '0')
    profile_image = user_info.get('image', [{}])[2].get('#text')
    registered = user_info.get('registered', {}).get('unixtime', 'Unknown')

    embed = discord.Embed(title=f"<:lastfm_iconicons:1303143391533469786> Profile: {username}", color=0x808080)

    if profile_image:
        embed.set_thumbnail(url=profile_image)

    embed.add_field(name="Play Count", value=playcount, inline=True)
    embed.add_field(name="Registered On", value=f"<t:{registered}:F>", inline=True)

    footer_text = f"{ctx.author.name} | Module : fm.py"
    embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

#whois