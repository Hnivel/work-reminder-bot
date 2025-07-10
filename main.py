import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
from dateutil import parser

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


def init_database():
    connect = sqlite3.connect('reminders.db')
    cursor = connect.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_id INTEGER,
            guild_id INTEGER,
            content TEXT,
            event_time TEXT,
            reminder_1day INTEGER DEFAULT 0,
            reminder_30min INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    connect.commit()
    connect.close()


init_database()

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.loop.create_task(check_reminders())


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f'Welcome {member.mention} to the server!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() in ['gen', 'geng', 'gen.g']:
        await message.channel.send(f"{message.author.mention} The best team in League of Legends!")

    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')


@bot.command()
async def work(ctx, *, content=None):
    """Create a work reminder with specified content and time"""
    if not content:
        await ctx.send("Please provide the work content. Usage: `!work <your work description>`")
        return

    await ctx.send(f"📅 **Work Reminder Setup**\n\nContent: {content}\n\nPlease enter the date and time for this event.\n\n**Examples:**\n- `2025-07-15 14:30` (July 15, 2025 at 2:30 PM)\n- `Tomorrow 9AM`\n- `Next Monday 10:00`\n- `July 20 3PM`\n\n*Type your desired time:*")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        time_msg = await bot.wait_for('message', check=check, timeout=60.0)
        time_input = time_msg.content

        # Parse the time input
        try:
            event_time = parser.parse(time_input, fuzzy=True)

            if event_time <= datetime.now():
                await ctx.send("❌ The specified time must be in the future. Please try again with `!work <content>`")
                return

            # Save to database
            connect = sqlite3.connect('reminders.db')
            cursor = connect.cursor()
            cursor.execute('''
                INSERT INTO reminders (user_id, channel_id, guild_id, content, event_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ctx.author.id, ctx.channel.id, ctx.guild.id if ctx.guild else None,
                  content, event_time.isoformat(), datetime.now().isoformat()))
            connect.commit()
            connect.close()

            # Calculate reminder times
            reminder_1day = event_time - timedelta(days=1)
            reminder_30min = event_time - timedelta(minutes=30)

            embed = discord.Embed(
                title="✅ Work Reminder Created!",
                description=f"**Content:** {content}\n**Event Time:** {event_time.strftime('%A, %B %d, %Y at %I:%M %p')}",

                color=0x00ff00
            )

            reminder_info = []
            if reminder_1day > datetime.now():
                reminder_info.append(
                    f"📅 1 day before: {reminder_1day.strftime('%A, %B %d at %I:%M %p')}")
            if reminder_30min > datetime.now():
                reminder_info.append(
                    f"⏰ 30 minutes before: {reminder_30min.strftime('%A, %B %d at %I:%M %p')}")

            if reminder_info:
                embed.add_field(name="Reminders will be sent:",
                                value="\n".join(reminder_info), inline=False)
            else:
                embed.add_field(
                    name="Note:", value="Event is too soon for advance reminders", inline=False)

            await ctx.send(embed=embed)

        except (ValueError, parser.ParserError):
            await ctx.send("❌ I couldn't understand that time format. Please try again with `!work <content>` and use a clear date/time format.")
            return

    except asyncio.TimeoutError:
        await ctx.send("⏰ Time's up! Please try again with `!work <content>`")


@bot.command()
async def reminders(ctx):
    """List all active reminders for the user"""
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT content, event_time FROM reminders 
        WHERE user_id = ? AND event_time > ? 
        ORDER BY event_time
    ''', (ctx.author.id, datetime.now().isoformat()))

    results = cursor.fetchall()
    conn.close()

    if not results:
        await ctx.send("📭 You have no active reminders.")
        return

    embed = discord.Embed(
        title="📋 Your Active Reminders",
        color=0x0099ff
    )

    for i, (content, event_time_str) in enumerate(results, 1):
        event_time = datetime.fromisoformat(event_time_str)
        time_until = event_time - datetime.now()

        if time_until.days > 0:
            time_str = f"in {time_until.days} day{'s' if time_until.days != 1 else ''}"
        elif time_until.seconds > 3600:
            hours = time_until.seconds // 3600
            time_str = f"in {hours} hour{'s' if hours != 1 else ''}"
        else:
            minutes = time_until.seconds // 60
            time_str = f"in {minutes} minute{'s' if minutes != 1 else ''}"

        embed.add_field(
            name=f"{i}. {content[:50]}{'...' if len(content) > 50 else ''}",
            value=f"📅 {event_time.strftime('%m/%d/%Y at %I:%M %p')}\n⏱️ {time_str}",
            inline=False
        )

    await ctx.send(embed=embed)


async def check_reminders():
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            now = datetime.now()
            connect = sqlite3.connect('reminders.db')
            cursor = connect.cursor()

            # Check for 1-day reminders
            cursor.execute('''
                SELECT id, user_id, channel_id, content, event_time FROM reminders
                WHERE reminder_1day = 0 AND event_time > ? AND event_time <= ?
            ''', (now.isoformat(), (now + timedelta(days=1, minutes=5)).isoformat()))

            day_reminders = cursor.fetchall()

            for reminder_id, user_id, channel_id, content, event_time_str in day_reminders:
                try:
                    channel = bot.get_channel(channel_id)
                    user = bot.get_user(user_id)
                    event_time = datetime.fromisoformat(event_time_str)

                    if channel and user:
                        embed = discord.Embed(
                            title="📅 1-Day Reminder",
                            description=f"**{content}**\n\nScheduled for: {event_time.strftime('%A, %B %d at %I:%M %p')}",

                            color=0xffaa00
                        )
                        await channel.send(f"{user.mention}", embed=embed)

                        # Mark as sent
                        cursor.execute(
                            'UPDATE reminders SET reminder_1day = 1 WHERE id = ?', (reminder_id,))
                except Exception as e:
                    print(f"Error sending 1-day reminder: {e}")

            # Check for 30-minute reminders
            cursor.execute('''
                SELECT id, user_id, channel_id, content, event_time FROM reminders
                WHERE reminder_30min = 0 AND event_time > ? AND event_time <= ?
            ''', (now.isoformat(), (now + timedelta(minutes=35)).isoformat()))

            min_reminders = cursor.fetchall()

            for reminder_id, user_id, channel_id, content, event_time_str in min_reminders:
                try:
                    channel = bot.get_channel(channel_id)
                    user = bot.get_user(user_id)
                    event_time = datetime.fromisoformat(event_time_str)

                    if channel and user:
                        embed = discord.Embed(
                            title="⏰ 30-Minute Reminder",
                            description=f"**{content}**\n\nScheduled for: {event_time.strftime('%A, %B %d at %I:%M %p')}\n\n*This is your final reminder!*",

                            color=0xff4444
                        )
                        await channel.send(f"{user.mention}", embed=embed)

                        # Mark as sent
                        cursor.execute(
                            'UPDATE reminders SET reminder_30min = 1 WHERE id = ?', (reminder_id,))
                except Exception as e:
                    print(f"Error sending 30-min reminder: {e}")

            # Clean up old reminders (older than 1 week past event time)
            week_ago = now - timedelta(weeks=1)
            cursor.execute(
                'DELETE FROM reminders WHERE event_time < ?', (week_ago.isoformat(),))

            connect.commit()
            connect.close()

        except Exception as e:
            print(f"Error in reminder checker: {e}")

        await asyncio.sleep(60)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
