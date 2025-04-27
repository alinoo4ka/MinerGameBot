from aiogram.enums import ParseMode
from aiogram import types, F, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import block_user, unblock_user, get_all_users, update_user_resources, get_user_resources_for_plasma_upgrade
import io
import logging

ADMIN_ID = 7765885209
RESOURCE_REQUEST = {}  
get_user_resources = get_user_resources_for_plasma_upgrade

def admin_panel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Список", callback_data="list_users")
    builder.button(text="🚫 Бан", callback_data="block_user")
    builder.button(text="🛡️ Разбан", callback_data="unblock_user")
    builder.button(text="🪨", callback_data="give_рудa")
    builder.button(text="🪙", callback_data="give_монеты")
    builder.button(text="🌆", callback_data="give_плазма")
    builder.adjust(1, 2, 3)
    return builder.as_markup()


blocking_user_id = None
unblocking_user_id = None


async def admin_panel(message: types.Message):
    await message.answer("🎛 <b>Админ-панель</b>", reply_markup=admin_panel_keyboard(), parse_mode=ParseMode.HTML)

async def list_users(query: types.CallbackQuery):
    users = get_all_users()
    if users:
        user_list = "\n".join(
            f"{i + 1}. {user[2]} @{user[1] or 'Н/Д'} {user[0]}"
            for i, user in enumerate(users)
        )

        file = io.StringIO(user_list)
        file.name = "user_list.txt"

        await query.message.answer_document(
            document=types.BufferedInputFile(
                file.getvalue().encode(), filename="user_list.txt"
            ),
            caption="<b>Список пользователей:</b>", parse_mode=ParseMode.HTML
        )
        await query.answer()
    else:
        await query.message.edit_text("❓ <b>Пока нет зарегистрированных пользователей.</b>", parse_mode=ParseMode.HTML)
        await query.answer()

async def block_user_command(query: types.CallbackQuery):
    global blocking_user_id
    blocking_user_id = query.from_user.id
    await query.message.answer(
        "🚫 <b>Введите User ID пользователя, которого нужно заблокировать:</b>", parse_mode=ParseMode.HTML
    )
    await query.answer()


async def process_block_user(message: types.Message):
    global blocking_user_id
    try:
        user_id_to_block = int(message.text)
        block_user(user_id_to_block)
        await message.answer(
            f"🚫 <b>Пользователь <code>{user_id_to_block}</code> был заблокирован</b>",
            parse_mode=ParseMode.HTML
        )
        blocking_user_id = None
    except ValueError:
        await message.answer(
            "📛 <b>Неверный User ID. Пожалуйста, введите число</b>",
            parse_mode=ParseMode.HTML
        )

async def unblock_user_command(query: types.CallbackQuery):
    global unblocking_user_id
    unblocking_user_id = query.from_user.id
    await query.message.answer(
        "🛡️ <b>Введите User ID пользователя, которого нужно разблокировать:</b>", parse_mode=ParseMode.HTML
    )
    await query.answer()

async def process_unblock_user(message: types.Message):
    global unblocking_user_id
    try:
        user_id_to_unblock = int(message.text)
        unblock_user(user_id_to_unblock)
        await message.answer(
            f"🛡️ <b>Пользователь <code>{user_id_to_unblock}</code> был разблокирован</b>",
            parse_mode=ParseMode.HTML
        )
        unblocking_user_id = None
    except ValueError:
        await message.answer(
            "📛 <b>Неверный User ID. Пожалуйста, введите число</b>",
            parse_mode=ParseMode.HTML
        )

async def process_admin_commands(message: types.Message, admin_id: int):
    if message.text == "/admin" and message.from_user.id == admin_id:
        await admin_panel(message)
        return True
    return False

async def give_resource_command(query: types.CallbackQuery, resource: str):
    """Generic handler for giving resources."""
    RESOURCE_REQUEST[query.from_user.id] = resource
    await query.message.answer(
        f"<b>Введите User ID и количество {resource}, которое нужно выдать (в формате 'ID количество'):</b>",
        parse_mode=ParseMode.HTML
    )
    await query.answer()

async def process_give_resource(message: types.Message, resource: str):
    """Generic processor for giving resources."""
    if message.from_user.id in RESOURCE_REQUEST and RESOURCE_REQUEST[message.from_user.id] == resource:
        try:
            user_id, amount = map(int, message.text.split())
            рудa, плазма, монеты = get_user_resources(user_id)
            if resource == "рудa":
                рудa += amount
            elif resource == "монеты":
                монеты += amount
            elif resource == "плазма":
                плазма += amount
            else:
                await message.answer("📛 <b>Неизвестный тип ресурса</b>", parse_mode=ParseMode.HTML)
                return

            update_user_resources(user_id, рудa, плазма, монеты)
            await message.answer(
                f"✨ <b>Пользователю <code>{user_id}</code> выдано <code>{amount}</code> {resource}</b>",
                parse_mode=ParseMode.HTML
            )
        except ValueError:
            await message.answer(
                "🚫 <b>Неверный формат ввода. Введите User ID и количество через пробел (например, <code>12345 10</code>).</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.error(f"Ошибка при выдаче ресурса: {e}")
            await message.answer(
                "❌ <b>Произошла ошибка при выдаче ресурса. Пожалуйста, попробуйте позже.</b>",
                parse_mode=ParseMode.HTML
            )
        finally:
            del RESOURCE_REQUEST[message.from_user.id]                

async def give_рудa_command(query: types.CallbackQuery):
    await give_resource_command(query, "рудa")

async def give_монеты_command(query: types.CallbackQuery):
    await give_resource_command(query, "монеты")

async def give_плазма_command(query: types.CallbackQuery):
    await give_resource_command(query, "плазма")
    
async def process_admin_callback(query: types.CallbackQuery, admin_id: int):
    if query.from_user.id == admin_id:
        if query.data == "list_users":
            await list_users(query)
            return True
        elif query.data == "block_user":
            await block_user_command(query)
            return True
        elif query.data == "unblock_user":
            await unblock_user_command(query)
            return True

    return False


async def process_admin_message(message: types.Message, admin_id: int):
    global blocking_user_id, unblocking_user_id

    if message.from_user.id == blocking_user_id:
        await process_block_user(message)
        return

    if message.from_user.id == unblocking_user_id:
        await process_unblock_user(message)
        return

    # Process giving resources
    if message.from_user.id in RESOURCE_REQUEST:
        resource = RESOURCE_REQUEST[message.from_user.id]
        await process_give_resource(message, resource)
        return

    if await process_admin_commands(message, admin_id):
        return
        