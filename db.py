from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def get_db(host=None, user=None, password=None, name=None):
    host = host or os.getenv("DB_HOST")
    user = user or os.getenv("DB_USER")
    password = password or os.getenv("DB_PASSWORD")
    name = name or os.getenv("DB_NAME")
    url = f"mysql+pymysql://{user}:{password}@{host}/{name}"
    engine = create_engine(url)
    return SQLDatabase(engine)


def get_schema_info(db):
    raw_tables = db.run("SHOW TABLES;")

    
    import ast
    try:
        tables = ast.literal_eval(raw_tables)
    except:
        tables = raw_tables

    schema = {}

    for t in tables:

        
        if isinstance(t, (list, tuple)):
            table_name = t[0]
        elif isinstance(t, dict):
            table_name = list(t.values())[0]
        else:
            table_name = str(t)

        if not table_name:
            continue

        
        raw_cols = db.run(f"SHOW COLUMNS FROM {table_name};")

        try:
            cols = ast.literal_eval(raw_cols)
        except:
            cols = raw_cols

        schema[table_name] = []

        for col in cols:
            if isinstance(col, dict):
                schema[table_name].append(col.get("Field"))
            elif isinstance(col, (list, tuple)):
                schema[table_name].append(col[0])
            else:
                schema[table_name].append(str(col))

    return schema

def format_schema(schema: dict) -> str:
    text = ""

    for table, cols in schema.items():
        text += f"\nTable: {table}\nColumns: {', '.join(cols)}\n"

    return text