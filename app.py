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
        load_css("styles/login.css")
        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        st.image("public/admin_avatar.png", width=150)

        st.header("Вход в админку")
        st.write("Нажмите на кнопку ниже, чтобы войти через OIDC-провайдера.")
        if st.button("Войти через Google"):
            st.login()  # Использует настройки из [auth] в secrets.toml

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Пользователь аутентифицирован
        user_info = st.experimental_user
        email = user_info.email

        db_user = get_user_by_email(email)
        if db_user:
            _, _, role = db_user
            if role == 'ADMIN':
                show_admin_dashboard(email)
            else:
                load_css("styles/login.css")
                st.error("У вас недостаточно прав для доступа к этой странице.")
        else:
            load_css("styles/login.css")
            st.error("Пользователь не найден в базе данных.")

        if st.button("Выйти"):
            st.logout()


if __name__ == "__main__":
    main()
