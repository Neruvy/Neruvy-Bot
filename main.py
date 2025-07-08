import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime
import threading
import time
import asyncio
import sys
import select
if os.name == 'nt':
    import msvcrt
from discord.ext.commands import CommandNotFound
import shutil
import json

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("MTM3MDc3MDIwOTIwNzc1MDcxOQ.GjBArS.JAWHxAi8h628uV8OYoKvQ2f6jobh9u0TM4R0SM")

# Set up bot with new prefix and all intents
bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

# ANSI color codes
BLUE = '\033[94m'
BOLD_BLUE = '\033[1;94m'
RESET = '\033[0m'

# Global list to store command logs
command_logs = []

# Welcome/Leave message storage
WELCOME_LEAVE_FILE = "welcome_leave_messages.json"
welcome_messages = {}
leave_messages = {}
welcome_channels = {}
leave_channels = {}

def load_welcome_leave_messages():
    """Load welcome and leave messages from JSON file"""
    global welcome_messages, leave_messages, welcome_channels, leave_channels
    try:
        if os.path.exists(WELCOME_LEAVE_FILE):
            with open(WELCOME_LEAVE_FILE, 'r') as f:
                data = json.load(f)
                welcome_messages = data.get('welcome', {})
                leave_messages = data.get('leave', {})
                welcome_channels = data.get('welcome_channels', {})
                leave_channels = data.get('leave_channels', {})
    except Exception as e:
        print(f"Error loading welcome/leave messages: {e}")
        welcome_messages = {}
        leave_messages = {}
        welcome_channels = {}
        leave_channels = {}

def save_welcome_leave_messages():
    """Save welcome and leave messages to JSON file"""
    try:
        data = {
            'welcome': welcome_messages,
            'leave': leave_messages,
            'welcome_channels': welcome_channels,
            'leave_channels': leave_channels
        }
        with open(WELCOME_LEAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving welcome/leave messages: {e}")

def format_message(message, member, guild):
    """Format message with placeholders"""
    if not message:
        return None
    
    # Available placeholders
    replacements = {
        '{user}': member.mention,
        '{user.name}': member.name,
        '{user.display_name}': member.display_name,
        '{user.id}': str(member.id),
        '{server}': guild.name,
        '{server.member_count}': str(guild.member_count),
        '{server.name}': guild.name,
        '{user.created_at}': member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        '{user.joined_at}': member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unknown"
    }
    
    formatted_message = message
    for placeholder, value in replacements.items():
        formatted_message = formatted_message.replace(placeholder, value)
    
    return formatted_message

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def rgb_gradient(start_rgb, end_rgb, steps):
    """Generate a list of RGB tuples forming a gradient from start_rgb to end_rgb."""
    if steps <= 1:
        return [start_rgb]
    gradient = []
    for i in range(steps):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (steps - 1))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (steps - 1))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (steps - 1))
        gradient.append((r, g, b))
    return gradient

def print_gradient(text, start_rgb=(0, 102, 255), end_rgb=(128, 0, 128), vertical=False):
    """Print text with a blue-to-purple gradient. If vertical=True and text is multiline, apply top-to-bottom gradient."""
    if not text:
        print()
        return
    if vertical and '\n' in text:
        lines = text.splitlines()
        gradient = rgb_gradient(start_rgb, end_rgb, len(lines))
        for line, (r, g, b) in zip(lines, gradient):
            print(f"\033[38;2;{r};{g};{b}m{line}\033[0m")
    else:
        gradient = rgb_gradient(start_rgb, end_rgb, len(text))
        for char, (r, g, b) in zip(text, gradient):
            print(f"\033[38;2;{r};{g};{b}m{char}\033[0m", end="")
        print()

