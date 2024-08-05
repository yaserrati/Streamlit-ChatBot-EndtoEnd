import streamlit as st

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

    response = f"MyTeam Bot: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
