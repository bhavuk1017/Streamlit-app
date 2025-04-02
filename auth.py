# import streamlit as st
# from config import USERS, INVIGILATORS

# # def authenticate_user(email, password):
# #     """Authenticate user with email and password."""
# #     if email in USERS and USERS[email] == password:
# #         st.session_state["user"] = email
# #         return True
# #     return False

# def authenticate_user(email, password):
#     """Authenticate user with email and password."""
#     if email not in USERS:
#         USERS[email] = "password123"
#         with open("config.py", "r") as f:
#             config_content = f.read()
        
#         # Update the USERS section in the file
#         updated_content = config_content.replace(
#             "USERS = {", 
#             f"USERS = {{\n    \"{email}\": \"password123\","
#         )
        
#         with open("config.py", "w") as f:
#             f.write(updated_content)

#     st.session_state["user"] = email
#     return True



# def authenticate_invigilator(email, password):
#     """Authenticate invigilator with email and password."""
#     if any(inv["email"] == email and inv["password"] == password for inv in INVIGILATORS.values()):
#         st.session_state["invigilator"] = email
#         return True
#     return False

# def is_user_authenticated():
#     """Check if a user is currently authenticated."""
#     return "user" in st.session_state

# def is_invigilator_authenticated():
#     """Check if an invigilator is currently authenticated."""
#     return "invigilator" in st.session_state

# def get_current_user():
#     """Get currently authenticated user's email."""
#     return st.session_state.get("user")

# def get_current_invigilator():
#     """Get currently authenticated invigilator's email."""
#     return st.session_state.get("invigilator")

# def logout_user():
#     """Log out current user."""
#     if "user" in st.session_state:
#         del st.session_state["user"]

# def logout_invigilator():
#     """Log out current invigilator."""
#     if "invigilator" in st.session_state:
#         del st.session_state["invigilator"]

import streamlit as st
from database import users_collection, invigilators_collection
from pymongo.errors import DuplicateKeyError
from email_service import send_email 

def authenticate_user(email, password):
    """Authenticate a user with email and password."""
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        st.session_state["authenticated"] = True
        st.session_state["user"] = email
        return True
    return False

def authenticate_invigilator(email, password):
    """Authenticate an invigilator with email and password."""
    invigilator = invigilators_collection.find_one({"email": email, "password": password})
    if invigilator:
        st.session_state["invigilator_authenticated"] = True
        st.session_state["invigilator"] = email
        return True
    return False

def is_user_authenticated():
    """Check if a user is authenticated."""
    return st.session_state.get("authenticated", False)

def is_invigilator_authenticated():
    """Check if an invigilator is authenticated."""
    return st.session_state.get("invigilator_authenticated", False)

def get_current_user():
    """Get the current authenticated user."""
    return st.session_state.get("user", None)

def get_current_invigilator():
    """Get the current authenticated invigilator."""
    return st.session_state.get("invigilator", None)

def get_invigilator_name_by_email(email):
    """Get invigilator name from email."""
    invigilator = invigilators_collection.find_one({"email": email})
    return invigilator.get("name") if invigilator else None

# def register_user(email, password, name):
#     """Register a new user."""
#     try:
#         users_collection.insert_one({
#             "email": email,
#             "password": password,
#             "name": name
#         })
#         return True
#     except DuplicateKeyError:
#         return False
from pymongo.errors import DuplicateKeyError
from google.auth.exceptions import GoogleAuthError

def register_user(email, password, name):
    """Register a new user after verifying the email."""
    try:
        # Attempt to send a verification email
        subject = "Email Verification"
        body = f"Hello {name},\n\nThank you for registering. Please verify your email address."
        
        if not send_email(email, subject, body):
            return {"success": False, "error": "Invalid email address. Could not send verification email."}
        
        # Insert user into the database if email is valid
        users_collection.insert_one({
            "email": email,
            "password": password,
            "name": name
        })
        return {"success": True, "message": "User registered successfully."}
    
    except DuplicateKeyError:
        return {"success": False, "error": "Email already exists. Please use a different email."}
    
    except GoogleAuthError as e:
        return {"success": False, "error": f"Google Authentication Error: {str(e)}"}
    
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

def logout_user():
    """Log out the current user."""
    if "authenticated" in st.session_state:
        del st.session_state["authenticated"]
    if "user" in st.session_state:
        del st.session_state["user"]
def get_all_invigilators():
    """Get a list of all available invigilators."""
    invigilators = invigilators_collection.find({}, {"email": 1, "name": 1})
    return list(invigilators)