def print_boxed_centered(lines, title=None):
    """Print a list of lines centered in a Unicode box, with an optional title, using a vertical gradient."""
    width = shutil.get_terminal_size((80, 20)).columns
    content_lines = [line.strip() for line in lines]
    if title:
        content_lines = [title] + content_lines
    max_len = max(len(line) for line in content_lines)
    box_width = max(max_len + 6, 30)  # Minimum width 30
    left_pad = (width - box_width) // 2
    # Prepare all lines to print (top, title, separator, content, bottom)
    box_lines = []
    # Top border
    box_lines.append(" " * left_pad + "┌" + "─" * (box_width - 2) + "┐")
    # Title (if present)
    if title:
        box_lines.append(" " * left_pad + "│" + title.center(box_width - 2) + "│")
        box_lines.append(" " * left_pad + "├" + "─" * (box_width - 2) + "┤")
        content_lines = content_lines[1:]
    # Content
    for line in content_lines:
        box_lines.append(" " * left_pad + "│" + line.center(box_width - 2) + "│")
    # Bottom border
    box_lines.append(" " * left_pad + "└" + "─" * (box_width - 2) + "┘")
    # Vertical gradient: blue (top) to purple (bottom)
    start_rgb = (0, 102, 255)
    end_rgb = (128, 0, 128)
    n = len(box_lines)
    gradient = rgb_gradient(start_rgb, end_rgb, n)
    for line, (r, g, b) in zip(box_lines, gradient):
        print(f"\033[38;2;{r};{g};{b}m{line}\033[0m")

def show_ascii_art():
    """Display the ASCII art for Neruvy Bot with vertical gradient and centered"""
    ascii_art = """
    ███╗   ██╗███████╗██████╗ ██╗   ██╗██╗   ██╗██╗   ██╗
    ████╗  ██║██╔════╝██╔══██╗██║   ██║╚██╗ ██╔╝╚██╗ ██╔╝
    ██╔██╗ ██║█████╗  ██████╔╝██║   ██║ ╚████╔╝  ╚████╔╝ 
    ██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║  ╚██╔╝    ╚██╔╝  
    ██║ ╚████║███████╗██║  ██║╚██████╔╝   ██║      ██║   
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝      ╚═╝   
                                                            
    ██████╗  ██████╗ ████████╗                           
    ██╔══██╗██╔═══██╗╚══██╔══╝                           
    ██████╔╝██║   ██║   ██║                              
    ██╔══██╗██║   ██║   ██║                              
    ██████╔╝╚██████╔╝   ██║                              
    ╚═════╝  ╚═════╝    ╚═╝                              
    """
    width = shutil.get_terminal_size((80, 20)).columns
    centered_art = '\n'.join(line.center(width) for line in ascii_art.splitlines())
    print_gradient(centered_art, vertical=True)

def show_main_menu():
    """Display the main menu as a grid that auto-adjusts to terminal size. If too small, prompt user to resize."""
    clear_screen()
    show_ascii_art()
    options = [
        "1. View All Commands",
        "2. View Admin Commands",
        "3. View Info Commands",
        "4. View Fun Commands",
        "5. View Command Usage Examples",
        "6. Bot Status",
        "7. Change Bot Status",
        "8. View Command Logs",
        "0. Exit Menu"
    ]
    width = shutil.get_terminal_size((80, 20)).columns
    box_width = max(len(opt) for opt in options) + 4
    min_grid_width = box_width
    # Find max options per row that fit
    max_per_row = len(options)
    for n in range(len(options), 0, -1):
        total_width = (box_width + 1) * n - 1
        if total_width <= width:
            max_per_row = n
            break
    if (box_width + 1) * 1 - 1 > width:
        # Too small for even one box
        msg = "Terminal window too small! Please resize the window to view the menu."
        print_gradient("\n" + msg.center(width) + "\n", vertical=True)
        return
    # Prepare grid rows
    rows = [options[i:i+max_per_row] for i in range(0, len(options), max_per_row)]
    grid_lines = []
    for row in rows:
        total_grid_width = (box_width + 1) * len(row) - 1
        left_pad = (width - total_grid_width) // 2
        # Top line of boxes
        line = " " * left_pad + "+".join(["-" * box_width for _ in row])
        grid_lines.append(line)
        # Option line
        opt_line = " " * left_pad + "|".join([opt.center(box_width) for opt in row])
        grid_lines.append(opt_line)
    # Bottom border
    line = " " * left_pad + "+".join(["-" * box_width for _ in rows[-1]])
    grid_lines.append(line)
    print_gradient("\n".join(grid_lines), vertical=True)

