from datetime import datetime
import psycopg2
from config import DB_CONFIG
import uuid
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
    query = 'SELECT email, password, role FROM public."User" WHERE email = %s'
    cur.execute(query, (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_all_tasks():
    """
    Получает все задачи (Problem) из БД, возвращает список словарей с ключами id и title.
    Выбираются только задачи, которые не скрыты (hidden = false).
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
    Создаёт новый хакатон (Contest) и связывает его с выбранными задачами (ContestProblem).
    Для таблицы Contest требуются поля: id, title, description, startTime, endTime, hidden, updatedAt, leaderboard.
    Для таблицы ContestProblem требуются поля: id, contestId, problemId, index, updatedAt, solved.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        now_dt = datetime.now()

        # Вставка записи в таблицу Contest с указанием обязательных столбцов
        insert_contest_query = """
        INSERT INTO "Contest" (id, title, description, "startTime", "endTime", hidden, "updatedAt", leaderboard)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(insert_contest_query, (
            hackathon_data["id"],
            hackathon_data["title"],
            hackathon_data["description"],
            hackathon_data["startTime"],
            hackathon_data["endTime"],
            hackathon_data["hidden"],
            now_dt,     # updatedAt
            True       # leaderboard (по умолчанию true)
        ))
        contest_id = cur.fetchone()[0]

        # Вставка записей в таблицу ContestProblem для каждой выбранной задачи
        for index, problem_id in enumerate(hackathon_data["selected_problem_ids"]):
            contest_problem_id = str(uuid.uuid4())
            insert_contest_problem_query = """
            INSERT INTO "ContestProblem" (id, "contestId", "problemId", "index", "updatedAt", solved)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cur.execute(insert_contest_problem_query, (
                contest_problem_id,
                contest_id,
                problem_id,
                index,
                now_dt,  # updatedAt для ContestProblem
                0        # solved по умолчанию 0
            ))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("Ошибка при создании хакатона:", e)
        return False
