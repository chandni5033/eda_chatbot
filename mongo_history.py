from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def get_collection():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["eda_chatbot"]
    return db["chat_history"]


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


def load_messages(user_email, session_id):
    collection = get_collection()

    return list(collection.find(
        {"user_email": user_email, "session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1))


def get_all_sessions(user_email):
    collection = get_collection()

    pipeline = [
        {"$match": {"user_email": user_email}},
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$session_id",
            "session_name": {"$first": "$session_name"},
            "timestamp": {"$first": "$timestamp"}
        }},
        {"$sort": {"timestamp": -1}}
    ]

    return list(collection.aggregate(pipeline))


def delete_session(user_email, session_id):
    collection = get_collection()
    collection.delete_many({
        "user_email": user_email,
        "session_id": session_id
    })