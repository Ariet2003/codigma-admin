import streamlit as st
from datetime import datetime
import uuid
from db import get_all_tasks, create_hackathon

@st.dialog("Подтвердите создание хакатона")
def confirm_create_hackathon(hackathon_data):
    st.markdown("#### Проверьте данные хакатона:")
    st.write("**Название:**", hackathon_data["title"])
    st.write("**Описание:**", hackathon_data["description"])
    st.write("**Начало:**", hackathon_data["startTime"])
    st.write("**Окончание:**", hackathon_data["endTime"])
    st.write("**Открытый:**", "Да" if not hackathon_data["hidden"] else "Нет")
    st.write("**Выбранные задачи:**", hackathon_data["selected_task_names"])
    if st.button("Подтвердить создание"):
        result = create_hackathon(hackathon_data)
        st.session_state.hackathon_created = result
        st.rerun()

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

    # Флажок для определения, является ли хакатон открытым
    is_open = st.checkbox("Открытый хакатон", key="is_open")

    st.markdown("---")
    # Получение списка задач из БД (ожидается, что функция вернёт список словарей с ключами id и title)
    tasks = get_all_tasks()
    task_options = {task["title"]: task["id"] for task in tasks}
    selected_tasks = st.multiselect(
        "Выберите задачи для хакатона",
        placeholder="Выберите задачи",
        options=list(task_options.keys())
    )

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

            # Подготовка данных хакатона в виде словаря с генерацией уникального id
            hackathon_data = {
                "id": str(uuid.uuid4()),
                "title": hackathon_title,
                "description": hackathon_description,
                "startTime": start_datetime,
                "endTime": end_datetime,
                "hidden": not is_open,  # если хакатон открытый, hidden будет False
                "selected_problem_ids": [task_options[title] for title in selected_tasks],
                "selected_task_names": selected_tasks
            }
            # Открываем диалоговое окно для подтверждения создания хакатона
            confirm_create_hackathon(hackathon_data)

    # Если результат создания хакатона уже сохранён в session_state, отображаем сообщение
    if "hackathon_created" in st.session_state:
        if st.session_state.hackathon_created:
            st.success("Хакатон успешно создан!")
        else:
            st.error("Произошла ошибка при создании хакатона!")
        # Очистка состояния для повторного создания
        del st.session_state.hackathon_created

    st.markdown("</div>", unsafe_allow_html=True)
