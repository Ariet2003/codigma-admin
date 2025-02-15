import streamlit as st


def show_settings_page():
    # Центрируем содержимое с помощью встроенного HTML и CSS

    st.title("Настройки админ-панели")
    st.write("Добро пожаловать в раздел настроек! Здесь вы можете управлять своим аккаунтом.")

    st.subheader("Управление аккаунтом 👤")
    if st.button("Выйти из аккаунта 🚪"):
        st.logout()


