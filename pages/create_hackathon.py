import streamlit as st
from datetime import datetime
from db import get_all_tasks, create_hackathon


def show_create_hackathon_page():
    # Функция для подключения CSS-стилей
    def local_css(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css("styles/create_hackathon.css")

    st.markdown('<div class="create-hackathon-container">', unsafe_allow_html=True)
    st.markdown("<h2>Создание Хакатона</h2>", unsafe_allow_html=True)

    # Ввод основных данных хакатона
    hackathon_title = st.text_input("Название хакатона", key="hackathon_title")
    hackathon_description = st.text_area("Описание хакатона", key="hackathon_description", height=150)

    # Разбиваем на две колонки: для даты и времени начала и окончания
    start_col, end_col = st.columns(2)

    with start_col:
        st.markdown("#### Начало хакатона")
        start_date = st.date_input("Дата начала", key="start_date", value=datetime.today())
        start_time_input = st.time_input("Время начала", key="start_time", value=datetime.now().time())

    with end_col:
        st.markdown("#### Окончание хакатона")
        end_date = st.date_input("Дата окончания", key="end_date", value=datetime.today())
        end_time_input = st.time_input("Время окончания", key="end_time", value=datetime.now().time())

    # Флажок, определяющий, является ли хакатон открытым (если открытый — hidden = False)
    is_open = st.checkbox("Открытый хакатон", key="is_open")

    st.markdown("---")
    # Получение списка задач из БД (ожидается, что функция вернёт список словарей с ключами id и title)
    tasks = get_all_tasks()
    task_options = {task["title"]: task["id"] for task in tasks}
    selected_tasks = st.multiselect("Выберите задачи для хакатона", placeholder="Выберите задачи", options=list(task_options.keys()))

    if st.button("Создать хакатон", type="primary"):
        error_messages = []
        if not hackathon_title.strip():
            error_messages.append("Название хакатона не может быть пустым!")
        if not hackathon_description.strip():
            error_messages.append("Описание хакатона не может быть пустым!")
        if start_date > end_date:
            error_messages.append("Дата начала не может быть позже даты окончания!")

        if error_messages:
            st.error("\n".join(error_messages))
        else:
            # Формирование объектов datetime для начала и окончания
            start_datetime = datetime.combine(start_date, start_time_input)
            end_datetime = datetime.combine(end_date, end_time_input)

            # Подготовка данных хакатона в виде словаря
            hackathon_data = {
                "title": hackathon_title,
                "description": hackathon_description,
                "startTime": start_datetime,
                "endTime": end_datetime,
                "hidden": not is_open,  # если хакатон открытый, hidden будет False
                "selected_problem_ids": [task_options[title] for title in selected_tasks]
            }

            # Вызов функции создания хакатона в БД
            result = create_hackathon(hackathon_data)
            if result:
                st.success("Хакатон успешно создан!")
            else:
                st.error("Произошла ошибка при создании хакатона!")

    st.markdown("</div>", unsafe_allow_html=True)
