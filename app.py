import streamlit as st
from db import get_user_by_email
from pages.admin_dashboard import show_admin_dashboard


# Функция для загрузки CSS-файла
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Загружаем глобальные стили
load_css("styles/global.css")


def main():
    if not st.experimental_user.is_logged_in:
        # Загружаем стили только для страницы входа
        load_css("styles/login.css")

        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        # Аватарка
        st.image("public/admin_avatar.png", width=150)

        # Заголовок
        st.header("Вход в админку")

        # Описание
        st.write("Нажмите на кнопку ниже, чтобы войти через OIDC-провайдера.")

        # Кнопка для входа через Google
        if st.button("Войти через Google"):
            st.login()  # Использует настройки из [auth] в secrets.toml

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Пользователь аутентифицирован
        user_info = st.experimental_user
        email = user_info.email
        st.write(f"Добро пожаловать, {user_info.name}!")

        db_user = get_user_by_email(email)
        if db_user:
            _, _, role = db_user
            if role == 'ADMIN':
                show_admin_dashboard(email)
            else:
                st.error("У вас недостаточно прав для доступа к этой странице.")
        else:
            st.error("Пользователь не найден в базе данных.")

        if st.button("Выйти"):
            st.logout()


if __name__ == "__main__":
    main()
