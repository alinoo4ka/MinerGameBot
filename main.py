import asyncio
import logging
import random
import re
import sqlite3

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database
import admin_panel
from commands import level
from commands import breadwinner
from commands import plasma_chance
from commands import mban

BOT_TOKEN = "8031609683:AAGbcmlTkh96TWSRqLZwx-xnIj2P_QUT10M"  # Replace with your bot token
ADMIN_ID = 7765885209

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

texts = [
    "Текст 0: Первый текст",
    "Текст 1: Второй текст",
    "Текст 2: Третий текст",
]

blocking_user_id = None
unblocking_user_id = None

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await process_start_command(message)

@dp.message(Command("mban"))
async def mban_command_handler(message: types.Message):
    await mban.process_mban_command(message)
    
@dp.message(Command("munban"))
async def munban_command_handler(message: types.Message):
    await mban.process_munban_command(message)
    
@dp.message(Command("mmute"))
async def mkick_command_handler(message: types.Message):
    await mban.process_mute_command(message)    
        
@dp.message(Command("admin"))
async def admin_command_handler(message: types.Message):
    await admin_panel.admin_panel(message)

@dp.message(Command("lvl"))
async def level_command_handler(message: types.Message):
    await level.process_level_command(message)

@dp.message(F.text.lower().startswith("ур"))
async def level_command_handler(message: types.Message):
    await level.process_level_command(message)

@dp.message(F.text.lower().startswith("уровень"))
async def level_command_handler(message: types.Message):
    await level.process_level_command(message)

@dp.message(F.text.lower().startswith("коп"))
async def dig_command_handler(message: types.Message):
    await breadwinner.dig_handler(message)

@dp.message(F.text.lower().startswith("копать"))
async def dig_command_handler(message: types.Message):
    await breadwinner.dig_handler(message)

@dp.message(F.text.lower().startswith("продать всё"))
async def sell_all_command_handler(message: types.Message):
    await breadwinner.sell_all_handler(message)

@dp.message(Command("balance"))
async def balance_command_handler(message: types.Message):
    await show_balance(message)

@dp.message(F.text.lower().startswith("б"))
async def balance_command_handler(message: types.Message):
    await show_balance(message)

@dp.message(Command("chance"))
async def chance_command_handler(message: types.Message):
    await plasma_chance.show_chance_level(message)

@dp.message(F.text.lower().startswith("шп"))
async def chance_command_handler(message: types.Message):
    await plasma_chance.show_chance_level(message)

@dp.message(F.text.lower().startswith("шанс плазмы"))
async def chance_command_handler(message: types.Message):
    await plasma_chance.show_chance_level(message)

@dp.message(F.text.lower().startswith("сменить ник"))
async def change_nickname_handler(message: types.Message):
    await process_change_nickname(message)