def show_all_commands():
    """Display all commands with gradient text, centered and boxed"""
    clear_screen()
    show_ascii_art()
    commands_list = sorted(bot.commands, key=lambda x: x.name)
    lines = [f"{i:2d}. ${cmd.name:<15} - {cmd.help if cmd.help else 'No description available'}" for i, cmd in enumerate(commands_list, 1)]
    lines.append("")
    lines.append("0. Back to Main Menu")
    print_boxed_centered(lines, title="ALL COMMANDS")

def show_admin_commands():
    """Display admin commands with gradient text, centered and boxed"""
    clear_screen()
    show_ascii_art()
    admin_commands = ['ban', 'kick', 'addrole', 'removerole', 'setstatus', 'say', 'clearbot', 'setwelcome', 'setleave', 'clearwelcome', 'clearleave', 'testwelcome', 'testleave', 'setwelcomechannel', 'setleavechannel', 'clearwelcomechannel', 'clearleavechannel']
    commands_list = [cmd for cmd in bot.commands if cmd.name in admin_commands]
    lines = [f"{i:2d}. ${cmd.name:<15} - {cmd.help if cmd.help else 'No description available'}" for i, cmd in enumerate(commands_list, 1)]
    lines.append("")
    lines.append("0. Back to Main Menu")
    print_boxed_centered(lines, title="ADMIN COMMANDS")

def show_info_commands():
    """Display info commands with gradient text, centered and boxed"""
    clear_screen()
    show_ascii_art()
    info_commands = ['userinfo', 'channelinfo', 'serverinfo', 'ping', 'welcomeinfo']
    commands_list = [cmd for cmd in bot.commands if cmd.name in info_commands]
    lines = [f"{i:2d}. ${cmd.name:<15} - {cmd.help if cmd.help else 'No description available'}" for i, cmd in enumerate(commands_list, 1)]
    lines.append("")
    lines.append("0. Back to Main Menu")
    print_boxed_centered(lines, title="INFO COMMANDS")

def show_fun_commands():
    """Display fun commands with gradient text, centered and boxed"""
    clear_screen()
    show_ascii_art()
    fun_commands = ['goodmorning', 'sendembed', 'poll', 'changenick']
    commands_list = [cmd for cmd in bot.commands if cmd.name in fun_commands]
    lines = [f"{i:2d}. ${cmd.name:<15} - {cmd.help if cmd.help else 'No description available'}" for i, cmd in enumerate(commands_list, 1)]
    lines.append("")
    lines.append("0. Back to Main Menu")
    print_boxed_centered(lines, title="FUN COMMANDS")

def show_usage_examples():
    """Display command usage examples with gradient text, centered and boxed"""
    clear_screen()
    show_ascii_art()
    examples = [
        ("$ping", "Check bot latency"),
        ("$userinfo @user", "Get info about a user"),
        ("$ban @user reason", "Ban a user with reason"),
        ("$kick @user", "Kick a user"),
        ("$addrole @user @role", "Add role to user"),
        ("$removerole @user @role", "Remove role from user"),
        ("$say Hello World", "Make bot say something"),
        ("$poll 'Question?' Option1 Option2", "Create a poll"),
        ("$setstatus playing Minecraft", "Set bot status"),
        ("$changenick @user NewNick", "Change user nickname"),
        ("$clearbot 50", "Delete 50 bot messages"),
        ("$goodmorning", "Send good morning message"),
        ("$sendembed", "Send example embed"),
        ("$serverinfo", "Get server information"),
        ("$channelinfo", "Get channel information"),
        ("$setwelcome Welcome {user}!", "Set welcome message"),
        ("$setleave Goodbye {user}!", "Set leave message"),
        ("$setwelcomechannel #welcome", "Set welcome channel"),
        ("$setleavechannel #goodbye", "Set leave channel"),
        ("$welcomeinfo", "Show welcome/leave settings"),
        ("$testwelcome", "Test welcome message"),
        ("$testleave", "Test leave message")
    ]
    lines = [f"{i:2d}. {usage:<25} - {description}" for i, (usage, description) in enumerate(examples, 1)]
    lines.append("")
    lines.append("0. Back to Main Menu")
    print_boxed_centered(lines, title="COMMAND USAGE EXAMPLES")

