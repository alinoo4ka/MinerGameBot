import random
from aiogram import types, F
from aiogram.filters import Command
from database import get_user_resources, update_user_resources

async def dig_handler(message: types.Message):
    user_id = message.from_user.id
    try:
        рудa, плазма, монеты = get_user_resources(user_id)
    except Exception as e:
        print(f"Ошибка при получении ресурсов пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при получении ваших ресурсов. Попробуйте позже.")
        return

    if random.random() < 0.7:  # 70% шанс
        плазма += 1
        рудa += 1
        await message.answer("Плазма +1!\nРуда +1!")
    else:
        рудa += 1
        await message.answer("Руда +1")

    try:
        update_user_resources(user_id, рудa, плазма, монеты) # Correct order, no keywords
    except Exception as e:
        print(f"Ошибка при обновлении ресурсов пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при обновлении ваших ресурсов. Попробуйте позже.")

async def sell_all_handler(message: types.Message):
    user_id = message.from_user.id
    try:
        рудa, плазма, монеты = get_user_resources(user_id)
    except Exception as e:
        print(f"Ошибка при получении ресурсов пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при получении ваших ресурсов. Попробуйте позже.")
        return
    earned_money = рудa * 10  # Сначала вычисляем заработок
    монеты += earned_money  # Потом добавляем его к монетам
    рудa = 0  # Только потом обнуляем руду
    try:
        update_user_resources(user_id, рудa, плазма, монеты)
        await message.answer(f"Вы продали всю руду и получили {earned_money} монет!\nТеперь у вас {монеты} монет.")
    except Exception as e:
        print(f"Ошибка при обновлении ресурсов пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при продаже руды. Попробуйте позже.")
        return