from aiogram import types, F, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from database import get_plasma_chance_level, update_plasma_chance_level, get_user_resources_for_plasma_upgrade, update_user_resources

BASE_UPGRADE_COST = 25
MAX_CHANCE = 0.75

async def show_chance_level(message: types.Message):
    user_id = message.from_user.id
    chance_level = get_plasma_chance_level(user_id)
    chance_percentage = calculate_plasma_chance(chance_level) * 100
    
    if calculate_plasma_chance(chance_level) >= MAX_CHANCE:
        text = f"🌇 Шанс выпадения плазмы: {chance_percentage:.2f}%\nМаксимальный шанс!"
        keyboard = None
    else:
        upgrade_cost = calculate_upgrade_cost(chance_level)
        text = f"🌇 Шанс выпадения плазмы: {chance_percentage:.2f}%\nДля улучшения надо: {upgrade_cost} монет"
        keyboard = create_upgrade_keyboard(user_id)

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


def create_upgrade_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🌇 Улучшить", callback_data="upgrade_chance")
    return builder.as_markup()

async def process_upgrade_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    рудa, плазма, монеты = get_user_resources_for_plasma_upgrade(user_id)
    current_level = get_plasma_chance_level(user_id)
    upgrade_cost = calculate_upgrade_cost(current_level)

    try:
        if монеты >= upgrade_cost:
            new_монеты = монеты - upgrade_cost
            new_level = current_level + 1
            update_plasma_chance_level(user_id, new_level)
            update_user_resources(user_id, рудa, плазма, new_монеты)
            chance_percentage = calculate_plasma_chance(new_level) * 100            
            if calculate_plasma_chance(new_level) >= MAX_CHANCE:
                text = f"🌇 Шанс выпадения плазмы: {chance_percentage:.2f}%\nМаксимальный шанс!"
                keyboard = None
            else:
                next_upgrade_cost = calculate_upgrade_cost(new_level)
                text = f"🌇 Шанс выпадения плазмы: {chance_percentage:.2f}%\nДля улучшения надо: {next_upgrade_cost} монет"
                keyboard = create_upgrade_keyboard(user_id)

            await query.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            await query.answer("Уровень улучшен!", parse_mode=ParseMode.HTML)
        else:
            await query.answer("Недостаточно монет для улучшения!", parse_mode=ParseMode.HTML)

    except Exception as e:
        await query.answer("Произошла ошибка. Пожалуйста, попробуйте позже.", parse_mode=ParseMode.HTML)
        print(f"Ошибка в process_upgrade_callback: {e}")

def calculate_plasma_chance(level: int) -> float:
    """Рассчитывает шанс выпадения плазмы на основе уровня прокачки."""
    base_chance = 0.05  
    increased_chance = level * 0.05  
    plasma_chance = min(base_chance + increased_chance, MAX_CHANCE)  
    return plasma_chance
    
def calculate_upgrade_cost(level: int) -> int:
    """Рассчитывает стоимость улучшения на основе уровня."""
    return BASE_UPGRADE_COST + (level * BASE_UPGRADE_COST)

def register_handlers(dp: Dispatcher):
    dp.callback_query.register(process_upgrade_callback, F.data == "upgrade_chance")