def show_bot_status():
    """Display bot status with gradient text, centered and boxed"""
    clear_screen()
    show_ascii_art()
    lines = []
    if bot.user:
        lines.append(f"Bot Name: {bot.user}")
        lines.append(f"Bot ID: {bot.user.id}")
        lines.append(f"Connected to {len(bot.guilds)} server(s)")
        lines.append(f"Latency: {round(bot.latency * 1000)}ms")
        lines.append(f"Status: Online")
    else:
        lines.append(f"Bot Status: Starting up...")
    lines.append("")
    lines.append("0. Back to Main Menu")
    print_boxed_centered(lines, title="BOT STATUS")

def show_command_logs():
    """Display all command logs with gradient text, updating in real time, centered and boxed. Press 'q' to exit."""
    def get_key():
        if os.name == 'nt':
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8').lower()
        else:
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if dr:
                return sys.stdin.read(1).lower()
        return None
    try:
        while True:
            clear_screen()
            show_ascii_art()
            if not command_logs:
                lines = ["No command logs yet."]
            else:
                lines = command_logs[-100:]
            lines.append("")
            lines.append("Press 'q' to return to the main menu.")
            print_boxed_centered(lines, title="COMMAND USAGE LOGS (LIVE)")
            for _ in range(10):
                key = get_key()
                if key == 'q':
                    return
                time.sleep(0.1)
    except KeyboardInterrupt:
        return

def change_bot_status():
    """Interactive bot status changer with gradient text, centered and boxed"""
    clear_screen()
    show_ascii_art()
    options = [
        "1. Playing",
        "2. Streaming",
        "3. Listening",
        "4. Watching",
        "5. Clear Status",
        "0. Back to Main Menu"
    ]
    lines = options.copy()
    lines.append("")
    lines.append("Enter your choice (0-5): ")
    print_boxed_centered(lines, title="CHANGE BOT STATUS")
    try:
        choice = input().strip()
        if choice == "0":
            return
        elif choice in ["1", "2", "3", "4"]:
            message = input("Enter the status message: ").strip()
            if not message:
                print_boxed_centered(["Status message cannot be empty!", "", "Press Enter to continue..."], title="CHANGE BOT STATUS")
                input()
                return
            activity_type = ""
            if choice == "1":
                activity_type = "playing"
                activity = discord.Game(name=message)
            elif choice == "2":
                activity_type = "streaming"
                activity = discord.Streaming(name=message, url="https://twitch.tv/yourchannel")
            elif choice == "3":
                activity_type = "listening"
                activity = discord.Activity(type=discord.ActivityType.listening, name=message)
            elif choice == "4":
                activity_type = "watching"
                activity = discord.Activity(type=discord.ActivityType.watching, name=message)
            asyncio.run_coroutine_threadsafe(bot.change_presence(activity=activity), bot.loop)
            print_boxed_centered([f"✅ Status updated to **{activity_type}**: {message}", "", "Press Enter to continue..."], title="CHANGE BOT STATUS")
            input()
        elif choice == "5":
            asyncio.run_coroutine_threadsafe(bot.change_presence(activity=None), bot.loop)
            print_boxed_centered(["✅ Bot status cleared", "", "Press Enter to continue..."], title="CHANGE BOT STATUS")
            input()
        else:
            print_boxed_centered(["Invalid choice. Please enter a number between 0-5.", "", "Press Enter to continue..."], title="CHANGE BOT STATUS")
            input()
            return
    except Exception as e:
        print_boxed_centered([f"Error changing status: {e}", "", "Press Enter to continue..."], title="CHANGE BOT STATUS")
        input()

