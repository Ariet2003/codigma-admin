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
        st.session_state.page = "Главная страница"

    def set_page(page):
        st.session_state.page = page

    # Боковая панель с кнопками навигации
    st.sidebar.title("Меню")
    if st.sidebar.button("Главная страница"):
        set_page("Главная страница")
    if st.sidebar.button("Хакатоны"):
        set_page("Хакатоны")
    if st.sidebar.button("Отчеты"):
        set_page("Отчеты")
    if st.sidebar.button("Рейтинг"):
        set_page("Рейтинг")
    if st.sidebar.button("Создать хакатон"):
        set_page("Создать хакатон")
    if st.sidebar.button("Настройки"):
        set_page("Настройки")

    # Основное содержимое страницы
    if st.session_state.page == "Главная страница":
        st.title("Админ-панель")
        st.write("Добро пожаловать в админ-панель!")
    elif st.session_state.page == "Хакатоны":
        st.title("Хакатоны")
        st.write("Здесь отображаются все хакатоны.")
    elif st.session_state.page == "Отчеты":
        st.title("Отчеты")
        st.write("Здесь можно просматривать отчеты.")
    elif st.session_state.page == "Рейтинг":
        st.title("Рейтинг")
        st.write("Здесь отображается рейтинг участников.")
    elif st.session_state.page == "Создать хакатон":
        st.title("Создать хакатон")
        st.write("Форма для создания нового хакатона.")
    elif st.session_state.page == "Настройки":
        st.title("Настройки")
        st.write("Настройки админ-панели.")