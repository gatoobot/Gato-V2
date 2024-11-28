from mango import *

import discord
from discord.ext import commands

prefix_collection = db['prefix']

# Préfixe par défaut
DEFAULT_PREFIX = '$'

# Cache pour les préfixes des guildes
prefix_cache = {}

# Fonction pour obtenir le préfixe spécifique au serveur depuis MongoDB ou le cache
def load_prefix(guild_id):
    # Si le préfixe est déjà en cache, on le retourne directement
    if str(guild_id) in prefix_cache:
        return prefix_cache[str(guild_id)]
    
    # Sinon, on charge le préfixe depuis MongoDB
    try:
        doc = prefix_collection.find_one({"guild_id": str(guild_id)})
        if doc:
            prefix_cache[str(guild_id)] = doc.get('prefix', DEFAULT_PREFIX)
            return prefix_cache[str(guild_id)]
        else:
            prefix_cache[str(guild_id)] = DEFAULT_PREFIX
            return DEFAULT_PREFIX
    except Exception as e:
        print(f"Erreur lors de la récupération du préfixe pour la guilde {guild_id}: {e}")
        return DEFAULT_PREFIX

# Fonction pour sauvegarder le nouveau préfixe dans MongoDB et le cache
def save_prefix(guild_id, new_prefix):
    try:
        # Mettre à jour MongoDB
        prefix_collection.update_one(
            {"guild_id": str(guild_id)}, 
            {"$set": {"prefix": new_prefix}}, 
            upsert=True  
        )

        # Mettre à jour le cache
        prefix_cache[str(guild_id)] = new_prefix
        print(f"Le préfixe de la guilde {guild_id} a été mis à jour à `{new_prefix}`.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du préfixe pour la guilde {guild_id}: {e}")

# Fonction pour obtenir le préfixe dynamique
def get_prefix(bot, message):
    guild_id = message.guild.id if message.guild else None
    return load_prefix(guild_id)

# Commande pour changer le préfixe
async def set_prefix_command(ctx, new_prefix: str = None):
    current_prefix = load_prefix(ctx.guild.id)

    if new_prefix is None:
        embed = discord.Embed(
            title="Command name: setprefix",
            description="Change the bot prefix.",
            color=discord.Color(0x808080)
        )
        embed.set_author(name=f"{ctx.bot.user.name}", icon_url=ctx.bot.user.avatar.url)
        embed.add_field(name="Aliases", value="N/A", inline=False)
        embed.add_field(name="Parameters", value="prefix", inline=False)
        embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Administrator**", inline=False)
        embed.add_field(name="Usage", value=f"```Syntax: {current_prefix}setprefix <new_prefix>\nExample: {current_prefix}setprefix !```", inline=False)
        embed.set_footer(text=f"Page 1/1 • Module: moderation.py • {ctx.message.created_at.strftime('%H:%M')}")
        await ctx.send(embed=embed)
        return

    if len(new_prefix) > 3:
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : The prefix should be at most 3 characters.",
            color=discord.Color.red()
        ))
        return

    if new_prefix == current_prefix:
        await ctx.send(embed=discord.Embed(
            description=f"<:warn:1297301606362251406> : The prefix is already `{new_prefix}`.",
            color=discord.Color.yellow()
        ))
        return

    save_prefix(ctx.guild.id, new_prefix)

    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : The prefix has been changed to `{new_prefix}`.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# Enregistrer la commande setprefix dans le bot
def register_prefix_commands(bot):
    @bot.command(name='setprefix')
    @commands.has_permissions(administrator=True)
    async def set_prefix_command_wrapper(ctx, new_prefix: str = None):
        await set_prefix_command(ctx, new_prefix)