def terminal_menu():
    """Interactive terminal menu system with gradient text"""
    while True:
        show_main_menu()
        try:
            choice = input(f"\033[38;2;0;102;255mEnter your choice (0-8): \033[0m").strip()
            if choice == "0":
                print_gradient("Exiting menu...")
                break
            elif choice == "1":
                show_all_commands()
                input(f"\033[38;2;0;102;255mPress Enter to continue...\033[0m")
            elif choice == "2":
                show_admin_commands()
                input(f"\033[38;2;0;102;255mPress Enter to continue...\033[0m")
            elif choice == "3":
                show_info_commands()
                input(f"\033[38;2;0;102;255mPress Enter to continue...\033[0m")
            elif choice == "4":
                show_fun_commands()
                input(f"\033[38;2;0;102;255mPress Enter to continue...\033[0m")
            elif choice == "5":
                show_usage_examples()
                input(f"\033[38;2;0;102;255mPress Enter to continue...\033[0m")
            elif choice == "6":
                show_bot_status()
                input(f"\033[38;2;0;102;255mPress Enter to continue...\033[0m")
            elif choice == "7":
                change_bot_status()
            elif choice == "8":
                show_command_logs()
                # No input pause needed, handled in show_command_logs
            else:
                print_gradient("Invalid choice. Please enter a number between 0-8.")
                time.sleep(1)
        except KeyboardInterrupt:
            print_gradient("\nExiting menu...")
            break
        except Exception as e:
            print_gradient(f"Error: {e}")
            time.sleep(1)

@bot.event
async def on_ready():
    # Load welcome/leave messages
    load_welcome_leave_messages()
    
    # ASCII Art for Neruvy Bot with vertical gradient and centered
    ascii_art = """
    ███╗   ██╗███████╗██████╗ ██╗   ██╗██╗   ██╗██╗   ██╗
    ████╗  ██║██╔════╝██╔══██╗██║   ██║╚██╗ ██╔╝╚██╗ ██╔╝
    ██╔██╗ ██║█████╗  ██████╔╝██║   ██║ ╚████╔╝  ╚████╔╝ 
    ██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║  ╚██╔╝    ╚██╔╝  
    ██║ ╚████║███████╗██║  ██║╚██████╔╝   ██║      ██║   
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝      ╚═╝   
                                                            
    ██████╗  ██████╗ ████████╗                           
    ██╔══██╗██╔═══██╗╚══██╔══╝                           
    ██████╔╝██║   ██║   ██║                              
    ██╔══██╗██║   ██║   ██║                              
    ██████╔╝╚██████╔╝   ██║                              
    ╚═════╝  ╚═════╝    ╚═╝                              
    """
    width = shutil.get_terminal_size((80, 20)).columns
    centered_art = '\n'.join(line.center(width) for line in ascii_art.splitlines())
    print_gradient(centered_art, vertical=True)
    print_gradient(f'Bot is ready. Logged in as {bot.user}')
    if bot.user is not None:
        print_gradient(f'Bot ID: {bot.user.id}')
    else:
        print_gradient('Bot ID: (not available)')
    print_gradient(f'Connected to {len(bot.guilds)} guild(s)')
    print_gradient('=' * 50)
    print_gradient('Bot is now online and ready to receive commands!')
    print_gradient('=' * 50)
    print_gradient('\nStarting interactive terminal menu...')
    print_gradient('You can now use the menu to navigate through commands!')
    menu_thread = threading.Thread(target=terminal_menu, daemon=True)
    menu_thread.start()

@bot.event
async def on_command(ctx):
    """Log command usage only to command_logs list (not terminal)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = ctx.author
    command = ctx.command.name
    guild = ctx.guild.name if ctx.guild else "DM"
    channel = ctx.channel.name if hasattr(ctx.channel, 'name') else "DM"
    log_entry = f"[{timestamp}] COMMAND: {user} ({user.id}) used '{command}' in {guild} #{channel}"
    command_logs.append(log_entry)

@bot.event
async def on_command_error(ctx, error):
    """Log command errors to command_logs list (for menu display) and notify user if command not found."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = ctx.author
    command = ctx.command.name if ctx.command else "Unknown"
    guild = ctx.guild.name if ctx.guild else "DM"
    channel = ctx.channel.name if hasattr(ctx.channel, 'name') else "DM"
    log_entry = f"[{timestamp}] ERROR: {user} ({user.id}) failed to use '{command}' in {guild} #{channel} - {error}"
    command_logs.append(log_entry)
    if isinstance(error, CommandNotFound):
        await ctx.send("❌ That command does not exist. Please check your spelling or use `$help` for a list of commands.")

