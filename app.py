import gradio as gr
import requests
import os
from dotenv import load_dotenv
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
token = None  # Global variable to store token
# Store session messages here as list of tuples (sender, text)
session_messages = []

def register_user(username, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/register",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return "Registration successful! You can now log in."
        else:
            return f"Registration failed: {response.json().get('detail')}"
    except Exception as e:
        return f"Error during registration: {str(e)}"

'''def login_user(username, password):
    global token
    try:
        response = requests.post(
            f"{BACKEND_URL}/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            session_messages = []  # Clear previous session messages on new login
            return "Login successful! You can now chat with the bot."
        else:
            return f"Login failed: {response.json().get('detail')}"
    except Exception as e:
        return f"Error during login: {str(e)}"
'''
def login_user(username, password):
    global token, session_messages
    try:
        response = requests.post(
            f"{BACKEND_URL}/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            session_messages = []  # Clear previous session messages on new login
            return "Login successful! You can now chat with the bot.", []
        else:
            return f"Login failed: {response.json().get('detail')}", []
    except Exception as e:
        return f"Error during login: {str(e)}", []
    
def load_chat_history():
    global token
    if not token:
        return "Error: You must login first."

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BACKEND_URL}/chat/", headers=headers)
        if response.status_code == 200:
            history = response.json()
            formatted = "\n".join([f"{msg['sender'].capitalize()}: {msg['text']}" for msg in history])
            return formatted
        else:
            return f"Failed to load history: {response.text}"
    except Exception as e:
        return f"Error loading chat history: {str(e)}"


'''def chat_with_bot(user_input):
    global token
    if not token:
        return "Error: You must login first."

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": user_input},
            headers=headers
        )

        if response.status_code == 200:
            return response.json().get("response", "No response from bot.")
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error connecting to chatbot: {e}"
    '''

def chat_with_bot(user_input):
    global token, session_messages
    if not token:
        return "Error: You must login first.", session_messages

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": user_input},
            headers=headers
        )
        if response.status_code == 200:
            bot_response = response.json().get("response", "No response from bot.")
            # Add user and bot messages to session history
            session_messages.append(("User", user_input))
            session_messages.append(("Bot", bot_response))
            return "", session_messages  # Clear input box and update chat display
        else:
            return f"Error {response.status_code}: {response.text}", session_messages
    except Exception as e:
        return f"Error connecting to chatbot: {e}", session_messages

def new_chat():
    global session_messages
    session_messages = []  # Clear session messages
    return session_messages



def upload_and_ask(file, question):
    global token
    if not token:
        return "Error: Please login first."

    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (file.name, open(file.name, "rb"))}
    data = {"question": question}

    try:
        response = requests.post(
            f"{BACKEND_URL}/ask-from-file",
            headers=headers,
            files=files,
            data=data
        )
        if response.status_code == 200:
            return response.json().get("response", "No response from bot.")
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error connecting to chatbot: {e}"
    
def logout_user():
    global token
    token = None
    return "You have been logged out."


def clear_history():
    global token
    if not token:
        return "Error: You must login first."
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(f"{BACKEND_URL}/chat/clear", headers=headers)
        if response.status_code == 200:
            return response.json().get("message")
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error clearing history: {str(e)}"



with gr.Blocks() as demo:
    gr.Markdown("# Mistral Chatbot - Register or Login")

    with gr.Tab("Register"):
        username_register = gr.Textbox(label="New Username")
        password_register = gr.Textbox(label="New Password", type="password")
        register_btn = gr.Button("Register")
        register_output = gr.Textbox(label="Registration Message", interactive=False)

        def register_and_clear(username, password):
            msg = register_user(username, password)
            return "", "", msg

        register_btn.click(
            fn=register_and_clear,
            inputs=[username_register, password_register],
            outputs=[username_register, password_register, register_output]
        )

    with gr.Tab("Login"):
        username_login = gr.Textbox(label="Username")
        password_login = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login")
        login_output = gr.Textbox(label="Login Message", interactive=False)

        def login_and_clear(username, password):
            msg = login_user(username, password)
            return "", "", msg

        login_btn.click(
            fn=login_and_clear,
            inputs=[username_login, password_login],
            outputs=[username_login, password_login, login_output]
        )
 
    '''chatbot_input = gr.Textbox(placeholder="Type your message here...")
    chatbot_output = gr.Textbox(label="Bot Response", interactive=False)
    chat_button = gr.Button("Send")
    chat_button.click(fn=chat_with_bot, inputs=chatbot_input, outputs=chatbot_output)'''

    chatbot_display = gr.Chatbot(label="Chatbot", height=400)
    chatbot_input = gr.Textbox(placeholder="Type your message here...")
    chat_button = gr.Button("Send")

    chat_button.click(
    fn=chat_with_bot,
    inputs=chatbot_input,
    outputs=[chatbot_input, chatbot_display]
    )
    
    new_chat_button = gr.Button("🆕 New Chat")
    new_chat_button.click(
    fn=new_chat,
    outputs=chatbot_display
    )


    chat_history_output = gr.Textbox(label="Chat History", lines=10, interactive=False)
    load_history_button = gr.Button("Load Chat History")
    load_history_button.click(fn=load_chat_history, outputs=chat_history_output)
    
    gr.Markdown("## 📄 Upload a file and ask a question about it")
    file_input = gr.File(label="Upload Document")
    file_question = gr.Textbox(label="Your Question About the Document")
    file_output = gr.Textbox(label="Answer")

    ask_file_btn = gr.Button("Ask from File")
    ask_file_btn.click(fn=upload_and_ask, inputs=[file_input, file_question], outputs=file_output)

    logout_button = gr.Button("Logout")
    logout_message = gr.Textbox(label="Logout Message", interactive=False)
    logout_button.click(fn=logout_user, outputs=logout_message)

    clear_button = gr.Button("Clear Chat History")
    clear_message = gr.Textbox(label="Clear Status", interactive=False)
    clear_button.click(fn=clear_history, outputs=clear_message)

demo.launch()
