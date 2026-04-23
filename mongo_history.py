from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


# ---------------- CONNECT ----------------
def get_collection():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["eda_chatbot"]
    collection = db["chat_history"]

    
    collection.create_index([("timestamp", -1)])

    return collection


# ---------------- SAVE MESSAGE ----------------
def save_message(user_email, session_id, session_name, role, content, sql=""):
    collection = get_collection()

    collection.insert_one({
        "user_email": user_email,
        "session_id": session_id,
        "session_name": session_name,
        "role": role,
        "content": content,
        "sql": sql,
        "timestamp": datetime.now()  
    })


# ---------------- LOAD MESSAGES ----------------
def load_messages(user_email, session_id):
    collection = get_collection()

    return list(collection.find(
        {"user_email": user_email, "session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1))   


# ---------------- GET ALL SESSIONS ----------------
def get_all_sessions(user_email):
    collection = get_collection()

    pipeline = [
        {"$match": {"user_email": user_email}},  

        {"$sort": {"timestamp": -1}}, 

        {"$group": {
            "_id": "$session_id",
            "session_name": {"$first": "$session_name"},
            "last_message": {"$first": "$content"},
            "timestamp": {"$first": "$timestamp"}
        }},

        {"$sort": {"timestamp": -1}}
    ]

    return list(collection.aggregate(pipeline))


# ---------------- DELETE SESSION ----------------
def delete_session(user_email, session_id):
    collection = get_collection()

    collection.delete_many({
        "user_email": user_email,
        "session_id": session_id
    })


# ---------------- RENAME SESSION ----------------
def rename_session(user_email, session_id, new_name):
    collection = get_collection()

    collection.update_many(
        {"user_email": user_email, "session_id": session_id},
        {"$set": {"session_name": new_name}}
    )