@bot.event
async def on_member_join(member):
    """Send welcome message when a member joins"""
    guild_id = str(member.guild.id)
    if guild_id in welcome_messages:
        message = welcome_messages[guild_id]
        formatted_message = format_message(message, member, member.guild)
        if formatted_message:
            # Get the specific welcome channel if set
            channel = None
            if guild_id in welcome_channels:
                channel_id = welcome_channels[guild_id]
                channel = member.guild.get_channel(channel_id)
            
            # Fallback to system channel or first text channel
            if not channel:
                channel = member.guild.system_channel
                if not channel:
                    text_channels = [c for c in member.guild.text_channels if c.permissions_for(member.guild.me).send_messages]
                    if text_channels:
                        channel = text_channels[0]
            
            if channel:
                try:
                    embed = discord.Embed(
                        title="🎉 Welcome!",
                        description=formatted_message,
                        color=discord.Color.green(),
                        timestamp=datetime.now()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"Member #{member.guild.member_count}")
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Error sending welcome message: {e}")

@bot.event
async def on_member_remove(member):
    """Send leave message when a member leaves"""
    guild_id = str(member.guild.id)
    if guild_id in leave_messages:
        message = leave_messages[guild_id]
        formatted_message = format_message(message, member, member.guild)
        if formatted_message:
            # Get the specific leave channel if set
            channel = None
            if guild_id in leave_channels:
                channel_id = leave_channels[guild_id]
                channel = member.guild.get_channel(channel_id)
            
            # Fallback to system channel or first text channel
            if not channel:
                channel = member.guild.system_channel
                if not channel:
                    text_channels = [c for c in member.guild.text_channels if c.permissions_for(member.guild.me).send_messages]
                    if text_channels:
                        channel = text_channels[0]
            
            if channel:
                try:
                    embed = discord.Embed(
                        title="👋 Goodbye!",
                        description=formatted_message,
                        color=discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"Member left - {member.guild.member_count} members remaining")
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Error sending leave message: {e}")

@bot.command(help="Sends a good morning message to the user")
async def goodmorning(ctx):
    await ctx.send(f"Good morning, {ctx.author.mention}!")

@bot.command(help="Sends an example embed message")
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

@bot.command(help="Shows the bot's latency/ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="Ping",
        description="Latency in ms",
        color=discord.Color.blue()
    )
    embed.add_field(name=f"{bot.user.name if bot.user else 'Bot'}'s Latency:", value=f"{latency}ms", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}.", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='ban', help="Bans a member from the server")
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

@bot.command(name='kick', help="Kicks a member from the server")
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

@bot.command(name='say', help="Makes the bot say a message (deletes your command)")
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

@bot.command(name='addrole', help="Adds a role to a member")
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

@bot.command(name='removerole', help="Removes a role from a member")
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

@bot.command(name='setstatus', help="Sets the bot's status (playing, streaming, listening, watching)")
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

@bot.command(name='changenick', help="Changes a member's nickname")
@commands.has_permissions(manage_nicknames=True)
async def change_nickname(ctx, member: discord.Member, *, new_nickname: str):
    try:
        await member.edit(nick=new_nickname)
        await ctx.send(f"✅ Changed nickname for {member.mention} to `{new_nickname}`.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to change that user's nickname.")
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred: {e}")

@bot.command(name='userinfo', help="Shows information about a user")
async def user_info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # Default to the invoker

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

@bot.command(name='channelinfo', help="Shows information about a channel")
async def channel_info(ctx, channel: discord.abc.GuildChannel = None):
    if channel is None:
        channel = ctx.channel  # Defaults to the channel the command was used in

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

@bot.command(name='clearbot', help="Deletes bot messages from the channel")
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

@bot.command(name='poll', help="Creates a poll with multiple options")
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

@bot.command(name='serverinfo', help="Shows information about the server")
async def server_info(ctx):
    guild = ctx.guild

    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Server Name", value=guild.name, inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

    await ctx.send(embed=embed)

@bot.command(name='setwelcome', help="Set a custom welcome message for the server")
@commands.has_permissions(manage_guild=True)
async def set_welcome_message(ctx, *, message: str):
    """Set a custom welcome message for the server"""
    guild_id = str(ctx.guild.id)
    welcome_messages[guild_id] = message
    save_welcome_leave_messages()
    
    embed = discord.Embed(
        title="✅ Welcome Message Set!",
        description=f"**New welcome message:**\n{message}",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Available Placeholders",
        value="`{user}` - User mention\n`{user.name}` - Username\n`{user.display_name}` - Display name\n`{user.id}` - User ID\n`{server}` - Server name\n`{server.member_count}` - Member count\n`{user.created_at}` - Account creation date\n`{user.joined_at}` - Join date",
        inline=False
    )
    await ctx.send(embed=embed)

