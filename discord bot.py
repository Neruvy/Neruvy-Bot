import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("INSERT TOKEN HERE")

# Set up bot with new prefix and all intents
bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command()
async def EzMod(ctx):
    await ctx.send(f"{ctx.author.mention}, EzMod was discontinued because it was just a reskinned bot thats been used by hundreds of people. But EzBot is a new, made from scratch bot made by @.ez1oo .")

@bot.command()
async def goodmorning(ctx):
    await ctx.send(f"Good morning, {ctx.author.mention}!")

@bot.command()
async def sendembed(ctx):
    embeded_msg = discord.Embed(
        title="Title of embed",
        description="Description of embed",
        color=discord.Color.blue()
    )
    embeded_msg.set_thumbnail(url=ctx.author.display_avatar.url)
    embeded_msg.add_field(name="Name of field", value="Value of field", inline=False)
    if ctx.guild.icon:
        embeded_msg.set_image(url=ctx.guild.icon.url)
    embeded_msg.set_footer(text="Footer text", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embeded_msg)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="Ping",
        description="Latency in ms",
        color=discord.Color.blue()
    )
    embed.add_field(name=f"{bot.user.name}'s Latency:", value=f"{latency}ms", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}.", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ You can't ban this member due to role hierarchy.")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} has been banned. Reason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this user.")
    except discord.HTTPException:
        await ctx.send("❌ Something went wrong while trying to ban the user.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please specify a member to ban. Usage: `$ban @user [reason]`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Couldn't find that member. Please mention a valid user.")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f'✅ {member.mention} has been kicked. Reason: {reason or "No reason provided."}')
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick this user.")
    except discord.HTTPException:
        await ctx.send("❌ Something went wrong while trying to kick the user.")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please specify a member to kick. Usage: `!kick @user [reason]`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Couldn't find that member. Please mention a valid user.")

@bot.command(name='say')
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

@say.error
async def say_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the 'Manage Messages' permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please include a message to say. Usage: `!say Hello!`")

@bot.command(name='addrole')
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role: discord.Role):
    if role in member.roles:
        await ctx.send(f"ℹ️ {member.mention} already has the role `{role.name}`.")
        return
    if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ You can't assign a role equal to or higher than your own.")
        return
    if role >= ctx.guild.me.top_role:
        await ctx.send("❌ I can't assign that role because it's above my highest role.")
        return
    try:
        await member.add_roles(role)
        await ctx.send(f"✅ Successfully gave `{role.name}` to {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to assign that role.")
    except discord.HTTPException:
        await ctx.send("❌ Failed to assign the role due to an API error.")

@addrole.error
async def addrole_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the `Manage Roles` permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!addrole @user @role`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Couldn't find the user or role. Please mention both correctly.")

@bot.command(name='removerole')
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role: discord.Role):
    if role not in member.roles:
        await ctx.send(f"ℹ️ {member.mention} does not have the role `{role.name}`.")
        return
    if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ You can't remove a role equal to or higher than your own.")
        return
    if role >= ctx.guild.me.top_role:
        await ctx.send("❌ I can't remove that role because it's above my highest role.")
        return
    try:
        await member.remove_roles(role)
        await ctx.send(f"✅ Successfully removed `{role.name}` from {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to remove that role.")
    except discord.HTTPException:
        await ctx.send("❌ Failed to remove the role due to an API error.")

@removerole.error
async def removerole_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the `Manage Roles` permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!removerole @user @role`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Couldn't find the user or role. Please mention both correctly.")

@bot.command(name='setstatus')
@commands.has_permissions(administrator=True)
async def setstatus(ctx, activity_type: str, *, message: str):
    activity_type = activity_type.lower()

    if activity_type == "playing":
        activity = discord.Game(name=message)
    elif activity_type == "streaming":
        activity = discord.Streaming(name=message, url="https://twitch.tv/yourchannel")  # Replace with actual URL
    elif activity_type == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=message)
    elif activity_type == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=message)
    else:
        await ctx.send("❌ Invalid activity type. Use one of: `playing`, `streaming`, `listening`, `watching`.")
        return

    await bot.change_presence(activity=activity)
    await ctx.send(f"✅ Status updated to **{activity_type}**: {message}")

@setstatus.error
async def setstatus_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!setstatus <playing|streaming|listening|watching> <message>`")

# Start the bot
bot.run("INSERT TOKEN HERE")