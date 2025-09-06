import aiosqlite

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'

async def get_stats(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем сортированные данные по убыванию
        async with db.execute('SELECT user_id, rating FROM quiz_state ORDER BY rating DESC') as cursor:
            results = await cursor.fetchall()

    if not results:
        return "Статистика пока пуста."

    stats_text = "📊 **Статистика квиза**\n"
    for i, (db_user_id, rating) in enumerate(results):
        if db_user_id == user_id:
            stats_text += f"{i + 1} | Вы: Рейтинг: {rating}\n"
        else:
            stats_text += f"{i + 1} | Игрок: Рейтинг: {rating}\n"

    return stats_text

async def get_quiz_index(user_id: int):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def update_quiz_index(user_id: int, index: int, rating: int):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, rating) VALUES (?, ?, ?)', (user_id, index, rating))
        # Сохраняем изменения
        await db.commit()


async def get_rating(user_id: int):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT rating FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, rating INTEGER)''')
        # Сохраняем изменения
        await db.commit()
