import asyncio
import logging
from aiohttp import web
import aiohttp_jinja2
import jinja2
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils import executor
from environs import Env
BOT_TOKEN = "6237932576:AAFiXs2J4caQG1aGycoaah0IuRU2IsMe5Dc"

ENDPOINT = "https://www.canva.com/brand/join?token=2YjFf01xvIS38UY23l6nyA&referrer=team-invite"

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

logging.basicConfig(level=logging.ERROR)

# Placeholder function for web_start
async def web_start(request):
    # Your implementation here
    return web.Response(text="Web Start Placeholder")

# Placeholder function for web_send_message
async def web_send_message(request):
    # Your implementation here
    return web.Response(text="Web Send Message Placeholder")

# Placeholder function for web_check_user_data
async def web_check_user_data(request):
    # Your implementation here
    return web.Response(text="Web Check User Data Placeholder")

app = web.Application()
app.add_routes([web.get('/web-start', web_start),
                web.post('/sendMessage', web_send_message),
                web.post('/checkUserData', web_check_user_data)])
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('web'), enable_async=True)

async def on_startup(dps: Dispatcher):
    loop = asyncio.get_event_loop()
    loop.create_task(web._run_app(app, host="0.0.0.0", port=45678))

async def on_shutdown(dps: Dispatcher):
    await dps.storage.close()
    await dps.storage.wait_closed()

import datetime

import asyncio

# Define a function to delete buttons after a specified delay
async def delete_buttons(chat_id, message_id, delay_minutes):
    await asyncio.sleep(delay_minutes * 60)  # Convert minutes to seconds
    await bot.delete_message(chat_id, message_id)

@dp.message_handler(CommandStart())
async def cmd_start(msg: types.Message):
    user_id = msg.from_user.id
    is_member_abhicanva = await bot.get_chat_member("@abhicanva", user_id)
    is_member_abyproof = await bot.get_chat_member("@abyproof", user_id)
    
    if (is_member_abhicanva.status == "member" or is_member_abhicanva.status == "administrator" or is_member_abhicanva.status == "creator") and \
       (is_member_abyproof.status == "member" or is_member_abyproof.status == "administrator" or is_member_abyproof.status == "creator"):
        
        # Provide instructions for Canva login
        login_instructions = "To join the Canva team, please log in using your email and enter the OTP you receive."
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="😎 Join Canva Team", web_app=types.WebAppInfo(url=f"{ENDPOINT}"))]
        ])
        
        # Send the instructions message
        instructions_message = await msg.reply(login_instructions, reply_markup=keyboard)
        
        # Schedule the deletion of buttons after 10 minutes
        asyncio.create_task(delete_buttons(instructions_message.chat.id, instructions_message.message_id, delay_minutes=10))
        
    else:
        # Create inline keyboard buttons to join channels
        join_abhicanva_button = types.InlineKeyboardButton("Join @abhicanva", url="https://cosmofeed.com/vig/653a165dd2c541001d1c452e")
        join_abyproof_button = types.InlineKeyboardButton("Join @abyproof", url="https://t.me/abyproof")
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [join_abhicanva_button, join_abyproof_button]
        ])
        
        # Send the instructions message
        instructions_message = await msg.reply("To use this bot, please join both @abhicanva by paying and @abyproof channels by clicking the respective links below and then restart the bot.", reply_markup=keyboard)
        
        # Schedule the deletion of buttons after 10 minutes
        asyncio.create_task(delete_buttons(instructions_message.chat.id, instructions_message.message_id, delay_minutes=10))

def main():
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

if __name__ == "__main__":
    main()
