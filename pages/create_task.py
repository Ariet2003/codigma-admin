import streamlit as st
import json
from utils.problem_generator import problem_generator

def show_create_task_page():
    # Подключение локального CSS файла
    def local_css(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css("styles/create_task.css")

    # Инициализация состояния для динамических полей
    if "input_count" not in st.session_state:
        st.session_state.input_count = 1
    if "output_count" not in st.session_state:
        st.session_state.output_count = 1

    # Коллбэки
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
    st.markdown('<h4>Детали задачи</h4>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Название задачи", key="task_name")
    with col2:
        st.selectbox("Сложность алгоритма", options=["Easy", "Medium", "Hard"], key="task_difficulty")

    # --- Описание задачи ---
    st.markdown('<h4>Описание задачи</h4>', unsafe_allow_html=True)
    st.text_area("Напишите в формате Marcdown (.md)", height=150, key="task_description")

    st.markdown("---")

    # --- Генератор шаблонного кода ---
    st.markdown('<h4>Генератор шаблонного кода</h4>', unsafe_allow_html=True)
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
    st.markdown('<h3>Структура выходных данных</h3>', unsafe_allow_html=True)
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

    # При нажатии кнопки собираем все данные, проверяем заполненность полей и выводим их в формате JSON
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

        # Если есть ошибки, выводим уведомление, иначе – выводим JSON
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

            # Выводим данные в виде форматированного JSON в терминал
            print(json.dumps(metadata, ensure_ascii=False, indent=4))
            st.success("Задача успешно создана! 🎉")

            # Вызов функции, которая возвращает JSON-строку с шаблонами кода
            boilerplate_codes = problem_generator(metadata)

            # Вывод полученных данных на консоль
            print(json.dumps(boilerplate_codes, ensure_ascii=False, indent=4))

    st.markdown('</div>', unsafe_allow_html=True)
