from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_user_level, get_user_resources, update_user_level, update_user_resources

# Define the resource requirements for each level
LEVEL_REQUIREMENTS = {
    1: {"plasma": 10, "money": 50},
    2: {"plasma": 20, "money": 100},
    3: {"plasma": 30, "money": 150},
    4: {"plasma": 40, "money": 200},
    5: {"plasma": 50, "money": 250},
}

async def process_level_command(message: types.Message):
    user_id = message.from_user.id
    current_level = get_user_level(user_id)
    рудa, plasma, money = get_user_resources(user_id) # Get 3 values now

    # Determine the requirements for the next level
    next_level = current_level + 1
    if next_level in LEVEL_REQUIREMENTS:
        required_plasma = LEVEL_REQUIREMENTS[next_level]["plasma"]
        required_money = LEVEL_REQUIREMENTS[next_level]["money"]

        # Create the "Upgrade" button if the user has enough resources
        builder = InlineKeyboardBuilder()
        if plasma >= required_plasma and money >= required_money:
            builder.button(text="Улучшить", callback_data="upgrade_level")
            await message.answer(
                f"Твой уровень: {current_level}\n"
                f"Для повышения уровня надо:\n"
                f"{required_plasma} плазмы\n"
                f"{required_money} денег",
                reply_markup=builder.as_markup()
            )
        else:
            await message.answer(
                f"Твой уровень: {current_level}\n"
                f"Для повышения уровня надо:\n"
                f"{required_plasma} плазмы\n"
                f"{required_money} денег\n\n"
                "Недостаточно ресурсов для повышения уровня."
            )
    else:
        await message.answer(f"Твой уровень: {current_level}\nУровень максимальный.")

async def process_upgrade_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    current_level = get_user_level(user_id)
    рудa, plasma, money = get_user_resources(user_id) # Get 3 values now

    next_level = current_level + 1
    if next_level in LEVEL_REQUIREMENTS:
        required_plasma = LEVEL_REQUIREMENTS[next_level]["plasma"]
        required_money = LEVEL_REQUIREMENTS[next_level]["money"]

        if plasma >= required_plasma and money >= required_money:
            update_user_level(user_id)
            update_user_resources(user_id, рудa=рудa, plasma=plasma, money=money) # Pass all 3 values
            await query.answer("Уровень повышен!")
            await query.message.edit_text(f"Твой уровень повышен до {next_level}!")
        else:
            await query.answer("Недостаточно ресурсов для повышения уровня.")
    else:
        await query.answer("Уровень максимальный.")