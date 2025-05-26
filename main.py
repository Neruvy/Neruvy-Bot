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

@bot.command(name='changenick')
@commands.has_permissions(manage_nicknames=True)
async def change_nickname(ctx, member: discord.Member, *, new_nickname: str):
    try:
        await member.edit(nick=new_nickname)
        await ctx.send(f"✅ Changed nickname for {member.mention} to `{new_nickname}`.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to change that user's nickname.")
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred: {e}")

@bot.command(name='userinfo')
async def user_info(ctx, member: discord.Member = None):
    member = member or ctx.author  # Default to the invoker

    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    role_list = ", ".join(roles) if roles else "No roles"

    embed = discord.Embed(title=f"User Info: {member}", color=0x00ffcc)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="🆔 User ID", value=member.id, inline=False)
    embed.add_field(name="👤 Username", value=str(member), inline=True)
    embed.add_field(name="🏷️ Nickname", value=member.nick or "None", inline=True)
    embed.add_field(name="🤖 Bot Account", value="Yes" if member.bot else "No", inline=True)
    embed.add_field(name="📆 Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="📅 Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "N/A", inline=False)
    embed.add_field(name="📜 Roles", value=role_list, inline=False)

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

    await ctx.send(embed=embed)

@bot.command(name='channelinfo')
async def channel_info(ctx, channel: discord.abc.GuildChannel = None):
    channel = channel or ctx.channel  # Defaults to the channel the command was used in

    embed = discord.Embed(title=f"Channel Info: #{channel.name}", color=0x3498db)
    embed.add_field(name="🆔 Channel ID", value=channel.id, inline=False)
    embed.add_field(name="📂 Category", value=channel.category.name if channel.category else "None", inline=False)
    embed.add_field(name="🗂 Type", value=channel.type.name.capitalize(), inline=True)
    embed.add_field(name="🔞 NSFW", value="Yes" if getattr(channel, 'is_nsfw', lambda: False)() else "No", inline=True)
    embed.add_field(name="📅 Created On", value=channel.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

    if isinstance(channel, discord.TextChannel):
        embed.add_field(name="✏️ Topic", value=channel.topic or "None", inline=False)
        embed.add_field(name="👁 Slowmode", value=f"{channel.slowmode_delay} seconds", inline=True)

    if isinstance(channel, discord.VoiceChannel):
        embed.add_field(name="👥 User Limit", value=channel.user_limit or "Unlimited", inline=True)
        embed.add_field(name="🔊 Bitrate", value=f"{channel.bitrate} bps", inline=True)

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='clearbot')
@commands.has_permissions(manage_messages=True)
async def clear_bot_messages(ctx, limit: int = 100):
    """
    Deletes up to `limit` messages from bots in the current channel.
    Usage: !clearbot [limit]
    """
    await ctx.message.delete()  # Deletes the command invocation message

    def is_bot(m):
        return m.author.bot

    deleted = await ctx.channel.purge(limit=limit, check=is_bot)
    confirmation = await ctx.send(f"🧹 Deleted {len(deleted)} bot message(s).")
    await confirmation.delete(delay=5)  # Auto-delete confirmation message after 5 seconds

@bot.command(name='poll')
async def poll(ctx, question: str, *options):
    """
    Create a simple poll with 2–10 options.
    Usage: !poll "What's your favorite color?" Red Blue Green
    """
    if len(options) < 2:
        await ctx.send("❌ You need at least 2 options to create a poll.")
        return
    if len(options) > 10:
        await ctx.send("❌ You can only have up to 10 options.")
        return

    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    description = ""
    for i, option in enumerate(options):
        description += f"{emojis[i]} {option}\n"

    embed = discord.Embed(title="📊 Poll", description=f"**{question}**\n\n{description}", color=0x7289DA)
    embed.set_footer(text=f"Poll by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

    poll_message = await ctx.send(embed=embed)

    for i in range(len(options)):
        await poll_message.add_reaction(emojis[i])

# Start the bot
bot.run("INSERT TOKEN HERE")
