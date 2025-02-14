# app.py
import streamlit as st
from db import get_user_by_email
from pages.admin_dashboard import show_admin_dashboard

custom_css = """
<style>
/* Стили для кнопок при наведении */
div.stButton > button:hover {
    background-color: #1F2A3D !important;
    color: #FFFFFF !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

hide_sidebar_style = """
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

def main():


    # Если пользователь не аутентифицирован, показываем кнопку для входа
    if not st.experimental_user.is_logged_in:
        st.header("Авторизация")
        st.write("Нажмите на кнопку ниже, чтобы войти через OIDC-провайдера.")
        if st.button("Войти"):
            st.login()  # Использует настройки из [auth] в secrets.toml
    else:
        # Пользователь успешно аутентифицирован через провайдера
        user_info = st.experimental_user
        email = user_info.email  # Обычно email возвращается в токене
        st.write(f"Добро пожаловать, {user_info.name}!")

        # Проверяем наличие пользователя в БД по email
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
