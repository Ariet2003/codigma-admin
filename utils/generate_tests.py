import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()


def generate_tests(task_name: str, metadata: dict, solution_code: str, test_count: int) -> str:
    """
    Генерирует тестовые случаи для задачи с помощью ChatGPT.

    Параметры:
        task_name (str): Название задачи.
        metadata (dict): Метаданные задачи.
        solution_code (str): Исходный код одного из вариантов решения.
        test_count (int): Количество тестов для генерации.

    Возвращает:
        str: Сгенерированные тесты в формате строки (желательно JSON).
    """
    # Формируем сообщение для ChatGPT
    prompt = f"""
        Ты являешься экспертом в генерации тестовых случаев для задач по программированию.

        Название задачи: {task_name}

        Метаданные задачи:
        {json.dumps(metadata, ensure_ascii=False, indent=4)}

        Исходный код решения:
        {solution_code}

        Пожалуйста, сгенерируй {test_count} тестовых случаев для этой задачи.
        Для каждого тестового случая укажи входные данные и ожидаемый результат.
        Верни тесты в формате JSON-массива, где каждый тест — это объект с полями "input" и "expected_output".
        Учитывай разнообразные сценарии, включая крайние случаи.
    """

    # Получаем API-ключ из переменных окружения
    api_key = os.getenv("OPENAI_API_KEY")

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "Ты — эксперт в создании тестовых случаев для задач по программированию."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700,
        )

        tests = response.choices[0].message.content.strip()
        return tests

    except Exception as e:
        return f"Ошибка при генерации тестов: {str(e)}"