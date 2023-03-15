import logging
import time

from aiogram import executor, types
from aiogram.dispatcher.filters import AdminFilter, IsReplyFilter

from config import adminId
from random import randint
from misc import bot, dp


# Send admin message about bot started
async def send_adm(*args, **kwargs):
    await bot.send_message(chat_id=adminId, text='Bot started!')


# info tour
@dp.message_handler(commands=['start'])
async def welcome_send_info(message: types.Message):
    await message.answer(f"{message.from_user.full_name}, привет!\n\n"
                         f"Это бот модератор, для использования добавьте бота в ваш чат со стандартными разрешениями"
                         f" админа, иначе бот не сможет функционировать\n\n"
                         f"Команды для администраторов:\n\n"
                         f" <code>!ban</code> (reason)- бан пользователя и удаление его из чата\n"
                         f" <code>!mute10m</code> (30m, 1h, 6h, 1d)- запретить "
                         f"пользователю отправлять сообщение в чат в указанное время (минуты, часы, дни)\n"
                         f"<code>!unmute</code> - разрешить отправку сообщений\n"
                         f"<code>!del</code> - удалить сообщение\n"
                         f"<code>!pin</code> - закрепить сообщение\n"
                         f"<code>!unpin</code> - открепить сообщение\n"
                         f"<code>!unpin_all</code> - открепить все сообщения в чате\n\n"
                         f"❗Все команды кроме последней, нужно отправлять ответом на сообщение пользователя!\n\n"
                         f"Бота сделал @mr_storm")


# new chat member
@dp.message_handler(content_types=["new_chat_members"])
async def new_chat_member(message: types.Message):
    chat_id = message.chat.id
    await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    await bot.send_message(chat_id=chat_id, text=f"[{message.new_chat_members[0].full_name}]"
                                                 f"(tg://user?id={message.new_chat_members[0].id})"
                                                 f"🍞🧂, welcome to the group!", parse_mode=types.ParseMode.MARKDOWN)


# delete message user leave chat
@dp.message_handler(content_types=["left_chat_member"])
async def leave_chat(message: types.Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# user get info about him
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['me'])
async def welcome(message: types.Message):
    if message.from_user.username is None:
        await message.reply(f"Name - {message.from_user.full_name}\nID - {message.from_user.id}\n")
    else:
        await message.reply(f"Name - {message.from_user.full_name}\n"
                            f"ID - <code>{message.from_user.id}</code>\n"
                            f"Username - @{message.from_user.username}\n")


