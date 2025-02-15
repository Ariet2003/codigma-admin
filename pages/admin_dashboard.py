import streamlit as st


def show_admin_dashboard(email: str):
    # Функция для подключения локального CSS файла
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Подключаем CSS стили из файла
    local_css("styles/dashboard.css")

    # Инициализация выбранной страницы по умолчанию
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    def set_page(page):
        st.session_state.page = page

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

    # Основное содержимое страницы
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
        st.title("Create Task")
        st.write("Форма для создания новой задачи.")
    elif st.session_state.page == "Settings":
        st.title("Settings")
        st.write("Настройки админ-панели.")