@dp.message(F.text.lower().startswith("перевести"))
async def transfer_command_handler(message: types.Message):
    if not message.reply_to_message:
        await message.reply("🚫 <b>Эту команду нужно использовать в ответ на сообщение пользователя, которому вы хотите перевести монеты</b>", parse_mode=ParseMode.HTML)
        return

    sender_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        await message.reply("🚫 <b>Нельзя перевести деньги самому себе</b>", parse_mode=ParseMode.HTML)
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("🚫 <b>Неверный формат команды</b>\n<b>Используйте:</b> <code>перевести {количество}</code>", parse_mode=ParseMode.HTML)
            return
        amount = int(parts[1])

        if amount <= 0:
            await message.reply("🚫 <b>Сумма перевода должна быть положительным числом</b>", parse_mode=ParseMode.HTML)
            return
    except ValueError:
        await message.reply("🚫 <b>Неверный формат суммы перевода, укажите целое число</b>", parse_mode=ParseMode.HTML)
        return

    conn = sqlite3.connect(database.DATABASE_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT money FROM users WHERE user_id = ?", (sender_id,))
        result = cursor.fetchone()

        if not result:
            await message.reply("🚫 <b>Отправитель не найден</b>", parse_mode=ParseMode.HTML)
            return

        sender_balance = result[0]

        if sender_balance < amount:            
            await message.reply("🚫 <b>Недостаточно средств на балансе</b>", parse_mode=ParseMode.HTML)
            return

        cursor.execute("UPDATE users SET money = money - ? WHERE user_id = ?", (amount, sender_id))
        cursor.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (amount, receiver_id))

        conn.commit()

        await message.reply(f"💸 <b>Вы успешно перевели <code>{amount}</code> монет пользователю <code>{message.reply_to_message.from_user.first_name}</code></b>", parse_mode=ParseMode.HTML)

        try:
            await bot.send_message(receiver_id, f"💸 <b>Пользователь <code>{message.from_user.first_name}</code> перевел вам <code>{amount}</code> монет</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(f"Не удалось отправить уведомление получателю: {e}")
            await message.reply("🚫 <b>Ошибка, если ты:</b>\n<b>перевел деньги челу, который не написал <code>/start</code> в бота</b>\n<b>перевел деньги боту/каналу</b>\n<b>еще как-то хотел обмануть перевод денег, то знай: я списал у тебя сумму перевода с баланса, если ты правда переводил деньги пользователю, который не нажал старт в боте, если ты правда переводил деньги пользователю, который не нажал старт в боте, то при регистрации деньги уже будут у него на балансе.</b>", parse_mode=ParseMode.HTML)
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Ошибка при выполнении перевода: {e}")
        await message.reply("🚫 <b>Неизвестная ошибка</b>", parse_mode=ParseMode.HTML)

    finally:
        conn.close()
                    
@dp.message(F.text.lower().startswith("баланс"))
async def balance_command_handler(message: types.Message):
    await show_balance(message)

@dp.message(Command("inline"))
async def command_inline_handler(message: types.Message) -> None:
    await process_inline_command(message)

@dp.message()
async def message_handler(message: types.Message):
    await admin_panel.process_admin_message(message, ADMIN_ID)

@dp.callback_query(F.data == "list_users")
async def list_users_callback(query: types.CallbackQuery):
    if query.from_user.id == ADMIN_ID:
        await admin_panel.list_users(query)

@dp.callback_query(F.data == "block_user")
async def block_user_callback(query: types.CallbackQuery):
    global blocking_user_id
    if query.from_user.id == ADMIN_ID:
        blocking_user_id = query.from_user.id
        await admin_panel.block_user_command(query)

@dp.callback_query(F.data == "unblock_user")
async def unblock_user_callback(query: types.CallbackQuery):
    global unblocking_user_id
    if query.from_user.id == ADMIN_ID:
        unblocking_user_id = query.from_user.id
        await admin_panel.unblock_user_command(query)

dp.callback_query.register(admin_panel.give_рудa_command, F.data == "give_рудa")
dp.callback_query.register(admin_panel.give_монеты_command, F.data == "give_монеты")
dp.callback_query.register(admin_panel.give_плазма_command, F.data == "give_плазма")

dp.callback_query.register(level.process_upgrade_callback, F.data == "upgrade_level")
dp.callback_query.register(plasma_chance.process_upgrade_callback, F.data == "upgrade_chance")

async def show_balance(message: types.Message):
    user_id = message.from_user.id
    nickname = database.get_user_nickname(user_id)

    if not nickname:
        await message.answer("Пользователь не найден. Пожалуйста, начните с команды /start.")
        return

    try:
        рудa, plasma, money = database.get_user_resources_for_plasma_upgrade(user_id)
        await message.answer(
            f"{nickname}, Ваш баланс:\n"
            f"Руда: {рудa}\n"
            f"Плазма: {plasma}\n"
            f"Монеты: {money}"
        )
    except Exception as e:
        print(f"Ошибка при получении ресурсов пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при получении вашего баланса. Попробуйте позже.")

async def process_start_command(message: types.Message):
    user = message.from_user
    if user:
        if database.is_user_blocked(user.id):
            await message.answer("Вы заблокированы и не можете использовать этого бота.")
            return

        if database.is_user_registered(user.id):
            nickname = database.get_user_nickname(user.id)
            await message.answer(f"Привет, {nickname}! Я тебя уже знаю.")
        else:
            nickname = database.register_new_user(user.id, user.username, user.first_name, user.last_name)
            if nickname:
                logging.info(f"Добавлен новый пользователь: {user.id} с никнеймом {nickname}")
                await message.answer(
                    f"Привет, {nickname}! Я запомнил тебя."
                )
            else:
                await message.answer("Ошибка при регистрации пользователя.")

        random_text1 = random.choice(texts)
        random_text2 = random.choice(texts)
        await message.answer(f"Случайный текст 1:\n{random_text1}")
        await message.answer(f"Случайный текст 2:\n{random_text2}")
    else:
        await message.answer("Не удалось получить информацию о пользователе.")

async def process_inline_command(message: types.Message) -> None:
    user = message.from_user
    if user:
        if database.is_user_blocked(user.id):
            return
        await message.answer(
            texts[0], reply_markup=create_inline_keyboard(0)
        )
    else:
        await message.answer("Не удалось получить информацию о пользователе.")

def create_inline_keyboard(current_index: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if current_index == 2:
        builder.button(text="Текст 1", callback_data="text_1")
    elif current_index == 0:
        builder.button(text="Текст 1", callback_data="text_1")
    elif current_index == 1:
        builder.button(text="Текст 2", callback_data="text_2")
        builder.button(text="Текст 0", callback_data="text_0")

    return builder.as_markup()

async def process_change_nickname(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.reply("Использование: Сменить ник Новый_Ник")
        return

    new_nickname = parts[2]

    # Проверка соответствия требованиям к никнейму
    if not re.match(r'^[а-яА-Яa-zA-Z0-9+_\!\-#]+$', new_nickname):
        await message.reply("Никнейм должен содержать только русские, английские буквы, цифры и символы +_!-# без пробелов.")
        return

    user_id = message.from_user.id
    conn = sqlite3.connect(database.DATABASE_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE users SET nickname = ? WHERE user_id = ?", (new_nickname, user_id))
        conn.commit()
        await message.reply(f"Никнейм успешно изменен на: {new_nickname}")
    except Exception as e:
        logging.error(f"Ошибка при смене никнейма: {e}")
        conn.rollback()
        await message.reply("Произошла ошибка при смене никнейма.")
    finally:
        conn.close()

async def main() -> None:
    database.init_db()

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    