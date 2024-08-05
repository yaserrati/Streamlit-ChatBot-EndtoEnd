import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import pandas as pd
# -------------------------------------------------------------------------------------------------------
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Genai Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Google Gemini Model
model = genai.GenerativeModel('gemini-pro')

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(prompt, question):
    try:
        response = model.generate_content([prompt, question])
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return None
def sanitize_sql(sql):
    # Basic sanitization to ensure there are no malicious inputs
    # This can be enhanced based on specific requirements
    sql = sql.strip().strip(';')
    return sql

# Define your prompt for SQL generation
sql_prompt = """
You are an expert in converting English questions to SQL queries!
The SQL database has the following views:
1. `view_player` with the columns:
   - player_id (INTEGER PRIMARY KEY AUTOINCREMENT)
   - first_name (TEXT)
   - last_name (TEXT)
   - position (TEXT)
   - team_id (INTEGER)
   - age (INTEGER)
   - nationality (TEXT)
   - goals (INTEGER)

2. `view_team` with the columns:
   - team_id (INTEGER PRIMARY KEY AUTOINCREMENT)
   - team_name (TEXT)
   - title (INTEGER)

For example:
Example 1 - How many players are there?,
the SQL command will be something like this:
SELECT COUNT(*) FROM view_player;

Example 2 - List all players in the team 'Barcelona',
the SQL command will be something like this:
SELECT first_name, last_name 
FROM view_player p
JOIN view_team t ON p.team_id = t.team_id
WHERE t.team_name = 'Barcelona';

Example 3 - What are the titles of all teams?,
the SQL command will be something like this:
SELECT team_name, title_count 
FROM view_team;

Example 4 - List all players and their teams,
the SQL command will be something like this:
SELECT p.first_name, p.last_name, t.team_name
FROM view_player p
JOIN view_team t ON p.team_id = t.team_id;

Guidelines:
1. Ensure the SQL code is syntactically correct and does not include delimiters like `;`.
2. Avoid SQL keywords or delimiters in the output.
3. Handle different variations of questions accurately.
4. The SQL code should be valid, executable, and not contain unnecessary delimiters.

Schema:
- View: view_player
  Columns: player_id INTEGER PRIMARY KEY AUTOINCREMENT,
           first_name TEXT,
           last_name TEXT,
           position TEXT,
           team_id INTEGER,
           age INTEGER,
           nationality TEXT,
           goals INTEGER

- View: view_team
  Columns: team_id INTEGER PRIMARY KEY AUTOINCREMENT,
           team_name TEXT,
           title_count INTEGER
"""
# -------------------------------------------------------------------------------------------------------


# Set page configuration
st.set_page_config(
    page_title="MyTeam Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .css-1aumxhk {
        background-color: #262730;
        border: 1px solid #1f77b4;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .css-1aumxhk h4 {
        color: #1f77b4;
    }
    .css-1aumxhk p {
        color: #fafafa;
    }
    .css-1aumxhk input {
        background-color: #0e1117;
        color: #fafafa;
        border: 1px solid #1f77b4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title of the app
st.title("MyTeam Bot 🤖")

# Sidebar for additional options
with st.sidebar:
    st.header("Settings")
    st.markdown("Adjust the settings for MyTeam Bot.")
    st.slider("Response Speed", 0.1, 10.0, 5.0)
    st.radio("Select Theme", ["Light - doesnt activate right now ", "Dark"], index=1)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    sql_query = get_gemini_response(sql_prompt, prompt)
    response = f"MyTeam Bot: {sql_query}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
