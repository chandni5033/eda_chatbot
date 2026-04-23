import streamlit as st
from streamlit_oauth import OAuth2Component
import matplotlib.pyplot as plt
import pandas as pd
import os
import uuid
import ast
import jwt
from dotenv import load_dotenv

from sql_agent import query_database_with_sql
from db import get_db
from mongo_history import (
    save_message,
    load_messages,
    get_all_sessions,
    delete_session
)

load_dotenv()

# ------------------  GOOGLE AUTH ------------------
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/auth",
    "https://oauth2.googleapis.com/token",
)

if "user" not in st.session_state:
    result = oauth2.authorize_button(
        name="Login with Google",
        redirect_uri="http://localhost:8501",
        scope="openid email profile",
    )

    if result:
        id_token = result["token"]["id_token"]
        decoded = jwt.decode(id_token, options={"verify_signature": False})

        st.session_state.user = {
            "email": decoded["email"],
            "name": decoded["name"],
            "sub": decoded["sub"]
        }
        st.rerun()

    st.stop()

user_email = st.session_state.user["email"]

# ------------------ CONFIG ------------------
st.set_page_config(page_title="EDA Chatbot", layout="wide")

# ------------------ SESSION INIT ------------------
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

if "db_instance" not in st.session_state:
    st.session_state.db_instance = None

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "session_name" not in st.session_state:
    st.session_state.session_name = "New chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ HELPERS ------------------
def generate_session_name(prompt):
    return prompt.strip().capitalize()[:40]


# ------------------ SIDEBAR ------------------
with st.sidebar:

    st.write(f"👤 {st.session_state.user['name']}")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if st.button("✏️ New chat"):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.session_name = "New chat"
        st.session_state.messages = []
        st.rerun()

    st.divider()

    #  DB Connection
    st.markdown("### 🗄️ Database Connection")

    db_host = st.text_input("Host", value="localhost")
    db_user = st.text_input("Username", value="root")
    db_password = st.text_input("Password", type="password")
    db_name = st.text_input("Database name")

    if st.button("Connect"):
        try:
            db = get_db(
                host=db_host,
                user=db_user,
                password=db_password,
                name=db_name
            )
            db.run("SELECT 1")
            st.session_state.db_instance = db
            st.session_state.db_connected = True
            st.success("Connected")
        except Exception as e:
            st.error(f"Connection failed: {e}")

    st.divider()

    #  Chat Sessions
    st.markdown("### 💬 Chats")

    sessions = get_all_sessions(user_email)

    for s in sessions:

        col1, col2 = st.columns([4, 1])

        # OPEN CHAT
        with col1:
            if st.button(s["session_name"], key=f"open_{s['_id']}"):
                st.session_state.session_id = s["_id"]
                st.session_state.session_name = s["session_name"]
                st.session_state.messages = load_messages(user_email, s["_id"])
                st.rerun()

        # DELETE CHAT
        with col2:
            if st.button("🗑️", key=f"del_{s['_id']}"):
                delete_session(user_email, s["_id"])
                st.rerun()

# ------------------ MAIN ------------------
st.title("📊 EDA Chatbot")

if not st.session_state.db_connected:
    st.info("👈 Connect to database first")
    st.stop()

# ------------------ CHAT HISTORY ------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if msg["role"] == "assistant" and msg.get("sql"):
            st.code(msg["sql"], language="sql")

# ------------------ INPUT ------------------
if prompt := st.chat_input("Ask your data..."):

    # Auto session naming
    if st.session_state.session_name == "New chat":
        st.session_state.session_name = generate_session_name(prompt)

    # ---------------- SAVE USER MESSAGE ----------------
    save_message(
        user_email,
        st.session_state.session_id,
        st.session_state.session_name,
        "user",
        prompt
    )

    with st.chat_message("user"):
        st.write(prompt)

    # ---------------- ASSISTANT ----------------
    with st.chat_message("assistant"):

        raw, sql = query_database_with_sql(
            prompt,
            st.session_state.db_instance
        )

        # Show SQL
        if sql:
            st.code(sql, language="sql")

        # ---------------- HANDLE ERROR ----------------
        if isinstance(raw, str) and raw.startswith("SQL Error"):
            st.error(raw)

        else:
            try:
                df = pd.DataFrame(raw)

                if df.empty:
                    st.info("No data found")
                else:
                    st.dataframe(df.head(50))
            except Exception as e:
                st.error("Could not display result")

        # ---------------- SAVE ASSISTANT MESSAGE ----------------
        save_message(
            user_email,
            st.session_state.session_id,
            st.session_state.session_name,
            "assistant",
            "Generated SQL query",   
            sql
        )

        # ---------------- REFRESH CHAT ----------------
        st.session_state.messages = load_messages(
            user_email,
            st.session_state.session_id
        )