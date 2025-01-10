# recipes_handler.py
import asyncio

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiohttp
from random import choices
from googletrans import Translator


# Определение состояний
class RecipeStates(StatesGroup):
    category_selection = State()
    recipe_selection = State()
    recipe_details = State()


# Функция для создания клавиатуры с категориями
async def get_categories_keyboard():
    url = "https://www.themealdb.com/api/json/v1/1/categories.php"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    categories = [category['strCategory'] for category in data['categories']]

    keyboard = InlineKeyboardMarkup(row_width=2)
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category, callback_data=f"category:{category}"))

    return keyboard

# Обработчик выбора "Далее"
async def next_step_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "next_step":
        await recipe_details_handler(callback_query, state)

# Обработчик команды /category_search_random
async def category_search_random_handler(message: types.Message, state: FSMContext):
    args = message.get_args()
    try:
        recipe_count = int(args)
    except ValueError:
        await message.answer("Пожалуйста, укажите количество рецептов как число. Пример: /category_search_random 3")
        return

    await state.update_data(recipe_count=recipe_count)
    keyboard = await get_categories_keyboard()
    await message.answer("Выберите категорию рецептов:", reply_markup=keyboard)
    await RecipeStates.category_selection.set()


# Обработчик выбора категории
async def category_selected_handler(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.split(":")[1]
    await state.update_data(selected_category=category)

    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    meals = data.get('meals', [])
    user_data = await state.get_data()
    recipe_count = user_data.get('recipe_count', 3)

    selected_meals = choices(meals, k=min(recipe_count, len(meals)))
    recipe_ids = [meal['idMeal'] for meal in selected_meals]
    await state.update_data(recipe_ids=recipe_ids)

    translator = Translator()
    meal_names = [translator.translate(meal['strMeal'], dest='ru').text for meal in selected_meals]

    meal_list = "\n".join(f"• {name}" for name in meal_names)
    await callback_query.message.answer(f"Выбранные рецепты:\n{meal_list}\n\nНажмите 'Далее', чтобы узнать больше.")
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Далее", callback_data="next_step"))
    await callback_query.message.answer("Перейти к деталям рецептов:", reply_markup=keyboard)
    await RecipeStates.recipe_details.set()


# Обработчик вывода деталей рецептов
async def recipe_details_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    recipe_ids = user_data.get('recipe_ids', [])

    if not recipe_ids:
        await callback_query.message.answer("Рецепты для отображения отсутствуют.")
        return

    async with aiohttp.ClientSession() as session:
        tasks = [session.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}") for id in recipe_ids]
        responses = await aiohttp.gather(*tasks)
        recipes = [await response.json() for response in responses]

    translator = Translator()
    for recipe in recipes:
        meal = recipe['meals'][0]
        if meal is None:
            continue

        name = translator.translate(meal['strMeal'], dest='ru').text
        instructions = translator.translate(meal['strInstructions'], dest='ru').text

        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}')
            measure = meal.get(f'strMeasure{i}')
            if ingredient and ingredient.strip():
                ingredients.append(f"{translator.translate(ingredient, dest='ru').text} ({measure})")

        ingredient_list = "\n".join(ingredients)
        await callback_query.message.answer(
            f"**{name}**\n\n**Рецепт:**\n{instructions}\n\n**Ингредиенты:**\n{ingredient_list}",
            parse_mode="Markdown"
        )


# Регистрация обработчиков в основном файле
def register_handlers(dp):
    dp.register_message_handler(category_search_random_handler, commands="category_search_random", state="*")
    dp.register_callback_query_handler(category_selected_handler, lambda call: call.data.startswith("category:"),
                                       state=RecipeStates.category_selection)
    dp.register_callback_query_handler(next_step_handler, lambda call: call.data == "next_step",
                                       state=RecipeStates.recipe_details)


# recipes_handler.py

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiohttp
from random import choices
from googletrans import Translator


# Определение состояний
class RecipeStates(StatesGroup):
    category_selection = State()
    recipe_selection = State()
    recipe_details = State()


# Функция для создания клавиатуры с категориями
async def get_categories_keyboard():
    url = "https://www.themealdb.com/api/json/v1/1/categories.php"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    categories = [category['strCategory'] for category in data['categories']]

    keyboard = InlineKeyboardMarkup(row_width=2)
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category, callback_data=f"category:{category}"))

    return keyboard


# Обработчик команды /category_search_random
async def category_search_random_handler(message: types.Message, state: FSMContext):
    args = message.get_args()
    try:
        recipe_count = int(args)
    except ValueError:
        await message.answer("Пожалуйста, укажите количество рецептов как число. Пример: /category_search_random 3")
        return

    await state.update_data(recipe_count=recipe_count)
    keyboard = await get_categories_keyboard()
    await message.answer("Выберите категорию рецептов:", reply_markup=keyboard)
    await RecipeStates.category_selection.set()


# Обработчик выбора категории
async def category_selected_handler(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.split(":")[1]
    await state.update_data(selected_category=category)

    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    meals = data.get('meals', [])
    user_data = await state.get_data()
    recipe_count = user_data.get('recipe_count', 3)

    selected_meals = choices(meals, k=min(recipe_count, len(meals)))
    recipe_ids = [meal['idMeal'] for meal in selected_meals]
    await state.update_data(recipe_ids=recipe_ids)

    translator = Translator()
    meal_names = [translator.translate(meal['strMeal'], dest='ru').text for meal in selected_meals]

    meal_list = "\n".join(f"• {name}" for name in meal_names)
    await callback_query.message.answer(f"Выбранные рецепты:\n{meal_list}\n\nНажмите 'Далее', чтобы узнать больше.")
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Далее", callback_data="next_step"))
    await callback_query.message.answer("Перейти к деталям рецептов:", reply_markup=keyboard)
    await RecipeStates.recipe_details.set()


# Обработчик вывода деталей рецептов
async def recipe_details_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    recipe_ids = user_data.get('recipe_ids', [])

    async with aiohttp.ClientSession() as session:
        tasks = [session.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}") for id in recipe_ids]
        responses = await asyncio.gather(*tasks)
        recipes = [await response.json() for response in responses]

    translator = Translator()
    for recipe in recipes:
        meal = recipe['meals'][0]
        name = translator.translate(meal['strMeal'], dest='ru').text
        instructions = translator.translate(meal['strInstructions'], dest='ru').text

        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}')
            measure = meal.get(f'strMeasure{i}')
            if ingredient and ingredient.strip():
                ingredients.append(f"{translator.translate(ingredient, dest='ru').text} ({measure})")

        ingredient_list = "\n".join(ingredients)
        await callback_query.message.answer(
            f"**{name}**\n\n**Рецепт:**\n{instructions}\n\n**Ингредиенты:**\n{ingredient_list}",
            parse_mode="Markdown"
        )


# Регистрация обработчиков в основном файле
def register_handlers(dp):
    dp.register_message_handler(category_search_random_handler, commands="category_search_random", state="*")
    dp.register_callback_query_handler(category_selected_handler, lambda call: call.data.startswith("category:"),
                                       state=RecipeStates.category_selection)
    dp.register_callback_query_handler(recipe_details_handler, lambda call: call.data == "next_step",
                                       state=RecipeStates.recipe_details)
