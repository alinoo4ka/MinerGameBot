import sqlite3

DATABASE_FILE = 'users.db'

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            nickname TEXT, 
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level INTEGER DEFAULT 1,
            plasma INTEGER DEFAULT 0,
            money INTEGER DEFAULT 0,
            рудa INTEGER DEFAULT 0,  -- Добавлено поле для руды
            plasma_chance_level INTEGER DEFAULT 1 -- Добавлено поле для уровня шанса плазмы
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_users (
            user_id INTEGER PRIMARY KEY
        )
    ''')

    conn.commit()
    conn.close()

def get_plasma_chance_level(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT plasma_chance_level FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return 1 

def update_plasma_chance_level(user_id, level):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET plasma_chance_level = ? WHERE user_id = ?", (level, user_id))
    conn.commit()
    conn.close()

def is_user_registered(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()
    conn.close()
    return bool(existing_user)

def register_new_user(user_id, username=None, first_name=None, last_name=None):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    nickname = f"Игрок_{user_id}" #Генерируем никнейм
    try:
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, nickname)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, nickname))
        conn.commit()
        print(f"Пользователь {user_id} успешно зарегистрирован.")
        return nickname  # Возвращаем никнейм
    except Exception as e:
        print(f"Ошибка регистрации пользователя {user_id}: {e}")
        return None
    finally:
        conn.close()

def get_user_resources_for_plasma_upgrade(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT plasma, money, рудa FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        рудa, plasma, money = result[2], result[0], result[1]
        return int(рудa), int(plasma), int(money)
    return 0, 0, 0

def block_user(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO blocked_users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        print(f"Пользователь {user_id} заблокирован.")
    except Exception as e:
        print(f"Ошибка блокировки пользователя {user_id}: {e}")
    finally:
        conn.close()

def unblock_user(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM blocked_users WHERE user_id=?", (user_id,))
        conn.commit()
        print(f"Пользователь {user_id} разблокирован.")
    except Exception as e:
        print(f"Ошибка разблокировки пользователя {user_id}: {e}")
    finally:
        conn.close()

def is_user_blocked(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM blocked_users WHERE user_id=?", (user_id,))
    blocked_user = cursor.fetchone()
    conn.close()
    return bool(blocked_user)

def get_all_users():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name, nickname FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_level(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return 1  

def get_user_resources(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT plasma, money, рудa FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        plasma, money, рудa = result
        return {'рудa': рудa, 'plasma': plasma, 'money': money}
    return {'рудa': 0, 'plasma': 0, 'money': 0}

def update_user_level(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET level = level + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def update_user_resources(user_id, рудa, plasma, money):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET plasma = ?, money = ?, рудa = ? WHERE user_id = ?", (plasma, money, рудa, user_id))
    conn.commit()
    conn.close()
    
def get_user_nickname(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nickname FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None