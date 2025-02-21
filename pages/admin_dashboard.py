import streamlit as st
from pages.settings import show_settings_page
from pages.create_task import show_create_task_page

def show_admin_dashboard(email: str):
    # Функция для подключения локального CSS файла
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Подключаем CSS стили из файла
    local_css("styles/dashboard.css")

    # Чтение query-параметров из URL с использованием нового API st.query_params
    if "page" in st.query_params:
        st.session_state.page = st.query_params["page"]
    elif "page" not in st.session_state:
        st.session_state.page = "Home"

    def set_page(page):
        st.session_state.page = page
        # Обновляем query-параметры, присваивая новое значение
        st.query_params.page = page

    # Боковая панель с кнопками навигации
    st.sidebar.title("Меню")
    if st.sidebar.button(" 🏠 Главная страница"):
        set_page("Home")
    if st.sidebar.button(" ⚔️ Хакатоны"):
        set_page("Hackathons")
    if st.sidebar.button(" 📜 Отчеты"):
        set_page("Reports")
    if st.sidebar.button(" 🏅 Рейтинг"):
        set_page("Ranking")
    if st.sidebar.button(" 🪄 Создать хакатон"):
        set_page("CreateHackathon")
    if st.sidebar.button(" ✒️ Создать задачу"):
        set_page("CreateTask")
    if st.sidebar.button(" ⚙️ Настройки"):
        set_page("Settings")

    # Основное содержимое страницы в зависимости от выбранного значения
    if st.session_state.page == "Home":
        st.title("Admin Panel")
        st.write("Добро пожаловать в админ-панель!")
    elif st.session_state.page == "Hackathons":
        st.title("Hackathons")
        st.write("Здесь отображаются все хакатоны.")
    elif st.session_state.page == "Reports":
        st.title("Reports")
        st.write("Здесь можно просматривать отчеты.")
    elif st.session_state.page == "Ranking":
        st.title("Ranking")
        st.write("Здесь отображается рейтинг участников.")
    elif st.session_state.page == "CreateHackathon":
        st.title("Create Hackathon")
        st.write("Форма для создания нового хакатона.")
    elif st.session_state.page == "CreateTask":
        show_create_task_page()
    elif st.session_state.page == "Settings":
        show_settings_page()


if __name__ == "__main__":
    # Предполагается, что пользователь уже аутентифицирован
    email = "admin@example.com"  # или получить реальный email
    show_admin_dashboard(email)
