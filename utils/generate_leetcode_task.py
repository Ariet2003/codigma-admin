import openai
import os

def generate_leetcode_task(prompt_text: str) -> str:
    """
    Функция принимает текст и запрашивает у ChatGPT генерацию условия задачи в формате Markdown.
    """
    system_prompt = (
        "Ты помощник по программированию. Твоя задача - создавать условия задач в стиле LeetCode. "
        "Формат вывода должен быть строго следующим:\n\n"
        "## Название задачи\n\n"
        "### Условие\n"
        "Описание задачи по заданной теме.\n\n"
        "### Пример 1:\n"
        "**Вход:**  \n"
        "`Описание входных данных`\n\n"
        "**Выход:**  \n"
        "`Ожидаемый результат`\n\n"
        "(При необходимости несколько примеров)\n"
        "Если будут важные данные (например, переменные или значения), используй ``"
    )

    api_key = os.getenv("OPENAI_API_KEY")

    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text}
        ]
    )

    return response.choices[0].message.content.strip()
