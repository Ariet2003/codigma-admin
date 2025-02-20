import json
import re


def extract_json(tests_str):
    """
    Извлекает чистую JSON-строку из входного текста.

    Сначала пытается найти блок, обрамлённый тегами ```json ... ```.
    Если такой блок не найден, ищет первую открывающую '[' и последнюю закрывающую ']'
    и возвращает подстроку между ними.

    :param tests_str: Исходная строка, содержащая тесты с дополнительным текстом.
    :return: Чистая JSON-строка.
    :raises ValueError: Если JSON не найден.
    """
    # Попытка извлечь блок, обрамлённый ```json ... ```
    match = re.search(r"```json\s*(\[[\s\S]*\])\s*```", tests_str)
    if match:
        return match.group(1)

    # Если блок с ```json не найден, пытаемся извлечь содержимое от первой '[' до последней ']'
    start = tests_str.find('[')
    end = tests_str.rfind(']')
    if start != -1 and end != -1 and start < end:
        return tests_str[start:end + 1]

    raise ValueError("No valid JSON found in the input string.")


def parse_tests(tests_str):
    """
    Принимает строку с тестами (возможно, содержащую дополнительный текст вокруг JSON) и преобразует каждый тест так, чтобы:
      - Поле "input" стало строкой с форматированием:
          * Если значение является списком: первая строка — количество элементов, вторая — элементы через пробел.
          * Если значение не список: просто строковое представление.
          Порядок строк соответствует порядку ключей во входном словаре.
      - Поле "expected_output":
          * Если это булево значение, оно преобразуется в "true"/"false".
          * Если это словарь с единственным ключом (название ключа может быть любым), используется только его значение.

    :param tests_str: Строка, содержащая тесты в формате JSON, возможно с дополнительным текстом.
    :return: Список словарей с отформатированными тестами.
    """
    # Сначала извлекаем чистую JSON-строку
    json_str = extract_json(tests_str)
    tests = json.loads(json_str)
    formatted_tests = []

    for test in tests:
        input_data = test.get("input", {})
        lines = []

        # Форматируем поле "input"
        for key, value in input_data.items():
            if isinstance(value, list):
                lines.append(str(len(value)))  # Первая строка: количество элементов
                lines.append(" ".join(str(item) for item in value))  # Вторая строка: элементы через пробел
            else:
                lines.append(str(value))

        formatted_input = "\n".join(lines)

        # Обрабатываем поле "expected_output"
        expected_output = test.get("expected_output")
        # Если это словарь с единственным ключом (название ключа может быть любым), берём только его значение.
        if isinstance(expected_output, dict) and len(expected_output) == 1:
            expected_output = next(iter(expected_output.values()))

        # Если булево значение, приводим к "true"/"false"
        if isinstance(expected_output, bool):
            expected_output = str(expected_output).lower()

        formatted_tests.append({
            "input": formatted_input,
            "expected_output": expected_output
        })

    return formatted_tests