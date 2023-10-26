
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict
import asyncio

API_TOKEN = '6119053767:AAG7N06GXeHT8dAlWyQ3z86XnHjMfqapOAE'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
votes = defaultdict(lambda: defaultdict(int)) # user_id: {voter_id: vote}
ban_counts = defaultdict(int)



from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = """
Hello! I'm here to help manage this group. Here's what I can do:

1. Any user can initiate a vote to ban another user by replying to their message with the /ban command.
2. After reaching 5 votes in 5 Min.. user will be banned from Group.

Please use these commands responsibly!
    """
    
    # Create an inline keyboard with a "Add to Group" button
    keyboard = InlineKeyboardMarkup()
    add_to_group_button = InlineKeyboardButton("Add to Group", url=f"https://t.me/banbyvotebot?startgroup=start")
    keyboard.add(add_to_group_button)

    await message.answer(welcome_text, reply_markup=keyboard)


@dp.message_handler(content_types=['new_chat_members'])
async def welcome_new_member(message: types.Message):
    for new_member in message.new_chat_members:
        welcome_message = await bot.send_message(chat_id=message.chat.id, text=f'Welcome, {new_member.full_name}!\n\nPlease follow the guidelines:\n1. Be respectful to each other.\n2. No spamming.\n3. Stay on topic.')
        await asyncio.sleep(300)  # Wait for 1 minute
        await welcome_message.delete()  # Delete the welcome message
    await message.delete()  # Delete the service message about new members



@dp.message_handler(commands=['ban'])
async def start_vote(message: types.Message):
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else None
    if user_id:
        user_status = await bot.get_chat_member(chat_id=message.chat.id, user_id=user_id)
        if user_status.status not in ['creator', 'administrator']:  # Don't start vote for admin/owner
            keyboard = InlineKeyboardMarkup()
            ban_btn = InlineKeyboardButton("Ban", callback_data=f"ban_{user_id}")
            unban_btn = InlineKeyboardButton("Unban", callback_data=f"unban_{user_id}")
            keyboard.add(ban_btn, unban_btn)
            vote_message = await bot.send_message(chat_id=message.chat.id, text='Voting started. Choose an option:', reply_markup=keyboard)
            await asyncio.sleep(300)  # Wait for 1 minute
            await vote_message.delete()  # Delete the vote message
        else:
            await message.reply('You can\'t start a ban vote for an admin or the group owner.')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ban_'))
async def process_callback_ban(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    voter_id = callback_query.from_user.id

    if votes[user_id][voter_id] == 0:
        votes[user_id][voter_id] = 1
        ban_counts[user_id] += 1

    if ban_counts[user_id] >= 5: # If ban votes reach 2
        try:
            await bot.kick_chat_member(chat_id=callback_query.message.chat.id, user_id=user_id)
            await bot.answer_callback_query(callback_query.id, text='User has been removed due to majority vote.')
            del votes[user_id]
            del ban_counts[user_id]
        except Exception as e:
            await bot.answer_callback_query(callback_query.id, text='An error occurred while trying to remove the user.')
    else:
        await bot.answer_callback_query(callback_query.id, text=f'Vote registered. Current vote count for this user: {ban_counts[user_id]}')

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('unban_'))
async def process_callback_unban(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    voter_id = callback_query.from_user.id

    if votes[user_id][voter_id] == 1:
        votes[user_id][voter_id] = 0
        ban_counts[user_id] -= 1

    await bot.answer_callback_query(callback_query.id, text=f'Unban vote registered. Current vote count for this user: {ban_counts[user_id]}')

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
