# Discord Bot

A feature-rich Discord bot with moderation and utility.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Environment File**
   Create a `.env` file in the same directory as `main.py` with your bot token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

3. **Run the Bot**
   ```bash
   python main.py
   ```

## Commands

- `$goodmorning` - Greets the user
- `$ping` - Shows bot latency
- `$sendembed` - Sends a sample embed
- `$ban @user [reason]` - Bans a user (requires ban permissions)
- `$kick @user [reason]` - Kicks a user (requires kick permissions)
- `$say <message>` - Makes the bot say something (requires manage messages)
- `$addrole @user @role` - Adds a role to a user (requires manage roles)
- `$removerole @user @role` - Removes a role from a user (requires manage roles)
- `$setstatus <type> <message>` - Sets bot status (requires admin)
- `$changenick @user <nickname>` - Changes user nickname (requires manage nicknames)
- `$userinfo [@user]` - Shows user information
- `$channelinfo [#channel]` - Shows channel information
- `$clearbot [limit]` - Clears bot messages (requires manage messages)
- `$poll "question" option1 option2...` - Creates a poll with reactions
- `$serverinfo` - Shows server information

## Welcome/Leave Message System

The bot includes an automated welcome and leave message system with customizable messages:

### Welcome/Leave Commands
- `$setwelcome <message>` - Set a custom welcome message (requires manage server)
- `$setleave <message>` - Set a custom leave message (requires manage server)
- `$setwelcomechannel #channel` - Set specific channel for welcome messages (requires manage server)
- `$setleavechannel #channel` - Set specific channel for leave messages (requires manage server)
- `$welcomeinfo` - Show current welcome/leave message settings
- `$clearwelcome` - Clear the welcome message (requires manage server)
- `$clearleave` - Clear the leave message (requires manage server)
- `$clearwelcomechannel` - Clear welcome channel setting (requires manage server)
- `$clearleavechannel` - Clear leave channel setting (requires manage server)
- `$testwelcome` - Test the welcome message (requires manage server)
- `$testleave` - Test the leave message (requires manage server)

### Available Placeholders
You can use these placeholders in your welcome/leave messages:
- `{user}` - User mention
- `{user.name}` - Username
- `{user.display_name}` - Display name
- `{user.id}` - User ID
- `{server}` - Server name
- `{server.member_count}` - Member count
- `{user.created_at}` - Account creation date
- `{user.joined_at}` - Join date

### Example Usage
```
$setwelcome Welcome {user} to {server}! You are member #{server.member_count}
$setleave Goodbye {user}! We'll miss you in {server}!
$setwelcomechannel #welcome
$setleavechannel #goodbye
```

## Security Note

⚠️ **IMPORTANT**: Never share your bot token publicly. The token in the code has been moved to a `.env` file for security. Make sure to add `.env` to your `.gitignore` file if using version control. 
