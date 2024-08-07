import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import pandas as pd
import pandasql as ps
import re
import json



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

def prompt_gemmi():
    
    start_prompt =""""
        You are an expert in converting natural language questions into SQL queries. 
        The SQL database schema is provided below:
        Table: players
        Columns:
            - Name (TEXT)
            - Age (INTEGER)
            - Position (TEXT)
            - Nationality (TEXT)
            - Matches_Played (INTEGER)
            - Goals_Scored (INTEGER)
            - Assists (INTEGER)
            - Yellow_Cards (INTEGER)
            - Red_Cards (INTEGER)
            - Height_CM (INTEGER)
            - Weight_KG (INTEGER)
        It is important that the column names used in your SQL query match exactly with the column names in the schema. 
        Ensure that any aliases you use for columns in the SQL query also correctly match the schema names or are clearly defined.
        Here are some examples:
        Question: List all players
        SQL Query: SELECT * FROM players;
        Question: What are the names and ages of players who scored more than 20 goals?
        SQL Query: SELECT Name, Age FROM players WHERE Goals_Scored > 20;
        Question: Find the player with the highest number of assists
        SQL Query: SELECT Name, Assists FROM players ORDER BY Assists DESC LIMIT 1;
        Question: Which players are taller than 180 cm and weigh less than 80 kg?
        SQL Query: SELECT Name FROM players WHERE Height_CM > 180 AND Weight_KG < 80;
        Question: What is the BMI of players?
        SQL Query: SELECT Weight_KG / ((Height_CM / 100.0) * (Height_CM / 100.0)) AS BMI FROM players;
        Guidelines:
        1. Ensure the SQL code is syntactically correct and does not include delimiters like `;`.
        2. Avoid SQL keywords or delimiters in the output.
        3. Handle different variations of questions accurately.
        4. The SQL code should be valid, executable, and not contain unnecessary delimiters.
        """
    return start_prompt


# -------------------------------------------------------------------------------------------------------
def generate_conversational_response(question):
    # Exemple de génération de réponse conversationnelle
    custom_prompt = f"""
    You are an assistant that responds to basic conversational queries in a friendly and helpful manner.
    If a user greets you or asks how you are, respond with a polite and friendly reply.
    If the user asks for specific information, a specific topic, a question, or an order, respond with 
    "I am here to chat with you, but I do not have the information you are looking for."
    
    Example interactions:
    User: "Hey"
    Assistant: "Hello! How can I help you today?"

    User: "How are you?"
    Assistant: "I'm doing well, thank you! How can I assist you today?"

    User: "Can you help me?"
    Assistant: "Of course! What do you need help with?"

    User: "Tell me about the latest news."
    Assistant: "I am here to chat with you, but I do not have the information you are looking for."

    User: "What's the weather like?"
    Assistant: "I am here to chat with you, but I do not have the information you are looking for."

    User: "Order a pizza for me."
    Assistant: "I am here to chat with you, but I do not have the information you are looking for."

    User: "Tell me a joke."
    Assistant: "I am here to chat with you, but I do not have the information you are looking for."

    User: "Can you tell me about Python programming?"
    Assistant: "I am here to chat with you, but I do not have the information you are looking for."

    Now, respond to the following question:
    User: {question}
    Assistant:
    """
    sql_query = get_gemini_response(custom_prompt.format(question=question), "")
    return sql_query

# # -----------------------------------------
# def load_interactions(json_file):
#     with open(json_file, 'r') as file:
#         data = json.load(file)
#     return data["interactions"]

# def generate_conversational_response(question, interactions_file='interactions.json'):
#     interactions = load_interactions(interactions_file)
    
#     example_interactions = ""
#     for interaction in interactions:
#         example_interactions += f"""
#     User: "{interaction['User']}"
#     Assistant: "{interaction['Assistant']}"
#     """
    
#     custom_prompt = f"""
#     You are an assistant that responds to basic conversational queries in a friendly and helpful manner.
#     If a user greets you or asks how you are, respond with a polite and friendly reply.
#     If the user asks for specific information, a specific topic, a question, or an order, respond with 
#     "I am here to chat with you, but I do not have the information you are looking for."

#     Example interactions:{example_interactions}

#     Now, respond to the following question:
#     User: {question}
#     Assistant:
#     """
    
#     # Assuming get_gemini_response is a function you have that takes the prompt and question and returns a response
#     response = get_gemini_response(custom_prompt, question)
#     return response
# # -----------------------------------------------
    

def respond_to_question(question, dataframe, prompt):
    related_keywords = ['players', 'name', 'age', 'position', 'nationality',
                        'matches played', 'goals scored', 'assists',
                        'yellow cards', 'red cards', 'height', 'weight', 'goalkeeper ','BMI', 'player']

    # Vérifier si la question est liée à la base de données
    if any(keyword in question.lower() for keyword in related_keywords):
        # Générer la requête SQL
        sql_query = get_gemini_response(prompt, question)
        sql_query = sql_query.strip('"')

        # Vérifier que la requête contient "SELECT"
        if "SELECT" in sql_query.upper():
            try:
                # Passer le DataFrame avec le nom de la table correct
                result = ps.sqldf(sql_query, {'players': dataframe})
                return result, 'dataframe'
            except Exception as e:
                return f"no result found: {e}", 'error'
        else:
            return "Generated SQL query is not a valid SELECT statement.", 'error'
    else:
        # Générer une réponse conversationnelle
        response = generate_conversational_response(question)
        return response, 'text'
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

players=pd.read_csv("football_players_n.csv")
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
# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    response, response_type = respond_to_question(prompt, players, prompt_gemmi())
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        if response_type == 'dataframe':
            st.dataframe(response)  # Display the DataFrame
        else:
            st.markdown(response)  # Display the text response
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": str(response)})