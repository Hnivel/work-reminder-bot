# Discord Work Reminder Bot

A Discord bot that helps you manage work reminders with automatic notifications.
## Features

🎯 **Work Reminders**: Create reminders for any work-related task or event  
📅 **1-Day Warning**: Get reminded 24 hours before your event  
⏰ **30-Minute Warning**: Get reminded 30 minutes before your event  
📝 **Flexible Time Input**: Use natural language for dates and times  
📋 **View Active Reminders**: List all your upcoming reminders  
💾 **Persistent Storage**: Reminders survive bot restarts  
🧹 **Auto Cleanup**: Old reminders are automatically deleted  

## Commands

### `!work <content>`

Create a new work reminder with the specified content. The bot will ask you to specify when the event should occur.

**Example:**

```
!work Complete project presentation
```

The bot will then prompt you for the time. You can use formats like:

- `2025-07-15 14:30` (July 15, 2025 at 2:30 PM)
- `Tomorrow 9AM`
- `Next Monday 10:00`
- `July 20 3PM`

### `!reminders`

Display all your active reminders in a nice formatted list.

### `!hello`

Simple greeting command to test if the bot is working.

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- A Discord Bot Token

### 1. Clone or Download

Download this project to your local machine.

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Set Up Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Copy the bot token
5. Create a `.env` file in the project directory:

```
DISCORD_TOKEN=your_bot_token_here
```

### 4. Invite Bot to Your Server

1. In the Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes: `bot`
3. Select bot permissions:
   - Send Messages
   - Use Slash Commands
   - Read Message History
   - Mention Everyone
4. Use the generated URL to invite the bot to your server

### 5. Run the Bot

```powershell
python main.py
```

## Bot Permissions Required

The bot needs the following permissions in your Discord server:

- **Send Messages**: To send reminders and responses
- **Read Message History**: To read your commands
- **Use External Emojis**: For better formatting
- **Mention @everyone, @here, and All Roles**: To mention you in reminders

## How Reminders Work

1. **Create**: Use `!work <content>` and specify a time
2. **Storage**: Reminder is saved to local SQLite database
3. **Background Checking**: Bot checks every minute for due reminders
4. **Notifications**: You'll get pinged at:
   - 24 hours before the event
   - 30 minutes before the event
5. **Cleanup**: Old reminders are automatically deleted after 1 week

## Example Usage

```
User: !work Submit quarterly report
Bot: 📅 Work Reminder Setup

Content: Submit quarterly report

Please enter the date and time for this event.

Examples:
- 2025-07-15 14:30 (July 15, 2025 at 2:30 PM)
- Tomorrow 9AM
- Next Monday 10:00
- July 20 3PM

Type your desired time:

User: Friday 5PM
Bot: ✅ Work Reminder Created!
Content: Submit quarterly report
Event Time: Friday, July 11, 2025 at 05:00 PM

Reminders will be sent:
📅 1 day before: Thursday, July 10 at 05:00 PM
⏰ 30 minutes before: Friday, July 11 at 04:30 PM
```

## Files Structure

```
discord-bots/
├── main.py              
├── requirements.txt    # Python dependencies
├── .env
├── discord.log         # Bot logs (auto-generated)
├── reminders.db        # SQLite database (auto-generated)
└── README.md           
```

## Dependencies

- **discord.py**: Discord API wrapper
- **python-dotenv**: Environment variable management
- **python-dateutil**: Advanced date/time parsing
- **sqlite3**: Database (built into Python)
- **asyncio**: Asynchronous programming (built into Python)