@set_welcome_message.error
async def set_welcome_message_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the 'Manage Server' permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please provide a welcome message. Usage: `$setwelcome Welcome {user} to {server}!`")

@bot.command(name='setleave', help="Set a custom leave message for the server")
@commands.has_permissions(manage_guild=True)
async def set_leave_message(ctx, *, message: str):
    """Set a custom leave message for the server"""
    guild_id = str(ctx.guild.id)
    leave_messages[guild_id] = message
    save_welcome_leave_messages()
    
    embed = discord.Embed(
        title="✅ Leave Message Set!",
        description=f"**New leave message:**\n{message}",
        color=discord.Color.orange()
    )
    embed.add_field(
        name="Available Placeholders",
        value="`{user}` - User mention\n`{user.name}` - Username\n`{user.display_name}` - Display name\n`{user.id}` - User ID\n`{server}` - Server name\n`{server.member_count}` - Member count\n`{user.created_at}` - Account creation date\n`{user.joined_at}` - Join date",
        inline=False
    )
    await ctx.send(embed=embed)

@set_leave_message.error
async def set_leave_message_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the 'Manage Server' permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please provide a leave message. Usage: `$setleave Goodbye {user}! We'll miss you!`")

@bot.command(name='welcomeinfo', help="Show current welcome and leave message settings")
async def welcome_info(ctx):
    """Show current welcome and leave message settings"""
    guild_id = str(ctx.guild.id)
    
    embed = discord.Embed(
        title="🎉 Welcome/Leave Message Settings",
        color=discord.Color.blue()
    )
    
    # Welcome message
    welcome_msg = welcome_messages.get(guild_id, "Not set")
    embed.add_field(
        name="Welcome Message",
        value=f"```{welcome_msg}```" if welcome_msg != "Not set" else "Not set",
        inline=False
    )
    
    # Welcome channel
    welcome_channel = "Not set"
    if guild_id in welcome_channels:
        channel = ctx.guild.get_channel(welcome_channels[guild_id])
        welcome_channel = channel.mention if channel else "Channel not found"
    embed.add_field(
        name="Welcome Channel",
        value=welcome_channel,
        inline=True
    )
    
    # Leave message
    leave_msg = leave_messages.get(guild_id, "Not set")
    embed.add_field(
        name="Leave Message",
        value=f"```{leave_msg}```" if leave_msg != "Not set" else "Not set",
        inline=False
    )
    
    # Leave channel
    leave_channel = "Not set"
    if guild_id in leave_channels:
        channel = ctx.guild.get_channel(leave_channels[guild_id])
        leave_channel = channel.mention if channel else "Channel not found"
    embed.add_field(
        name="Leave Channel",
        value=leave_channel,
        inline=True
    )
    
    embed.add_field(
        name="Available Placeholders",
        value="`{user}` `{user.name}` `{user.display_name}` `{user.id}` `{server}` `{server.member_count}` `{user.created_at}` `{user.joined_at}`",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='clearwelcome', help="Clear the welcome message for the server")
@commands.has_permissions(manage_guild=True)
async def clear_welcome_message(ctx):
    """Clear the welcome message for the server"""
    guild_id = str(ctx.guild.id)
    if guild_id in welcome_messages:
        del welcome_messages[guild_id]
        save_welcome_leave_messages()
        await ctx.send("✅ Welcome message has been cleared!")
    else:
        await ctx.send("ℹ️ No welcome message was set for this server.")

@bot.command(name='clearleave', help="Clear the leave message for the server")
@commands.has_permissions(manage_guild=True)
async def clear_leave_message(ctx):
    """Clear the leave message for the server"""
    guild_id = str(ctx.guild.id)
    if guild_id in leave_messages:
        del leave_messages[guild_id]
        save_welcome_leave_messages()
        await ctx.send("✅ Leave message has been cleared!")
    else:
        await ctx.send("ℹ️ No leave message was set for this server.")

