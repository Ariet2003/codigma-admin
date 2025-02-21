import base64
import requests
import time
from dotenv import load_dotenv
import os
import json

load_dotenv()


def run_judge0_testcases(data):
    """
    Принимает JSON с данными:
    {
        "language_id": int,
        "source_code": str,
        "testcases": [
            {"stdin": str, "expected_output": str},
            ...
        ]
    }
    и возвращает ответ в виде JSON:
    {
        "tests_count": <количество тесткейсов>,
        "status": <1 если все тесткейсы правильны, 0 если хотя бы один неправильный>,
        "compile_output": "Ошибка",
        "tokens": ["токены judge0 для каждого тесткейса"],
        "correct_tests_count": <количество правильных тесткейсов>,
        "incorrect_test_indexes": [<индексы неправильных тесткейсов>]
    }
    """
    testcases = data.get("testcases", [])
    tests_count = len(testcases)
    correct_tests_count = 0
    incorrect_test_indexes = []
    tokens = []

    language_id = data.get("language_id")
    source_code = data.get("source_code")
    # Кодируем исходный код один раз
    encoded_source_code = base64.b64encode(source_code.encode()).decode("utf-8")

    # URL и заголовки для запросов к API Judge0
    url = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&wait=false"
    headers = {
        "content-type": "application/json",
        "x-rapidapi-host": "judge029.p.rapidapi.com",
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY")
    }

    for idx, testcase in enumerate(testcases):
        stdin = testcase.get("stdin", "")
        expected_output = str(testcase.get("expected_output", ""))

        # Кодируем входные данные и ожидаемый вывод в base64
        encoded_stdin = base64.b64encode(stdin.encode()).decode("utf-8")
        encoded_expected_output = base64.b64encode(expected_output.encode()).decode("utf-8")

        payload = {
            "language_id": language_id,
            "source_code": encoded_source_code,
            "stdin": encoded_stdin,
            "expected_output": encoded_expected_output
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 201:
            tokens.append("Ошибка")
            incorrect_test_indexes.append(idx)
            continue

        token = response.json().get("token")
        print(token)
        if not token:
            tokens.append("Ошибка")
            incorrect_test_indexes.append(idx)
            continue

        tokens.append(token)
        result_url = f"https://judge0-ce.p.rapidapi.com/submissions/{token}?base64_encoded=true"

        # Опрос API каждые 5 секунд, пока выполнение не завершится
        while True:
            result_response = requests.get(result_url, headers=headers)
            result_data = result_response.json()
            status_id = result_data["status"]["id"]
            # Статусы 1 и 2 означают, что решение в очереди или обрабатывается
            if status_id in [1, 2]:
                time.sleep(5)
            else:
                break

        # Если статус "Accepted" (id == 3), тест пройден
        if status_id == 3:
            correct_tests_count += 1
        else:
            incorrect_test_indexes.append(idx)

    status = 1 if correct_tests_count == tests_count else 0

    answer = {
        "tests_count": tests_count,
        "status": status,
        "compile_output": "Ошибка",
        "tokens": tokens,
        "correct_tests_count": correct_tests_count,
        "incorrect_test_indexes": incorrect_test_indexes
    }

    return answer
