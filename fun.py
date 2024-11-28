from config import *

import re 
import random 
import asyncio 


@bot.command(name='gay')
async def gay(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    gay_percentage = random.randint(0, 100)

    embed = discord.Embed(
        description=f"{user.mention} is **{gay_percentage}%** gay 🌈",
        color=discord.Color(0x808080)  # Gray color for embed
    )

    await ctx.send(embed=embed)


@bot.command(name="love")
async def love(ctx, user1: discord.Member = None, user2: discord.Member = None):
    # Si deux utilisateurs sont mentionnés
    if user1 and user2:
        love_percentage = random.randint(0, 100)
        embed = discord.Embed(
            description=f"💖 : {user1.mention} and {user2.mention} love each other **{love_percentage}%**!",
            color=discord.Color.pink()
        )
    # Si un seul utilisateur est mentionné
    elif user1:
        love_percentage = random.randint(0, 100)
        embed = discord.Embed(
            description=f"💖 : {ctx.author.mention} and {user1.mention} love each other **{love_percentage}%**!",
            color=discord.Color.pink()
        )
    # Si personne n'est mentionné
    else:
        love_percentage = random.randint(0, 100)
        embed = discord.Embed(
            description=f"💖 : {ctx.author.mention}, you love yourself **{love_percentage}%**! 😍",
            color=discord.Color.pink()
        )
    
    await ctx.send(embed=embed)


@bot.command(name="tof")
async def tof(ctx, *, statement=None):
    current_prefix = load_prefix(ctx.guild.id)
    """
    Check if a statement is true or false with a random result.
    """

    # Check if a message is being quoted
    referenced_message = ctx.message.reference
    if referenced_message:  # If a message is quoted
        try:
            # Fetch the quoted message content
            quoted_message = await ctx.channel.fetch_message(referenced_message.message_id)
            statement = quoted_message.content
        except discord.NotFound:
            return await ctx.send(f"<:warn:1297301606362251406> :  The quoted message could not be found.")
        except discord.Forbidden:
            return await ctx.send(f"<:warn:1297301606362251406> :  I do not have permission to access the quoted message.")
        except discord.HTTPException:
            return await ctx.send(f"<:warn:1297301606362251406> :  An error occurred while fetching the quoted message.")

    # If no statement or quoted message
    if not statement:
        embed = discord.Embed(
            title="Command name: tof",
            description='Check if a statement is true or false.',  # Nom de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="message", 
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
            value=f"```Syntax: {current_prefix}tof\n"
                  f"Example: {current_prefix}tof```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return
        
        return

    # Generate a random response
    result = random.choice([f"<:cross:1310264653330255934>", f"<:approve:1297301591698706483>"])

    # Create the embed with the statement and response
    embed = discord.Embed(
        title="Is this statement true?",
        description=f" \"{statement}\"",
        color=discord.Color(0x808080)
    )
    embed.add_field(name="", value=result, inline=False)

    await ctx.send(embed=embed)

#gifs commands 


#slaps

slap_gifs = [
        "https://i.pinimg.com/originals/d1/49/69/d14969a21a96ec46f61770c50fccf24f.gif",
        "https://i.imgur.com/oOCq3Bt.gif",
        "https://i.imgur.com/fm49srQ.gif",
        "https://i.imgur.com/CwbYjBX.gif",
        "https://i.imgur.com/kSLODXO.gif",
        "https://i.imgur.com/wlLCjRo.gif",
        "https://i.imgur.com/fpabdc9.gif"
]   

@bot.command(name="slap")
async def slap(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)
    
    if member is None:
        # Créer l'embed si aucun membre n'est mentionné
        embed = discord.Embed(
            title="Command name: slap",
            description='Slap everyone you find annoying in the server.',  # Nom de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members", 
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
            value=f"```Syntax: {current_prefix}slap <member>\n"
                  f"Example: {current_prefix}slap @User```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Vérifier si l'utilisateur essaie de se frapper soi-même
    if member == ctx.author:
        embed_warning = discord.Embed(
            description=f"<:warn:1297301606362251406> :  **You can't slap yourself!**",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_warning, reference=ctx.message)
        return

    # Choisir un gif aléatoire
    slap_gif = random.choice(slap_gifs)

    # Créer l'embed pour le slap
    embed = discord.Embed(
        description=f"**{ctx.author.mention} slaps {member.mention}!**",
        color=discord.Color(0x808080)
    )

    # Ajouter le gif dans l'embed
    embed.set_image(url=slap_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="Ouch, that must have hurt!", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

#hugs

hug_gifs = [
        "https://i.imgur.com/FxcGzhH.gif",
        "https://i.imgur.com/BKOxZb7.gif",
        "https://i.imgur.com/ZTjKona.gif",
        "https://i.imgur.com/FPznEhE.gif",
        "https://i.imgur.com/YoW9dvm.gif",
        "https://i.imgur.com/eIEKQpx.gif",
]

@bot.command(name="hug")
async def hug(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        embed = discord.Embed(
            title="Command name: hug",
            description='Spread love and calm in the server.',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members", 
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
            value=f"```Syntax: {current_prefix}hug <member>\n"
                  f"Example: {current_prefix}hug @User```",
                    inline=False
        )

                # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return        
    
    if member == ctx.author:
        embed_warning = discord.Embed(
            description=f"<:warn:1297301606362251406> : **You can't hug yourself !** No hoes or what lol ?",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_warning, reference=ctx.message)
        return

    # Choisir un gif aléatoire
    hug_gif = random.choice(hug_gifs)

    # Créer l'embed pour le hug
    embed = discord.Embed(
        description=f"**{ctx.author.mention} gives a warm hug to {member.mention} !**",
        color=discord.Color(0x808080)
    )
    
    # Ajouter le gif dans l'embed
    embed.set_image(url=hug_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="So much love !", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


#tired 

tired_gifs = [
        "https://media.tenor.com/lwyR-BEUeD4AAAAM/taiga-taiga-tired.gif",
        "https://i.gifer.com/8k36.gif",
        "https://i.pinimg.com/originals/9e/39/ba/9e39ba87306a84018a59a82cf3692067.gif",
        "https://image.myanimelist.net/ui/_3fYL8i6Q-n-155t3dn_4oa8joxN4d65hmFMp22bNTIUW3ufQExKZv-GKL4AdqgU",
        "https://i.pinimg.com/originals/fc/b5/ce/fcb5ce928c4dfb8dd416a97b260cbe9a.gif",
        "https://i.pinimg.com/originals/8f/f0/89/8ff08978b0b50aea949f046b18c1ff81.gif",
]

@bot.command(name="tired")
async def tired(ctx, member: discord.Member = None):
    """Envoie un GIF représentant quelqu'un de fatigué."""

    if member is None:
        # Si aucun membre n'est mentionné, la commande envoie un GIF aléatoire de "tired"
        tired_gif = random.choice(tired_gifs)

        # Créer l'embed pour le "tired"
        embed = discord.Embed(
            description=f"**{ctx.author.mention} is tired!**",
            color=discord.Color(0x808080)  # Couleur gris foncé
        )
        
        # Ajouter le GIF dans l'embed
        embed.set_image(url=tired_gif)

        # Ajouter la photo de profil en rond dans le footer
        embed.set_footer(text="Take some rest!", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)
        return

    # Si un membre est mentionné
    if member == ctx.author:
        return

    # Choisir un GIF aléatoire de "tired" pour l'utilisateur mentionné
    tired_gif = random.choice(tired_gifs)

    # Créer l'embed pour le "tired" de l'utilisateur mentionné
    embed = discord.Embed(
        description=f"**{member.mention} is tired!**",
        color=discord.Color(0x808080)
    )
    
    # Ajouter le GIF dans l'embed
    embed.set_image(url=tired_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="Take some rest!", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


#wink

wink_gifs = [
    "https://i.gifer.com/5c6u.gif",
    "https://i.pinimg.com/originals/82/76/e0/8276e0e1ea9f4f51b6471369f4630a9f.gif",
    "https://media2.giphy.com/media/JZHk5UwSixVIs/giphy.gif?cid=6c09b952m6a4kr1u9mfwg5ulezz6py37rwd22tgjm22u84sl&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=g",
    "https://i.pinimg.com/originals/0b/06/48/0b06480cdfed314322a8abfe3d5e8004.gif",
    "https://i.pinimg.com/originals/18/b2/53/18b25352e70e70f614f7c53adb857eba.gif", 
    "https://i.pinimg.com/originals/1a/3e/80/1a3e80b2d8b08e39d3a7355dc23a88db.gif"

    
]

@bot.command(name="wink")
async def wink(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)
    if member is None:
        embed = discord.Embed(
            title="Command name: Wink",
            description='Wink at someone in the server',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members", 
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
            value=f"```Syntax: {current_prefix}wink <member>\n"
                f"Example: {current_prefix}wink @User```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    if member == ctx.author:
        embed_warning = discord.Embed(
            description=f"<:warn:1297301606362251406> : **You can't wink at yourself.**",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_warning, reference=ctx.message)
        return

    # Choisir un gif aléatoire
    wink_gif = random.choice(wink_gifs)

    # Créer l'embed pour le kiss
    embed = discord.Embed(
        description=f"**{ctx.author.mention} wink at {member.mention} !**",
        color=discord.Color(0x808080)
    )
    
    # Ajouter le gif dans l'embed
    embed.set_image(url=wink_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="you have such a w rizz", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)



#stare 

stare_gifs = [
    "https://i.pinimg.com/originals/41/17/1e/41171ead66a26530351c0d745ca9ed61.gif",
    "https://i.pinimg.com/originals/ca/0c/9e/ca0c9e05cc6777086163461df02a5d9f.gif",
    "https://gifdb.com/images/high/psychotic-anime-girl-stare-yh93lvrj6ncsey0e.gif",
    "https://media1.tenor.com/m/0bIMD076bWwAAAAd/anime-nisekoi.gif", 
    "https://media0.giphy.com/media/fvcrSYkOmtP8c/giphy.gif?cid=6c09b952k9ytbryyevlgeqgtnjsx47kkpfnz9mgwla3cu9ul&ep=v1_gifs_search&rid=giphy.gif&ct=g"

    
]

@bot.command(name="stare")
async def stare(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)
    if member is None:
        embed = discord.Embed(
            title="Command name: Stare",
            description='Stare at someone in the server',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members", 
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
            value=f"```Syntax: {current_prefix}stare <member>\n"
                f"Example: {current_prefix}stare @User```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    if member == ctx.author:
        embed_warning = discord.Embed(
            description=f"<:warn:1297301606362251406> : **You can't stare at yourself or buy a mirror.**",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_warning, reference=ctx.message)
        return

    # Choisir un gif aléatoire
    stare_gif = random.choice(stare_gifs)

    # Créer l'embed pour le kiss
    embed = discord.Embed(
        description=f"**{ctx.author.mention} stares {member.mention} !**",
        color=discord.Color(0x808080)
    )
    
    # Ajouter le gif dans l'embed
    embed.set_image(url=stare_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="Kinda scary looking deep into my soul.", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


#kiss 

kiss_gifs = [
    "https://i.imgur.com/i3uwlmZ.gif",
    "https://i.imgur.com/ldinbWi.gif",
    "https://i.imgur.com/86mp4Nx.gif",
    "https://i.imgur.com/0i9XwG1.gif",
    "https://i.imgur.com/Xx8QgyX.gif", 
    "https://i.pinimg.com/originals/62/1c/ea/621ceac89636fc46ecaf81824f9fee0e.gif",
    "https://i.imgur.com/mhMvQX2.gif"
    
]

@bot.command(name="kiss")
async def kiss(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)
    if member is None:
        embed = discord.Embed(
            title="Command name: Kiss",
            description='Spread love and kisses in the server.',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members", 
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
            value=f"```Syntax: {current_prefix}kisses <member>\n"
                f"Example: {current_prefix}kisses @User```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    if member == ctx.author:
        embed_warning = discord.Embed(
            description=f"<:warn:1297301606362251406> : **You can't kiss yourself !** No hoes or what lol ?",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_warning, reference=ctx.message)
        return

    # Choisir un gif aléatoire
    kiss_gif = random.choice(kiss_gifs)

    # Créer l'embed pour le kiss
    embed = discord.Embed(
        description=f"**{ctx.author.mention} kisses {member.mention} !**",
        color=discord.Color(0x808080)
    )
    
    # Ajouter le gif dans l'embed
    embed.set_image(url=kiss_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="So much love !", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


#bully


bully_gifs = [
    "https://i.imgur.com/9mEO5k1.gif",
    "https://i.imgur.com/3SsZUVT.gif",
    "https://i.imgur.com/xmj8XRD.gif",
    "https://i.imgur.com/g005tMV.gif",
    "https://i.imgur.com/meZ0TDz.gif", 
    "https://i.imgur.com/wzn0ghV.gif",
    "https://i.imgur.com/aBQJPvZ.gif"
    
]

@bot.command(name="bully")
async def bully(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        embed = discord.Embed(
            title="Command name: bully",
            description='Spread violence and bully someone in the server.',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members", 
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
            value=f"```Syntax: {current_prefix}bully <member>\n"
                f"Example: {current_prefix}bully @User```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return


    if member == ctx.author:
        embed_warning = discord.Embed(
            description=f"<:warn:1297301606362251406> : **You can't bully yourself !** Btw i wont judge your kink.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_warning,reference=ctx.message)
        return

    # Choisir un gif aléatoire
    bully_gif = random.choice(bully_gifs)

    # Créer l'embed pour le bully
    embed = discord.Embed(
        description=f"**{ctx.author.mention} bullies {member.mention} !**",
        color=discord.Color(0x808080)
    )

    # Ajouter le gif dans l'embed
    embed.set_image(url=bully_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="Hope that hurts !", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


bite_gifs = [
        "https://i.imgur.com/SpWh4iA.gif",
        "https://i.imgur.com/WK7TvIZ.gif",
        "https://i.imgur.com/QuO07Pd.gif",
        "https://i.imgur.com/seFp2WN.gif",
        "https://i.imgur.com/fyNa7PE.gif", 
        "https://24.media.tumblr.com/0997d9e6865c7a8fd53f65a8e3018017/tumblr_msizvuMMBa1s7s6pro1_500.gif",
        "https://i.pinimg.com/originals/43/3b/b3/433bb37bdb9db97055d51c589cb4cfc8.gif",
        
]

@bot.command(name="bite", aliases=['bites'])
async def bite(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        embed = discord.Embed(
            title="Command name: bite",
            description='Bite someone.',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members", 
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
            value=f"```Syntax: {current_prefix}bite <member>\n"
                f"Example: {current_prefix}bite @User```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return


    if member == ctx.author:
        embed_warning = discord.Embed(
            description=f"<:warn:1297301606362251406> : **You can't bite yourself !** Btw i wont judge your kink.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_warning, reference=ctx.message)
        return

    # Choisir un gif aléatoire
    bite_gif = random.choice(bite_gifs)

    # Créer l'embed pour le bite
    embed = discord.Embed(
        description=f"**{ctx.author.mention} bites {member.mention} !**",
        color=discord.Color(0x808080)
    )
    
    # Ajouter le gif dans l'embed
    embed.set_image(url=bite_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="Hope that hurts !", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


punch_gifs = [
            "https://i.pinimg.com/originals/a5/2e/ba/a52eba768035cb7ae66f15f3c66bb184.gif",
            "https://i.pinimg.com/originals/66/76/7a/66767af902113b20978f5880593b29af.gif",
            "https://i.imgur.com/jWZPAU2.gif",
            "https://i.imgur.com/GsMjksq.gif",
            "https://i.imgur.com/7jErgl1.gif"
]

@bot.command(name="punch")
async def punch(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        embed = discord.Embed(
            title="Command name: punch",
            description='Hit someone.',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="members", 
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
            value=f"```Syntax: {current_prefix}punch <member>\n"
                f"Example: {current_prefix}punch @User```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    
    if member == ctx.author:
        embed_warning = discord.Embed(
            description=f"<:warn:1297301606362251406> :  **Are you okay ?**",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return

    # Choisir un gif aléatoire
    punch_gif = random.choice(punch_gifs)

    # Créer l'embed pour le punch
    embed = discord.Embed(
        description=f"**{ctx.author.mention} punchs {member.mention} !**",
        color=discord.Color(0x808080)
    )
    
    # Ajouter le gif dans l'embed
    embed.set_image(url=punch_gif)

    # Ajouter la photo de profil en rond dans le footer
    embed.set_footer(text="Ouch, that must have hurt!", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)



#-----------------------------------------------------------------------------



@bot.command(name="pp", help="Generates a random size in inches, comments on it, and draws a doodle.")
async def pp(ctx):
    # Generate a random size between 1 and 15 inches
    size = random.randint(1, 15)

    # Comments based on the size
    if size < 5:
        comment = "That's a bit small, isn't it?"
    elif 5 <= size < 8:
        comment = "A medium size, that's acceptable!"
    elif 8 <= size < 12:
        comment = "Now we're talking, that's interesting!"
    else:
        comment = "Wow, that's huge!"

    # Create the doodle representation
    doodle = '8' + '=' * size + 'D'  # The size determines the number of '='

    # Create an embed
    embed = discord.Embed(
        description=f"Size: **{size} inches**\n{comment}\n\n```\n{doodle}\n```",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)  # Send the embed in the chat


# Classe représentant un bouton dans le jeu de Tic-Tac-Toe
class TTTButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if interaction.user != view.current_player:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> :  It's not your turn!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if self.label != "\u200b":  # Si la case est déjà occupée
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : This spot is already taken.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Définir la marque du joueur (X ou O)
        self.label = "X" if view.current_player == view.x_player else "O"
        self.style = discord.ButtonStyle.success if self.label == "X" else discord.ButtonStyle.danger

        # Mettre à jour le tableau de jeu
        view.board[self.x][self.y] = self.label
        winner = view.check_winner()

        # Vérifier s'il y a un gagnant
        if winner:
            for button in view.children:
                button.disabled = True
            winner_name = view.x_player if winner == "X" else view.o_player
            await interaction.response.edit_message(content=f"{winner_name.mention} wins!", view=view)
            view.stop()
        elif view.is_board_full():  # Vérifier s'il y a un match nul
            for button in view.children:
                button.disabled = True
            await interaction.response.edit_message(content="It's a draw!", view=view)
            view.stop()
        else:  # Passer au tour du joueur suivant
            view.current_player = view.o_player if view.current_player == view.x_player else view.x_player
            await interaction.response.edit_message(content=f"It's {view.current_player.mention}'s turn", view=view)

# Vue représentant le plateau de Tic-Tac-Toe
class TTTView(discord.ui.View):
    def __init__(self, x_player, o_player):
        super().__init__()
        self.x_player = x_player
        self.o_player = o_player
        self.current_player = x_player
        self.board = [["" for _ in range(3)] for _ in range(3)]

        # Ajouter les boutons (3x3) au plateau
        for x in range(3):
            for y in range(3):
                self.add_item(TTTButton(x, y))

    # Vérifier s'il y a un gagnant
    def check_winner(self):
        # Vérifier les lignes
        for row in self.board:
            if row[0] == row[1] == row[2] and row[0] != "":
                return row[0]
        # Vérifier les colonnes
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] != "":
                return self.board[0][col]
        # Vérifier les diagonales
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] != "":
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] != "":
            return self.board[0][2]
        return None

    # Vérifier si toutes les cases sont occupées
    def is_board_full(self):
        return all(self.board[x][y] != "" for x in range(3) for y in range(3))

# Commande pour démarrer un jeu de Tic-Tac-Toe
@bot.command(name="ttt", aliases=['tictactoe', 'tic-tac-toe'])
async def ttt(ctx, member: discord.Member = None):
    current_prefix = load_prefix(ctx.guild.id)

    if member is None:
        embed = discord.Embed(
            title="Command name: tic-tac-toe ",  # Nom de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases",
            value="tictactoe, tic-tac-toe",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters",
            value="N/A",
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
            value=f"```Syntax: {current_prefix}ttt <member>\n"
                  f"Example: {current_prefix}ttt @User```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    if member == ctx.author:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You can't play with yourself!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return

    # Créer une vue Tic-Tac-Toe avec les deux joueurs
    view = TTTView(ctx.author, member)
    await ctx.send(f"{ctx.author.mention} vs {member.mention} - {ctx.author.mention}'s turn!", view=view)

@bot.command(name='flipcoin')
async def flip_coin(ctx):
    result = random.choice(['Heads', 'Tails'])
    
    # Créer l'embed
    embed = discord.Embed(description=f"🪙 : The coin landed on **{result}**", color=discord.Color(0x808080))
    
    await ctx.send(embed=embed)


def uwufi_text(text: str) -> str:
    # Fonction qui transforme le texte en mode kawaii
    text = re.sub(r'[rl]', 'w', text)  # Remplacer 'r' et 'l' par 'w'
    text = re.sub(r'R', 'W', text)  # Remplacer 'R' par 'W'
    text = re.sub(r'L', 'W', text)  # Remplacer 'L' par 'W'
    
    kawaii_endings = [' owo', ' uwu', ' >w<', ' ^w^']
    text += kawaii_endings[len(text) % len(kawaii_endings)]  # Ajouter une fin kawaii

    return text

@bot.command(name="uwufi")
async def uwufi(ctx, *, message_text: str = None):
    current_prefix = load_prefix(ctx.guild.id)

    # Si aucun texte n'est fourni et qu'un message est cité
    if not message_text and ctx.message.reference:
        # Récupérer le message cité
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if referenced_message:
            message_text = referenced_message.content

    if not message_text:
        # Créer l'embed si aucun texte n'est fourni
        embed = discord.Embed(
            title="Command name : uwufi",  # Nom de la commande
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases",
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed.add_field(
            name="Parameters",
            value="N/A",
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
            value=f"```Syntax: {current_prefix}uwufi <message>\n"
                  f"Example: {current_prefix}uwufi Hello !```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: fun.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Transformer le texte en mode kawaii
    uwu_text = uwufi_text(message_text)

    # Envoi du texte transformé
    await ctx.send(uwu_text)

# Gestion des erreurs
@uwufi.error
async def uwufi_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await send_permission_error(ctx)


@bot.command(name="say")
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message_text: str):
    # Supprimer le message d'origine après 1 seconde
    await ctx.message.delete()

    # Envoyer le message en utilisant le bot
    await ctx.send(message_text)



# Définir les paramètres du jeu
letters_list = [
    'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak',
    'al', 'am', 'an', 'ao', 'ap', 'ar', 'as', 'at', 'au', 'av',
    'aw', 'ax', 'ay', 'az', 'ba', 'be', 'bi', 'bo', 'br', 'ca',
    'ce', 'ch', 'ci', 'cl', 'co', 'cr', 'cu', 'da', 'de', 'di',
    'do', 'du', 'ed', 'ef', 'el', 'en', 'es', 'et', 'fa', 'fe',
    'fo', 'fr', 'ga', 'go', 'gr', 'ha', 'he', 'hi', 'ho', 'hu',
    'ic', 'id', 'if', 'il', 'im', 'in', 'is', 'it', 'ja', 'je',
    'jo', 'ka', 'la', 'le', 'li', 'lo', 'ma', 'me', 'mi', 'mo',
    'mu', 'na', 'ne', 'no', 'of', 'on', 'or', 'os', 'pa', 'pe',
    'pi', 're', 'sa', 'se', 'si', 'so', 'ta', 'to', 'us', 'va',
    'we', 'wi', 'ye', 'za'
]
max_players = 5
min_players = 2
initial_lives = 3
response_time = 10  # temps limite pour chaque réponse

# Fonction pour vérifier si un mot commence par les lettres données
def starts_with(word, letters):
    return word.lower().startswith(letters.lower())

@bot.command(name="blacktea")
async def blacktea(ctx):
    embed = discord.Embed(
        title="BlackTea Matchmaking",
        description="**Guide**\nReact with 🍵 to join the round\nYou have 20 seconds to join.\nThe game starts only if there are at least 2 joined players.\nEveryone has 3 lives.\nThink about a word that starts with the specific letters given.",
        color=0x008080
    )
    message = await ctx.send(embed=embed)
    await message.add_reaction("🍵")

    # Liste des joueurs qui ont rejoint
    players = []

    # Vérifier les réactions pour voir qui rejoint
    def check_reaction(reaction, user):
        return reaction.message.id == message.id and str(reaction.emoji) == "🍵" and user != bot.user

    # Attendre 20 secondes pour que les joueurs rejoignent
    try:
        while len(players) < max_players:
            reaction, user = await bot.wait_for("reaction_add", timeout=20.0, check=check_reaction)
            if user not in players:
                players.append(user)
                await ctx.send(f"{user.name} has joined the game!")
    except asyncio.TimeoutError:
        pass

    # Vérifier si le nombre minimum de joueurs est atteint
    if len(players) < min_players:
        await ctx.send("Not enough players to start the game.")
        return

    # Initialiser les vies des joueurs
    player_lives = {player: initial_lives for player in players}
    embed_game_start = discord.Embed(
        title="The game is starting!",
        description="Get ready! Everyone has 3 lives.",
        color=0x008080
    )
    await ctx.send(embed=embed_game_start)

    # Le jeu continue tant qu'il reste des joueurs
    while len(player_lives) > 1:
        # Choisir une lettre aléatoire
        chosen_letters = random.choice(letters_list)
        embed_letters = discord.Embed(
            title="New Round!",
            description=f"Think of a word starting with **{chosen_letters.upper()}**. You have {response_time} seconds!",
            color=0x008080
        )
        await ctx.send(embed=embed_letters)

        for player in list(player_lives.keys()):
            def check_message(m):
                return m.author == player and m.channel == ctx.channel

            try:
                # Attendre que le joueur réponde
                msg = await bot.wait_for("message", check=check_message, timeout=response_time)

                if starts_with(msg.content, chosen_letters):
                    await ctx.send(f"**{player.name}** found a valid word: **{msg.content}**.")
                else:
                    player_lives[player] -= 1
                    await ctx.send(embed=discord.Embed(
                        title="Wrong answer!",
                        description=f"{player.name} loses 1 life. ({player_lives[player]} lives left)",
                        color=0xff0000
                    ))

            except asyncio.TimeoutError:
                # Si le joueur ne répond pas dans le temps imparti
                player_lives[player] -= 1
                await ctx.send(embed=discord.Embed(
                    title="Time over!",
                    description=f"{player.name} didn't answer in time and loses 1 life. ({player_lives[player]} lives left)",
                    color=0xff0000
                ))

            # Si un joueur perd toutes ses vies
            if player_lives[player] <= 0:
                await ctx.send(embed=discord.Embed(
                    title="Eliminated!",
                    description=f"{player.name} has been eliminated!",
                    color=0xff0000
                ))
                del player_lives[player]

        # Vérifier si un seul joueur reste
        if len(player_lives) == 1:
            winner = list(player_lives.keys())[0]
            await ctx.send(embed=discord.Embed(
                title="We have a winner!",
                description=f"**{winner.name}** wins the BlackTea game!",
                color=0x00ff00
            ))
            break
