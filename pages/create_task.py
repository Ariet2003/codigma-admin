import streamlit as st
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES
import json
from utils.problem_generator import problem_generator
from utils.generate_leetcode_task import generate_leetcode_task
from utils.generate_tests import generate_tests  # Импорт функции generate_tests


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
                min_lines=15,
                # Динамический ключ, зависящий от выбранного языка
                key=f"ace_{ace_language}"
            )

        # Сохраняем значение слайдера в переменную test_count
        test_count = c2.slider("Количество тестов", 5, 20, 10)

        # Кнопка для генерации тесткейсов
        if c2.button("✨ Тесткейсы", type="primary"):
            # Проверяем, что шаблон задачи уже создан и сохранён
            if "metadata" not in st.session_state:
                st.error("Сначала создайте шаблон задачи!")
            else:
                task_name = st.session_state.get("task_name", "")
                metadata = st.session_state.get("metadata")
                # Берём solution_code из редактора st_ace
                solution_code = test_code
                tests = generate_tests(task_name, metadata, solution_code, test_count)
                print(tests)  # Вывод тесткейсов в консоль
                st.success("Тесткейсы сгенерированы и выведены в консоль.")

    st.markdown('</div>', unsafe_allow_html=True)
