import os
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError

TELEGRAM_BOT_TOKEN = '8002977853:AAFcXX4h0N0fvGx2R5uZTAI0e7aomScqlwE'
ALLOWED_USER_ID = '7355703826'  # Admin's user ID
ADMIN_USERNAME = '@AVxAAYU'  # Admin username
allowed_user_ids = []  # List of allowed users
USER_FILE = "allowed_users.txt"  # File where user IDs will be stored

# Automatically add admin when the bot starts
def add_admin():
    duration_in_days = 99  # Admin's access duration in days
    duration_in_seconds = duration_in_days * 24 * 60 * 60  # Convert days to seconds
    allowed_user_ids.append(ALLOWED_USER_ID)
    with open(USER_FILE, "a") as file:
        file.write(f"{ALLOWED_USER_ID}\n")
    print(f"Admin user {ALLOWED_USER_ID} added for {duration_in_days} days.")

# Start command
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let FUCK BGMI! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Attack command
async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if the user is approved
    if str(user_id) not in allowed_user_ids:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"*❌ You are not authorized to use this bot! Please contact admin {ADMIN_USERNAME}*",
            parse_mode='Markdown'
        )
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args

    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

# Run attack simulation
async def run_attack(chat_id, ip, port, duration, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./attack <ip> <port> <duration> 900",  # Replace with actual attack command if needed
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

# Add user command
async def add(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)  # Get the user ID

    # Only allow the original admin to add users
    if user_id != ALLOWED_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text=f"*❌ You are not authorized to add users!* Please contact admin {ADMIN_USERNAME}", parse_mode='Markdown')
        return

    # Check if there's a command argument (user ID to add)
    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /add <user_id>*", parse_mode='Markdown')
        return

    user_to_add = context.args[0]

    # Check if user already exists in allowed users list
    if user_to_add in allowed_user_ids:
        response = "User already exists 🤦‍♂️."
    else:
        allowed_user_ids.append(user_to_add)
        with open(USER_FILE, "a") as file:
            file.write(f"{user_to_add}\n")
        response = f"User {user_to_add} Added Successfully 👍."

    await context.bot.send_message(chat_id=chat_id, text=response, parse_mode='Markdown')

# Users command to list all allowed users
async def users(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)  # Get the user ID

    # Only allow the original admin to view the list of users
    if user_id != ALLOWED_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text=f"*❌ You are not authorized to view the users list!* Please contact admin {ADMIN_USERNAME}", parse_mode='Markdown')
        return

    # If the allowed user IDs list is empty
    if not allowed_user_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ No users are currently approved!*", parse_mode='Markdown')
        return

    # Create a message to list all the users
    message = "*📜 List of Approved Users:*\n"
    for user in allowed_user_ids:
        message += f"\n*User ID*: {user}"

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Main function to set up the bot
def main():
    add_admin()  # Automatically add the admin when the bot starts
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("add", add))  # /add to add users
    application.add_handler(CommandHandler("users", users))  # /users to list all users

    application.run_polling()

if __name__ == '__main__':
    main()