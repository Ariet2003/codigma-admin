import streamlit as st
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES
import json
from utils.problem_generator import problem_generator
from utils.generate_leetcode_task import generate_leetcode_task
from utils.generate_tests import generate_tests
from utils.parse_tests import parse_tests
from utils.run_tests_on_code import run_judge0_testcases

def show_create_task_page():
    # Функция для подключения локального CSS файла
    def local_css(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Подключаем глобальные стили и стили для описания задачи отдельно
    local_css("styles/create_task.css")
    local_css("styles/description.css")  # Здесь находятся стили для контейнера описания

    # Инициализация состояния для динамических полей
    if "input_count" not in st.session_state:
        st.session_state.input_count = 1
    if "output_count" not in st.session_state:
        st.session_state.output_count = 1

    # Коллбэки для добавления/удаления полей
    def add_input_callback():
        st.session_state.input_count += 1

    def add_output_callback():
        st.session_state.output_count += 1

    def remove_input_callback():
        if st.session_state.input_count > 1:
            st.session_state.input_count -= 1

    def remove_output_callback():
        if st.session_state.output_count > 1:
            st.session_state.output_count -= 1

    def delete_test(i):
        tests = st.session_state["formatted_tests"]
        tests.pop(i)
        st.session_state["formatted_tests"] = tests
        # Переключаем флаг, чтобы обновить состояние
        st.session_state["delete_flag"] = not st.session_state.get("delete_flag", False)

    # Новый callback для добавления тесткейса
    def add_test_case():
        if "formatted_tests" not in st.session_state:
            st.session_state["formatted_tests"] = []
        st.session_state["formatted_tests"].append({"input": "", "expected_output": ""})
        st.session_state["add_test_flag"] = not st.session_state.get("add_test_flag", False)

    # Основной контейнер
    st.markdown('<div class="create-task-container">', unsafe_allow_html=True)
    st.markdown('<h2>Создание задачи</h2>', unsafe_allow_html=True)

    # --- Детали задачи ---
    st.markdown('<h3>Детали задачи</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Название задачи", key="task_name")
    with col2:
        st.selectbox("Сложность алгоритма", options=["Easy", "Medium", "Hard"], key="task_difficulty")

    # --- Описание задачи ---
    st.markdown('<h5>Описание задачи</h5>', unsafe_allow_html=True)

    # Инициализируем значение описания задачи, если его ещё нет
    if "task_description" not in st.session_state:
        st.session_state["task_description"] = ""

    col_add_rem_out = st.columns(3)
    with col_add_rem_out[0]:
        if st.button("✨ Генерировать Markdown"):
            st.session_state["task_description"] = generate_leetcode_task(st.session_state["task_description"])
    with col_add_rem_out[1]:
        # Переключатель для выбора режима отображения Markdown
        toggle_state = st.toggle("Markdown", key="markdown_toggle")

    if toggle_state:
        # Если включён режим Markdown, отображаем текст в контейнере с классом для стилей
        st.markdown(
            f'<div class="description-markdown-container">{"\n\n" + st.session_state["task_description"]}</div>',
            unsafe_allow_html=True
        )
    else:
        # Если переключатель выключен, показываем текстовое поле для редактирования.
        new_text = st.text_area(
            "Напишите условие и примеры тестов (входные и выходные данные)",
            height=150,
            value=st.session_state["task_description"],
            key="task_description_edit"
        )
        # Сохраняем введённое значение в основной ключ
        st.session_state["task_description"] = new_text

    st.markdown("---")

    # --- Генератор шаблонного кода ---
    st.markdown('<h3>Генератор шаблонного кода</h3>', unsafe_allow_html=True)
    st.text_input("Название функции", key="function_name")
    st.text("")
    st.text("")

    # --- Входные данные ---
    st.markdown('<h5>Структура входных данных</h5>', unsafe_allow_html=True)
    input_types = ["int", "float", "string", "bool", "list<int>", "list<float>", "list<string>", "list<bool>"]

    for i in range(st.session_state.input_count):
        col_var, col_type = st.columns([2, 1])
        with col_var:
            st.text_input(f"Название переменной {i + 1} (вход)", key=f"input_name_{i}")
        with col_type:
            st.selectbox(f"Тип переменной {i + 1}", options=input_types, key=f"input_type_{i}")

    col_add_rem = st.columns(6)
    with col_add_rem[0]:
        st.button("Добавить", on_click=add_input_callback)
    with col_add_rem[1]:
        st.button("Удалить", on_click=remove_input_callback)

    # --- Выходные данные ---
    st.markdown('<h5>Структура выходных данных</h5>', unsafe_allow_html=True)
    for i in range(st.session_state.output_count):
        col_var, col_type = st.columns([2, 1])
        with col_var:
            st.text_input(f"Название переменной {i + 1} (выход)", key=f"output_name_{i}")
        with col_type:
            st.selectbox(f"Тип переменной {i + 1}", options=input_types, key=f"output_type_{i}")

    col_add_rem_out = st.columns(6)
    with col_add_rem_out[0]:
        st.button("Добавить ", on_click=add_output_callback)
    with col_add_rem_out[1]:
        st.button("Удалить ", on_click=remove_output_callback)

    # При нажатии кнопки собираем все данные, проверяем заполненность полей и генерируем шаблоны
    if st.button("💡 Создать шаблон", type="primary"):
        error_messages = []
        # Проверка обязательных полей
        if not st.session_state.get("task_name", "").strip():
            error_messages.append("Название задачи не заполнено!")
        if not st.session_state.get("task_description", "").strip():
            error_messages.append("Описание задачи не заполнено!")
        if not st.session_state.get("function_name", "").strip():
            error_messages.append("Название функции не заполнено!")

        # Проверка входных данных
        for i in range(st.session_state.input_count):
            if not st.session_state.get(f"input_name_{i}", "").strip():
                error_messages.append(f"Название переменной входа {i + 1} не заполнено!")

        # Проверка выходных данных
        for i in range(st.session_state.output_count):
            if not st.session_state.get(f"output_name_{i}", "").strip():
                error_messages.append(f"Название переменной выхода {i + 1} не заполнено!")

        if error_messages:
            st.error("Пожалуйста, заполните все обязательные поля:\n" + "\n".join(error_messages))
        else:
            metadata = {
                "task_name": st.session_state.get("task_name", ""),
                "difficulty": st.session_state.get("task_difficulty", ""),
                "description": st.session_state.get("task_description", ""),
                "function_name": st.session_state.get("function_name", ""),
                "inputs": [],
                "outputs": []
            }
            for i in range(st.session_state.input_count):
                input_name = st.session_state.get(f"input_name_{i}", "")
                input_type = st.session_state.get(f"input_type_{i}", "")
                metadata["inputs"].append({"name": input_name, "type": input_type})
            for i in range(st.session_state.output_count):
                output_name = st.session_state.get(f"output_name_{i}", "")
                output_type = st.session_state.get(f"output_type_{i}", "")
                metadata["outputs"].append({"name": output_name, "type": output_type})

            print(json.dumps(metadata, ensure_ascii=False, indent=4))
            st.success("Шаблонные коды успешно созданы! 🎉")
            # Сохраняем сгенерированные шаблоны в st.session_state
            st.session_state.boilerplate_dict = problem_generator(metadata)
            # Сохраняем metadata для дальнейшего использования
            st.session_state.metadata = metadata

    # Если шаблоны уже сгенерированы, отображаем комбобокс и блоки с кодом
    if "boilerplate_dict" in st.session_state:
        st.markdown("---")
        boilerplate_dict = st.session_state.boilerplate_dict

        # Комбобокс для выбора языка (с сохранением выбора в session_state)
        lang_options = ["C++", "JavaScript", "Rust", "Java"]
        selected_lang = st.selectbox("Выберите язык для отображения кода", lang_options, key="selected_lang")

        # Определяем ключи для выбранного языка и параметр language для st.code
        if selected_lang == "C++":
            template_key = "cppTemplate"
            full_key = "fullCpp"
            code_lang = "cpp"
        elif selected_lang == "JavaScript":
            template_key = "jsTemplate"
            full_key = "fullJs"
            code_lang = "javascript"
        elif selected_lang == "Rust":
            template_key = "rustTemplate"
            full_key = "fullRust"
            code_lang = "rust"
        elif selected_lang == "Java":
            template_key = "javaTemplate"
            full_key = "fullJava"
            code_lang = "java"

        template_code = boilerplate_dict.get(template_key, "")
        full_code = boilerplate_dict.get(full_key, "")

        st.markdown('<h5>Шаблонный код</h5>', unsafe_allow_html=True)
        st.code(template_code, language=code_lang)
        st.markdown('<h5>Полный шаблонный код</h5>', unsafe_allow_html=True)
        st.code(full_code, language=code_lang)

        st.divider()

        st.markdown('<h3>Тесты для задачки</h3>', unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        c2.subheader("Parameters")

        # Выбор языка для редактора тестов
        ace_language = c2.selectbox(
            "Языковой режим для тестов",
            options=["c_cpp", "javascript", "rust", "java"],
            index=0,
            key="ace_language"
        )

        # Определяем значение по умолчанию для редактора тестов в зависимости от выбранного языка
        default_code_mapping = {
            "c_cpp": boilerplate_dict.get("cppTemplate", ""),
            "javascript": boilerplate_dict.get("jsTemplate", ""),
            "rust": boilerplate_dict.get("rustTemplate", ""),
            "java": boilerplate_dict.get("javaTemplate", "")
        }
        default_test_code = default_code_mapping.get(ace_language, template_code)

        with c1:
            test_code = st_ace(
                value=default_test_code,
                placeholder="Напишите свой код здесь",
                language=ace_language,
                theme="cobalt",
                keybinding="vscode",
                font_size=14,
                tab_size=8,
                show_gutter=True,
                show_print_margin=False,
                wrap=False,
                auto_update=True,
                readonly=False,
                min_lines=17,
                # Динамический ключ, зависящий от выбранного языка
                key=f"ace_{ace_language}"
            )

        # Сохраняем значение слайдера в переменную test_count
        test_count = c2.slider("Количество тестов", 1, 20, 10)

        # Кнопка для генерации тесткейсов
        if c2.button("✨ Тесткейсы", type="primary"):
            if "metadata" not in st.session_state:
                st.error("Сначала создайте шаблон задачи!")
            else:
                task_name = st.session_state.get("task_name", "")
                metadata = st.session_state.get("metadata")
                solution_code = test_code
                tests = generate_tests(task_name, metadata, solution_code, test_count)
                new_formatted_tests = parse_tests(tests)
                # Если тесткейсы уже существуют, добавляем новые, иначе создаём новый список
                if "formatted_tests" in st.session_state:
                    st.session_state["formatted_tests"].extend(new_formatted_tests)
                else:
                    st.session_state["formatted_tests"] = new_formatted_tests

        # Добавляем кнопку для ручного добавления нового тесткейса
        st.button("Добавить тесткейc", on_click=add_test_case)

        # Вывод тесткейсов, если они уже сохранены, и кнопка для их тестирования через Judge0
        if "formatted_tests" in st.session_state:
            st.markdown("### Сгенерированные тесткейсы")
            for i, test in enumerate(st.session_state["formatted_tests"]):
                col_input, col_expected, col_delete = st.columns([3, 3, 1])
                with col_input:
                    st.text_area(f"Входные данные {i + 1}", value=test["input"], key=f"test_input_{i}")
                with col_expected:
                    st.text_area(f"Ожидаемый вывод {i + 1}", value=test["expected_output"], key=f"test_output_{i}")
                with col_delete:
                    st.button("Удалить", key=f"delete_test_{i}", on_click=delete_test, args=(i,))



            # Кнопка для тестирования тесткейсов через Judge0
            if st.button("Тестировать тесткейсы", icon="🚀", type="primary"):
                if "formatted_tests" not in st.session_state:
                    st.error("Сначала сгенерируйте тесткейсы!")
                else:
                    # Обновляем значения тесткейсов из текстовых полей
                    for i in range(len(st.session_state["formatted_tests"])):
                        st.session_state["formatted_tests"][i]["input"] = st.session_state.get(f"test_input_{i}", "")
                        st.session_state["formatted_tests"][i]["expected_output"] = st.session_state.get(
                            f"test_output_{i}", "")

                    # Преобразуем тесткейсы в нужный формат, приводя stdin и expected_output к строке
                    testcases = []
                    for t in st.session_state["formatted_tests"]:
                        testcases.append({
                            "stdin": str(t.get("input", "")),
                            "expected_output": str(t.get("expected_output", ""))
                        })

                    # Определяем language_id для Judge0 на основе выбранного языка
                    judge0_language_ids = {
                        "c_cpp": 54,
                        "javascript": 63,
                        "rust": 73,
                        "java": 62
                    }
                    test_lang = st.session_state.get("ace_language", "c_cpp")
                    language_id = judge0_language_ids.get(test_lang, 54)

                    # Определяем полный шаблонный код для тестирования на основе выбранного языка в ace_language
                    if ace_language == "c_cpp":
                        full_key_test = "fullCpp"
                    elif ace_language == "javascript":
                        full_key_test = "fullJs"
                    elif ace_language == "rust":
                        full_key_test = "fullRust"
                    elif ace_language == "java":
                        full_key_test = "fullJava"

                    full_code_test = boilerplate_dict.get(full_key_test, "")
                    # Подставляем код из редактора (test_code) в шаблонный код для тестирования
                    prepared_source_code = full_code_test.replace("##USER_CODE_HERE##", test_code)

                    data_payload = {
                        "language_id": language_id,
                        "source_code": prepared_source_code,
                        "testcases": testcases
                    }
                    print(data_payload)

                    # Вызываем функцию тестирования и выводим результат в консоль
                    result = run_judge0_testcases(data_payload)
                    print("Результаты тестирования:")
                    print(json.dumps(result, ensure_ascii=False, indent=4))

                    # Новая логика: если все тесты прошли, выводим сообщение об успехе,
                    # иначе выводим номера тестов, которые не прошли (индексы преобразуем в 1-индексированные)
                    if result.get("status") == 1:
                        st.success("Все тесты успешно прошли!")
                    else:
                        incorrect_indexes = result.get("incorrect_test_indexes", [])
                        stderr = result.get("stderr")
                        incorrect_indexes = [str(idx + 1) for idx in incorrect_indexes]  # преобразуем в 1-индексацию
                        if stderr != "Правильно":
                            st.error("Следующие тесты не прошли: " + ", ".join(incorrect_indexes))
                            st.error("Вывод компиляции: " + stderr)
                        else:
                            st.error("Следующие тесты не прошли: " + ", ".join(incorrect_indexes))
                            st.error("Важно: если вы уверены, что тесткейсы правильные, возможно, код содержит ошибку. Убедитесь, что написанный код также верный.")

    st.markdown('</div>', unsafe_allow_html=True)
