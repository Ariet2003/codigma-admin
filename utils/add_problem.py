import psycopg2
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def create_problem_files(json_data):
    """
    Функция создает файловую структуру для задачи.
    В базовой директории (problems) создается папка с именем функции,
    далее внутри создаются папки inputs, outputs, boilerplate, boilerplate-full,
    а также файлы Problem.md и Structure.md.
    """
    # Базовая директория (не забудьте, что обратные слэши экранируются или используйте raw-string)
    base_dir = r"C:\Users\ACER\Desktop\DIP\codigma\apps\problems"

    # Имя функции (оно же имя папки задачи)
    function_name = json_data.get("Название функции", "default_function")
    problem_dir = os.path.join(base_dir, function_name)
    os.makedirs(problem_dir, exist_ok=True)

    # Создаем подпапки для тесткейсов: inputs и outputs
    inputs_dir = os.path.join(problem_dir, "inputs")
    outputs_dir = os.path.join(problem_dir, "outputs")
    os.makedirs(inputs_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    # Создаем файлы для тесткейсов
    testcases = json_data.get("Сгенерированные тесткейсы", [])
    for index, tc in enumerate(testcases):
        input_content = tc.get("input", "")
        expected_output = tc.get("expected_output", "")
        # Записываем входные данные (в файле будут именно реальные переводы строк)
        with open(os.path.join(inputs_dir, f"{index}.txt"), "w", encoding="utf-8") as f:
            f.write(input_content)
        # Записываем ожидаемый результат
        with open(os.path.join(outputs_dir, f"{index}.txt"), "w", encoding="utf-8") as f:
            f.write(expected_output)

    # Создаем папку boilerplate и записываем в нее шаблонные коды для каждого языка
    boilerplate_dir = os.path.join(problem_dir, "boilerplate")
    os.makedirs(boilerplate_dir, exist_ok=True)
    lang_file_mapping = {
        "C++": "function.cpp",
        "JavaScript": "function.js",
        "Rust": "function.rs",
        "Java": "function.java"
    }
    template_codes = json_data.get("Шаблонные коды", {})
    for lang, filename in lang_file_mapping.items():
        code = template_codes.get(lang, "")
        with open(os.path.join(boilerplate_dir, filename), "w", encoding="utf-8") as f:
            f.write(code)

    # Создаем папку boilerplate-full и записываем в нее полные шаблонные коды
    boilerplate_full_dir = os.path.join(problem_dir, "boilerplate-full")
    os.makedirs(boilerplate_full_dir, exist_ok=True)
    full_template_codes = json_data.get("Полные шаблонные коды", {})
    for lang, filename in lang_file_mapping.items():
        fullcode = full_template_codes.get(lang, "")
        with open(os.path.join(boilerplate_full_dir, filename), "w", encoding="utf-8") as f:
            f.write(fullcode)

    # Создаем файл Problem.md с условием задачи
    problem_md_path = os.path.join(problem_dir, "Problem.md")
    problem_statement = json_data.get("Условия задачи", "")
    with open(problem_md_path, "w", encoding="utf-8") as f:
        f.write(problem_statement)

    # Создаем файл Structure.md с описанием структуры входных и выходных данных
    structure_md_path = os.path.join(problem_dir, "Structure.md")
    structure_data = json_data.get("Структура входных и выходных данных", {})
    structure_lines = []
    structure_lines.append(f"Problem Name: {json_data.get('Название задачи', '')}")
    structure_lines.append(f"Function Name: {json_data.get('Название функции', '')}")
    structure_lines.append("Input Structure:")
    for inp in structure_data.get("inputs", []):
        # Формат: "Input Field: <тип> <имя>"
        field_type = inp.get("type", "")
        field_name = inp.get("name", "")
        structure_lines.append(f"Input Field: {field_type} {field_name}")
    structure_lines.append("Output Structure:")
    for out in structure_data.get("outputs", []):
        field_type = out.get("type", "")
        field_name = out.get("name", "")
        structure_lines.append(f"Output Field: {field_type} {field_name}")

    with open(structure_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(structure_lines))

    print(f"Файлы задачи созданы в: {problem_dir}")

def save_problem_data(json_data):
    """
    Принимает словарь (JSON) с данными задачи, сохраняет данные в таблицы Problem, TestCase и DefaultCode,
    и возвращает результат операции.

    Структура JSON:
        - "Название задачи": заголовок задачи
        - "Сложность алгоритма": сложность (например, "Easy")
        - "Условия задачи": условие задачи (также используется как markdown-условие)
        - "Название функции": название функции (slug)
        - "Структура входных и выходных данных": дополнительные метаданные (не сохраняются в БД)
        - "Шаблонные коды": словарь с кодами для каждого языка
        - "Полные шаблонные коды": словарь с полными шаблонными кодами для каждого языка
        - "Сгенерированные тесткейсы": список объектов с полями "input" и "expected_output"
    """
    # Параметры подключения к БД
    conn_params = {
        "dbname": os.getenv('DB_NAME'),
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD'),
        "host": os.getenv('DB_HOST'),
        "port": int(os.getenv('DB_PORT'))
    }

    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        now = datetime.now()

        # 1. Сохраняем задачу в таблице Problem
        problem_id = str(uuid.uuid4())
        title = json_data.get("Название задачи", "")
        description = json_data.get("Условия задачи", "")
        slug = json_data.get("Название функции", "")
        difficulty = json_data.get("Сложность алгоритма", "").upper()

        query_problem = """
            INSERT INTO "Problem" 
                (id, title, description, hidden, slug, solved, "createdAt", "updatedAt", difficulty, "problemMarkdown")
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query_problem, (
            problem_id,
            title,
            description,
            False,  # hidden всегда false
            slug,
            0,  # solved всегда 0
            now,
            now,
            difficulty,
            description  # "problemMarkdown" – используем условие задачи
        ))

        # 2. Сохраняем тесткейсы в таблице TestCase
        testcases = json_data.get("Сгенерированные тесткейсы", [])
        # Собираем входы и ожидаемые выходы в виде массивов строк
        inputs = [tc.get("input", "") for tc in testcases]
        outputs = [tc.get("expected_output", "") for tc in testcases]
        testcase_id = str(uuid.uuid4())
        query_testcase = """
            INSERT INTO "TestCase" 
                (id, input, output, "problemId")
            VALUES 
                (%s, %s, %s, %s)
        """
        cur.execute(query_testcase, (
            testcase_id,
            inputs,
            outputs,
            problem_id
        ))

        # 3. Сохраняем шаблонные коды и полные шаблонные коды в таблице DefaultCode
        # Мэппинг языков: JavaScript → 1, C++ → 2, Rust → 3, Java → 4
        lang_mapping = {
            "JavaScript": 1,
            "C++": 2,
            "Rust": 3,
            "Java": 4
        }
        codes = json_data.get("Шаблонные коды", {})
        fullcodes = json_data.get("Полные шаблонные коды", {})

        query_defaultcode = """
            INSERT INTO "DefaultCode" 
                (id, "languageId", "problemId", code, "createdAt", "updatedAt", fullcode)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s)
        """

        # Для каждого языка вставляем отдельную запись
        for lang, code in codes.items():
            if lang not in lang_mapping:
                continue  # если язык не поддерживается, пропускаем
            languageId = lang_mapping[lang]
            fullcode = fullcodes.get(lang, "")
            defaultcode_id = str(uuid.uuid4())
            cur.execute(query_defaultcode, (
                defaultcode_id,
                languageId,
                problem_id,
                code,
                now,
                now,
                fullcode
            ))

        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Сохранено"}

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return {"status": "error", "message": str(e)}


def add_problem(data):
    result = save_problem_data(data)
    if result.get("status") == "success":
        try:
            create_problem_files(data)
            return True
        except Exception as e:
            print(f"Ошибка при создании файлов: {e}")
            return False
    return False
