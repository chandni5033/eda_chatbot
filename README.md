# 📊 AI-Powered EDA Chatbot

An intelligent chatbot that converts natural language queries into SQL, executes them on a live MySQL database, and returns structured results with optional visualizations.

---

##  Features

- Natural Language → SQL conversion using LLM  
- Schema-aware query generation (avoids invalid columns)  
- Google OAuth authentication  
- Multi-user support with session-based chat history  
- Chat sessions with auto-naming and deletion  
- MySQL database integration  
- Data visualization using Matplotlib  
- Handles large datasets safely using query limiting (LIMIT)  

---

## Architecture

User → Streamlit UI  
→ LLM (SQL generation)  
→ MySQL (query execution)  
→ Results (table + visualization)  
→ MongoDB (chat history storage)

---

## Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **Database**: MySQL  
- **Chat Storage**: MongoDB  
- **LLM**: LLaMA 3.3 (via NVIDIA API)  
- **Libraries**: LangChain, SQLAlchemy, Pandas, Matplotlib  

---

## Key Concepts Used

- Prompt Engineering  
- Schema Awareness  
- SQL Query Generation  
- Multi-user Session Management  
- API Integration  
- Data Visualization  

---

## Setup

```bash
git clone https://github.com/your-username/eda-chatbot.git
cd eda-chatbot

python -m venv eda_env

# Activate environment:
# Windows:
eda_env\Scripts\activate

# Mac/Linux:
source eda_env/bin/activate

pip install -r requirements.txt

# Create a .env file
add these
NVIDIA_API_KEY=your_api_key
MONGO_URI=your_mongodb_uri
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# run the application
streamlit run app.py

```

