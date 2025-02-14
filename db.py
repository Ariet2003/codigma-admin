# db.py
import psycopg2
from config import DB_CONFIG

def get_connection():
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    return conn

def get_user_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    # Если имена таблицы или полей чувствительны к регистру, используйте кавычки
    query = 'SELECT email, password, role FROM public."User" WHERE email = %s'
    cur.execute(query, (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user