@bot.command(name='testwelcome', help="Test the welcome message (Admin only)")
@commands.has_permissions(manage_guild=True)
async def test_welcome_message(ctx):
    """Test the welcome message"""
    guild_id = str(ctx.guild.id)
    if guild_id in welcome_messages:
        message = welcome_messages[guild_id]
        formatted_message = format_message(message, ctx.author, ctx.guild)
        if formatted_message:
            embed = discord.Embed(
                title="🎉 Welcome! (Test)",
                description=formatted_message,
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.set_footer(text=f"Member #{ctx.guild.member_count} (Test)")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Error formatting welcome message.")
    else:
        await ctx.send("❌ No welcome message is set for this server.")

@bot.command(name='testleave', help="Test the leave message (Admin only)")
@commands.has_permissions(manage_guild=True)
async def test_leave_message(ctx):
    """Test the leave message"""
    guild_id = str(ctx.guild.id)
    if guild_id in leave_messages:
        message = leave_messages[guild_id]
        formatted_message = format_message(message, ctx.author, ctx.guild)
        if formatted_message:
            embed = discord.Embed(
                title="👋 Goodbye! (Test)",
                description=formatted_message,
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.set_footer(text=f"Member left - {ctx.guild.member_count} members remaining (Test)")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Error formatting leave message.")
    else:
        await ctx.send("❌ No leave message is set for this server.")

@bot.command(name='setwelcomechannel', help="Set the channel for welcome messages")
@commands.has_permissions(manage_guild=True)
async def set_welcome_channel(ctx, channel: discord.TextChannel):
    """Set the channel for welcome messages"""
    guild_id = str(ctx.guild.id)
    welcome_channels[guild_id] = channel.id
    save_welcome_leave_messages()
    
    embed = discord.Embed(
        title="✅ Welcome Channel Set!",
        description=f"Welcome messages will now be sent to {channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@set_welcome_channel.error
async def set_welcome_channel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the 'Manage Server' permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please mention a channel. Usage: `$setwelcomechannel #channel`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid text channel. Usage: `$setwelcomechannel #channel`")

@bot.command(name='setleavechannel', help="Set the channel for leave messages")
@commands.has_permissions(manage_guild=True)
async def set_leave_channel(ctx, channel: discord.TextChannel):
    """Set the channel for leave messages"""
    guild_id = str(ctx.guild.id)
    leave_channels[guild_id] = channel.id
    save_welcome_leave_messages()
    
    embed = discord.Embed(
        title="✅ Leave Channel Set!",
        description=f"Leave messages will now be sent to {channel.mention}",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

@set_leave_channel.error
async def set_leave_channel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the 'Manage Server' permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please mention a channel. Usage: `$setleavechannel #channel`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid text channel. Usage: `$setleavechannel #channel`")

@bot.command(name='clearwelcomechannel', help="Clear the welcome channel setting")
@commands.has_permissions(manage_guild=True)
async def clear_welcome_channel(ctx):
    """Clear the welcome channel setting"""
    guild_id = str(ctx.guild.id)
    if guild_id in welcome_channels:
        del welcome_channels[guild_id]
        save_welcome_leave_messages()
        await ctx.send("✅ Welcome channel has been cleared! Messages will use the system channel or fallback.")
    else:
        await ctx.send("ℹ️ No welcome channel was set for this server.")

@bot.command(name='clearleavechannel', help="Clear the leave channel setting")
@commands.has_permissions(manage_guild=True)
async def clear_leave_channel(ctx):
    """Clear the leave channel setting"""
    guild_id = str(ctx.guild.id)
    if guild_id in leave_channels:
        del leave_channels[guild_id]
        save_welcome_leave_messages()
        await ctx.send("✅ Leave channel has been cleared! Messages will use the system channel or fallback.")
    else:
        await ctx.send("ℹ️ No leave channel was set for this server.")

# Start the bot
bot.run("MTM3MDc3MDIwOTIwNzc1MDcxOQ.GjBArS.JAWHxAi8h628uV8OYoKvQ2f6jobh9u0TM4R0SM")