# ban user
@dp.message_handler(AdminFilter(is_chat_admin=True), IsReplyFilter(is_reply=True), commands=['ban'],
                    commands_prefix='!', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def ban(message: types.Message):
    replied_user = message.reply_to_message.from_user.id
    admin_id = message.from_user.id
    await bot.kick_chat_member(chat_id=message.chat.id, user_id=replied_user)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(chat_id=message.chat.id, text=f"[{message.reply_to_message.from_user.full_name}]"
                                                         f"(tg://user?id={replied_user})"
                                                         f" был забанен админом [{message.from_user.full_name}]"
                                                         f"(tg://user?id={admin_id})",
                           parse_mode=types.ParseMode.MARKDOWN)


# mute user in chat
@dp.message_handler(AdminFilter(is_chat_admin=True), IsReplyFilter(is_reply=True), commands=['mute'],
                    commands_prefix='!', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def mute(message: types.Message):
    args = message.text.split()

    if len(args) > 1:
        till_date = message.text.split()[1]
    else:
        till_date = "15m"

    if till_date[-1] == "m":
        ban_for = int(till_date[:-1]) * 60
    elif till_date[-1] == "h":
        ban_for = int(till_date[:-1]) * 3600
    elif till_date[-1] == "d":
        ban_for = int(till_date[:-1]) * 86400
    else:
        ban_for = 15 * 60

    replied_user = message.reply_to_message.from_user.id
    now_time = int(time.time())
    await bot.restrict_chat_member(chat_id=message.chat.id, user_id=replied_user,
                                   permissions=types.ChatPermissions(can_send_messages=True,
                                                                     can_send_media_messages=True,
                                                                     can_send_other_messages=True),
                                   until_date=now_time + ban_for)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(text=f"[{message.reply_to_message.from_user.full_name}](tg://user?id={replied_user})"
                                f" muted for {till_date}",
                           chat_id=message.chat.id, parse_mode=types.ParseMode.MARKDOWN)


# random mute chat member
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['dont_click_me'])
async def mute_random(message: types.Message):
    now_time = int(time.time())
    replied_user_id = message.from_user.id
    replied_user = message.from_user.full_name
    random_m = randint(1, 10)
    await bot.restrict_chat_member(chat_id=message.chat.id, user_id=replied_user_id,
                                   permissions=types.ChatPermissions(can_send_messages=False,
                                                                     can_send_media_messages=False,
                                                                     can_send_other_messages=False),
                                   until_date=now_time + 60 * random_m)
    await bot.send_message(text=f"[{replied_user}](tg://user?id={replied_user_id})"
                                f" выиграл(а) мут на {random_m} минут(ы)",
                           chat_id=message.chat.id, parse_mode=types.ParseMode.MARKDOWN)


# un_mute user in chat
@dp.message_handler(AdminFilter(is_chat_admin=True), IsReplyFilter(is_reply=True), commands_prefix='!',
                    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['unmute'])
async def un_mute_user(message: types.Message):
    replied_user = message.reply_to_message.from_user.id
    await bot.restrict_chat_member(chat_id=message.chat.id, user_id=replied_user,
                                   permissions=types.ChatPermissions(can_send_messages=True,
                                                                     can_send_media_messages=True,
                                                                     can_send_other_messages=True),)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(text=f"[{message.reply_to_message.from_user.full_name}](tg://user?id={replied_user})"
                                f" можешь теперь писать в чат )",
                           chat_id=message.chat.id, parse_mode=types.ParseMode.MARKDOWN)


# pin chat message
@dp.message_handler(AdminFilter(is_chat_admin=True), IsReplyFilter(is_reply=True),
                    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['pin'], commands_prefix='!')
async def pin_message(message: types.Message):
    msg_id = message.reply_to_message.message_id
    await bot.pin_chat_message(message_id=msg_id, chat_id=message.chat.id)


# unpin chat message
@dp.message_handler(AdminFilter(is_chat_admin=True), IsReplyFilter(is_reply=True), commands_prefix='!',
                    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['unpin'])
async def unpin_message(message: types.Message):
    msg_id = message.reply_to_message.message_id
    await bot.unpin_chat_message(message_id=msg_id, chat_id=message.chat.id)


# unpin all pins
@dp.message_handler(AdminFilter(is_chat_admin=True), IsReplyFilter(is_reply=True), commands_prefix='!',
                    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['unpin_all'])
async def unpin_all_messages(message: types.Message):
    await bot.unpin_all_chat_messages(chat_id=message.chat.id)


# delete user message
@dp.message_handler(AdminFilter(is_chat_admin=True), IsReplyFilter(is_reply=True), commands_prefix='!',
                    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['del'])
async def delete_message(message: types.Message):
    msg_id = message.reply_to_message.message_id
    await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# get chat admins list
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['admins'],
                    commands_prefix='!/')
async def get_admin_list(message: types.Message):
    admins = await message.chat.get_administrators()
    msg = str("Админы :\n")
    
    for admin in admins:
        msg += f"<a href=tg://user?id={admin.user.id}>{admin.user.full_name}</a>"
        
    await message.reply(msg, parse_mode=types.ParseMode.MARKDOWN)


# report about spam or something else
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['report'])
async def report_by_user(message: types.Message):
    msg_id = message.reply_to_message.message_id
    user_id = message.from_user.id
    admins_list = await message.chat.get_administrators()

    for admin in admins_list:
        try:
            await bot.send_message(text=f"User: [{message.from_user.full_name}](tg://user?id={user_id})\n"
                                        f"Reported about next message:\n"
                                        f"[Возможное нарушение](t.me/{message.chat.username}/{msg_id})",
                                   chat_id=admin.user.id, parse_mode=types.ParseMode.MARKDOWN,
                                   disable_web_page_preview=True)
        except Exception as e:
            logging.debug(f"\nCan't send report message to {admin.user.id}\nError - {e}")

    await message.reply("I reported it to chat admins, thank you!")


# # delete links and tags from users, allow for admins
@dp.message_handler(AdminFilter(is_chat_admin=False), content_types=['text'])
async def delete_links(message: types.Message):
    for entity in message.entities:
        if entity.type in ["url", "text_link", "mention"]:
            await bot.delete_message(message.chat.id, message.message_id)


# Polling
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=send_adm, skip_updates=True)
