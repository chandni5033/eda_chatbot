from langchain_openai import ChatOpenAI
import os
import re
from dotenv import load_dotenv
from db import get_schema_info, format_schema
from sqlalchemy import text
import pandas as pd


load_dotenv()


# ---------------- CLEAN SQL ----------------
def clean_sql(sql: str) -> str:
    sql = sql.replace("```sql", "").replace("```", "")
    sql = sql.replace("sql\n", "").strip()
    sql = sql.replace("\n", " ")
    sql = re.sub(r"\s+", " ", sql)
    return sql.strip()


# ---------------- LIMIT CONTROL ----------------
def enforce_limit(sql: str) -> str:
    if "select" in sql.lower() and "limit" not in sql.lower():
        if not any(k in sql.lower() for k in ["count(", "sum(", "avg(", "min(", "max("]):
            sql += " LIMIT 50"
    return sql


# ---------------- MAIN ----------------
def query_database_with_sql(question: str, db=None):

    llm = ChatOpenAI(
        model="meta/llama-3.3-70b-instruct",
        openai_api_key=os.getenv("NVIDIA_API_KEY"),
        openai_api_base="https://integrate.api.nvidia.com/v1",
        temperature=0,
        max_tokens=500,
    )

    # 🔥 Get DB name
    try:
        db_name = db._engine.url.database
    except:
        db_name = "your_database"

    # 🔥 GET SCHEMA
    schema = get_schema_info(db)
    schema_text = format_schema(schema)

    # 🔥 PROMPT WITH SCHEMA
    prompt = f"""
You are a SQL expert.

Database: {db_name}

SCHEMA:
{schema_text}

STRICT RULES:
- Use ONLY tables and columns from schema
- Do NOT invent columns (like emp_id if not present)
- Return ONLY SQL
- No explanation
- No markdown

RULES:
- Use COUNT(*) when unsure
- Use DISTINCT for unique values
- Use LEFT(column, 3) for substring
- Avoid SELECT *
- Use LIMIT only for listing

Example:
Q: departments with less than 4 people  
A: SELECT DEPARTMENT FROM worker GROUP BY DEPARTMENT HAVING COUNT(*) < 4;

Now generate SQL:

{question}
"""

    response = llm.invoke(prompt)

    sql = clean_sql(response.content)

    # ❌ FAIL SAFE
    if not sql.lower().startswith("select"):
        return "❌ SQL generation failed", ""

    # 🔥 LIMIT SAFETY
    sql = enforce_limit(sql)

    # 🔥 EXECUTE
    try:
        engine = db._engine

        with engine.connect() as conn:
            result = conn.execute(text(sql))

            rows = result.fetchall()
            columns = result.keys()

            df = pd.DataFrame(rows, columns=columns)

        return df.to_dict(orient="records"), sql

    except Exception as e:
        return f"SQL Error: {e}", sql