# auth.py
from db import get_user_by_email
from utils.hashing import verify_password

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if user is None:
        return None
    db_email, db_password, role = user
    if verify_password(password, db_password):
        return {"email": db_email, "role": role}
    return None
