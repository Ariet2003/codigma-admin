import psycopg2
from config import DB_CONFIG
import os
from psycopg2.extras import RealDictCursor

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


def get_all_tasks():
    """
    Получает все задачи (Problem) из БД, возвращает список словарей с ключами id и title.
    Здесь выбираются только задачи, которые не скрыты (hidden = false).
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT id, title FROM "Problem" WHERE hidden = false;')
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return tasks


def create_hackathon(hackathon_data):
    """
    Создаёт новый хакатон (Contest) и связывает с выбранными задачами (ContestProblem).

    hackathon_data — словарь с ключами:
      title, description, startTime, endTime, hidden, selected_problem_ids (список id задач)

    Возвращает True в случае успеха или False при ошибке.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Вставка записи в таблицу Contest
        insert_contest_query = """
        INSERT INTO "Contest" (title, description, "startTime", "endTime", hidden)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(insert_contest_query, (
            hackathon_data["title"],
            hackathon_data["description"],
            hackathon_data["startTime"],
            hackathon_data["endTime"],
            hackathon_data["hidden"]
        ))
        contest_id = cur.fetchone()[0]

        # Вставка записей в таблицу ContestProblem для каждой выбранной задачи
        for index, problem_id in enumerate(hackathon_data["selected_problem_ids"]):
            insert_contest_problem_query = """
            INSERT INTO "ContestProblem" (contestId, problemId, index)
            VALUES (%s, %s, %s);
            """
            cur.execute(insert_contest_problem_query, (contest_id, problem_id, index))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("Ошибка при создании хакатона:", e)
        return False
