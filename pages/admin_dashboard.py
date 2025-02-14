# pages/admin_dashboard.py
import streamlit as st

def show_admin_dashboard(email: str):
    st.title("Админ-панель")
    st.write(f"Добро пожаловать в админ-панель, {email}!")
    # Здесь можно добавить дополнительную функциональность для администратора
