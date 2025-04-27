
import logging
import time

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

async def is_admin(bot: types.Bot, chat_id: int, user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором чата."""
    try:
        chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return chat_member.status in ("administrator", "creator")
    except TelegramBadRequest as e:
        logging.error(f"Ошибка при получении информации об администраторе: {e}")
        return False

async def process_mban_command(message: types.Message):
    """
    Обработчик команды /mban. Банит пользователя в чате, на которого ответили.
    Доступно только для администратора.
    """

    является_ли_пользователь_админом = await is_admin(message.bot, message.chat.id, message.from_user.id)

    if not является_ли_пользователь_админом:
        await message.reply("🚫 У вас нет прав на выполнение этой команды.", parse_mode=ParseMode.HTML)
        return

    if not message.reply_to_message:
        await message.reply("🚫 Эту команду нужно использовать в ответ на сообщение пользователя, которого вы хотите забанить.", parse_mode=ParseMode.HTML)
        return

    id_пользователя_для_бана = message.reply_to_message.from_user.id
    имя_пользователя_для_бана = message.reply_to_message.from_user.username
    имя_пользователя_для_бана_отображаемое = message.reply_to_message.from_user.first_name

    # Проверяем, является ли цель тоже админом
    является_ли_цель_админом = await is_admin(message.bot, message.chat.id, id_пользователя_для_бана)
    if является_ли_цель_админом:
        await message.reply("🚫 Нельзя забанить администратора.", parse_mode=ParseMode.HTML)
        return

    try:
        bot = message.bot
        await bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=id_пользователя_для_бана
        )

        await message.reply(f"✅ Пользователь {имя_пользователя_для_бана_отображаемое} (@{имя_пользователя_для_бана}, ID: {id_пользователя_для_бана}) был успешно забанен в этом чате.",
                            parse_mode=ParseMode.HTML)

    except TelegramBadRequest as e:
        logging.error(f"Ошибка при бане пользователя в чате: {e}")
        await message.reply("🚫 Произошла ошибка при бане пользователя в чате. Возможно, у бота недостаточно прав.",
                            parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при бане пользователя: {e}")
        await message.reply("🚫 Произошла неизвестная ошибка при бане пользователя.", parse_mode=ParseMode.HTML)


async def process_munban_command(message: types.Message):
    """
    Обработчик команды /munban. Снимает бан пользователя в чате, на которого ответили.
    Доступно только для администратора.
    """

    является_ли_пользователь_админом = await is_admin(message.bot, message.chat.id, message.from_user.id)

    if not является_ли_пользователь_админом:
        await message.reply("🚫 <b>У вас нет прав на выполнение этой команды</b>", parse_mode=ParseMode.HTML)
        return

    if not message.reply_to_message:
        await message.reply("🚫 <b>Эту команду нужно использовать в ответ на сообщение пользователя, которого вы хотите разбанить</b>",
                            parse_mode=ParseMode.HTML)
        return

    id_пользователя_для_разбана = message.reply_to_message.from_user.id
    имя_пользователя_для_разбана = message.reply_to_message.from_user.username
    имя_пользователя_для_разбана_отображаемое = message.reply_to_message.from_user.first_name

    # Проверяем, является ли цель тоже админом
    является_ли_цель_админом = await is_admin(message.bot, message.chat.id, id_пользователя_для_разбана)
    if является_ли_цель_админом:
        await message.reply("🚫 <b>Администратор, который однажды уже был забанен в чате, не имеет права вернуться назад :(</b>",
                            parse_mode=ParseMode.HTML)
        return

    try:
        bot = message.bot
        await bot.unban_chat_member(
            chat_id=message.chat.id,
            user_id=id_пользователя_для_разбана
        )

        await message.reply(
            f"🛡️ <b>Пользователь <code>{имя_пользователя_для_разбана_отображаемое}</code> (<code>@{имя_пользователя_для_разбана}</code>, ID: <code>{id_пользователя_для_разбана}</code>) был успешно разбанен в этом чате</b>",
            parse_mode=ParseMode.HTML)

    except TelegramBadRequest as e:
        logging.error(f"Ошибка при разбане пользователя в чате: {e}")
        await message.reply("🚫 <b>Произошла ошибка при разбане пользователя в чате. Возможно, у бота недостаточно прав</b>",
                            parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при разбане пользователя: {e}")
        await message.reply("🚫 <b>Произошла неизвестная ошибка при разбане пользователя</b>", parse_mode=ParseMode.HTML)


async def process_mmute_command(message: types.Message):
    """
    Обработчик команды /mmute. Мутит пользователя в чате на которого ответили, на указанное количество минут.
    Доступно только для администратора.
    """

    является_ли_пользователь_админом = await is_admin(message.bot, message.chat.id, message.from_user.id)

    if not является_ли_пользователь_админом:
        await message.reply("🚫 <b>У вас нет прав на выполнение этой команды.</b>", parse_mode=ParseMode.HTML)
        return

    if not message.reply_to_message:
        await message.reply("🚫 <b>Эту команду нужно использовать в ответ на сообщение пользователя, которого вы хотите замутить.</b>",
                            parse_mode=ParseMode.HTML)
        return

    id_пользователя_для_мута = message.reply_to_message.from_user.id
    имя_пользователя_для_мута = message.reply_to_message.from_user.username
    имя_пользователя_для_мута_отображаемое = message.reply_to_message.from_user.first_name

    # Проверяем, является ли цель тоже админом
    является_ли_цель_админом = await is_admin(message.bot, message.chat.id, id_пользователя_для_мута)
    if является_ли_цель_админом:
        await message.reply("🚫 <b>Нельзя замутить администратора.</b>", parse_mode=ParseMode.HTML)
        return

    try:
        части = message.text.split()
        if len(части) < 2:
            await message.reply("🚫 <b>Не указано время мута в минутах. Используйте:</b> <code>/mmute [минуты]</code>",
                                parse_mode=ParseMode.HTML)
            return

        try:
            длительность_мута_в_минутах = int(части[1])
            if длительность_мута_в_минутах <= 0:
                await message.reply("🚫 <b>Время мута должно быть положительным числом.</b>", parse_mode=ParseMode.HTML)
                return
        except ValueError:
            await message.reply("🚫 <b>Неверный формат времени мута. Укажите целое число минут.</b>",
                                parse_mode=ParseMode.HTML)
            return

        bot = message.bot
        время_окончания_мута = int(time.time()) + длительность_мута_в_минутах * 60

        разрешения_для_мута = types.ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )

        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=id_пользователя_для_мута,
            permissions=разрешения_для_мута,
            until_date=время_окончания_мута
        )

        await message.reply(
            f"✅ <b>Пользователь <code>{имя_пользователя_для_мута_отображаемое}</code> (<code>@{имя_пользователя_для_мута}</code>, ID: <code>{id_пользователя_для_мута}</code>) был замучен на <code>{длительность_мута_в_минутах}</code> минут.</b>",
            parse_mode=ParseMode.HTML)

    except TelegramBadRequest as e:
        logging.error(f"Ошибка при муте пользователя в чате: {e}")
        await message.reply("🚫 <b>Произошла ошибка при муте пользователя в чате. Возможно, у бота недостаточно прав.</b>",
                            parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при муте пользователя: {e}")
        await message.reply("🚫 <b>Произошла неизвестная ошибка при муте пользователя.</b>", parse_mode=ParseMode.HTML)
