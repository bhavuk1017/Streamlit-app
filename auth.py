import streamlit as st
from config import USERS, INVIGILATORS

def authenticate_user(email, password):
    """Authenticate user with email and password."""
    if email in USERS and USERS[email] == password:
        st.session_state["user"] = email
        return True
    return False

def authenticate_invigilator(email, password):
    """Authenticate invigilator with email and password."""
    if any(inv["email"] == email and inv["password"] == password for inv in INVIGILATORS.values()):
        st.session_state["invigilator"] = email
        return True
    return False

def is_user_authenticated():
    """Check if a user is currently authenticated."""
    return "user" in st.session_state

def is_invigilator_authenticated():
    """Check if an invigilator is currently authenticated."""
    return "invigilator" in st.session_state

def get_current_user():
    """Get currently authenticated user's email."""
    return st.session_state.get("user")

def get_current_invigilator():
    """Get currently authenticated invigilator's email."""
    return st.session_state.get("invigilator")

def logout_user():
    """Log out current user."""
    if "user" in st.session_state:
        del st.session_state["user"]

def logout_invigilator():
    """Log out current invigilator."""
    if "invigilator" in st.session_state:
        del st.session_state["invigilator"]