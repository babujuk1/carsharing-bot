import sqlite3
import time


conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_messages (
        user_id INTEGER PRIMARY KEY,
        last_message_time REAL
    )
''')
conn.commit()


async def check_rate_limit(user_id):
    cursor.execute("SELECT last_message_time FROM user_messages WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        last_message_time = result[0]
        time_limit = 20  
        if time.time() - last_message_time < time_limit:
            return int(time_limit - (time.time() - last_message_time))
    return 0


async def update_last_message_time(user_id):
    cursor.execute("INSERT OR REPLACE INTO user_messages (user_id, last_message_time) VALUES (?, ?)", (user_id, time.time()))
    conn.commit()
    
async def close_connection():
    conn.close()