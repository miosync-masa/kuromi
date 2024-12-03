import os
import streamlit as st
import openai
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit ページ設定
st.set_page_config(page_title="Advanced Chat with Miosync", page_icon="💬", layout="wide")

# タイトルと説明
st.title("💬 Advanced Chat with miosync")
st.write("Chat with an AI assistant. You can customize the model and system behavior.")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "chatgpt-4o-latest"

if "system_message" not in st.session_state:
    st.session_state.system_message = "You are a helpful assistant."

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "top_p" not in st.session_state:
    st.session_state.top_p = 1.0

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 1000  # デフォルトのトークン数

# 履歴の長さ制限
MAX_HISTORY_LENGTH = 15

def trim_message_history():
    """
    履歴が長すぎる場合、古いメッセージを削除
    """
    if len(st.session_state.messages) > MAX_HISTORY_LENGTH:
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY_LENGTH:]

# チャット履歴を表示するための Message Placeholder
message_placeholder = st.empty()

def update_chat_history():
    """
    チャット履歴を Message Placeholder に表示
    """
    with message_placeholder.container():
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            elif msg["role"] == "assistant":
                st.markdown(f"**クロミ:** {msg['content']}")

def generate_response(user_input):
    """
    OpenAI APIを使用して応答を生成
    """
    # ユーザーの発言を履歴に追加
    st.session_state.messages.append({"role": "user", "content": user_input})
    trim_message_history()

    # チャット履歴を更新
    update_chat_history()

    try:
        # OpenAI API にメッセージ履歴を送信
        response = openai.ChatCompletion.create(
            model=st.session_state.selected_model,
            messages=st.session_state.messages,
            temperature=st.session_state.temperature,
            top_p=st.session_state.top_p,
            max_tokens=st.session_state.max_tokens,
        )
        # AIの応答を履歴に追加
        reply = response.choices[0].message["content"]
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # チャット履歴を更新
        update_chat_history()

    except Exception as e:
        st.error(f"An error occurred: {e}")

# サイドバー設定
st.sidebar.title("Settings")
st.sidebar.subheader("Model Configuration")
st.session_state.selected_model = st.sidebar.selectbox(
    "Choose a model:",
    ["gpt-4o", "gpt-4o-mini", "chatgpt-4o-latest"],
    index=["gpt-4o", "gpt-4o-mini", "chatgpt-4o-latest"].index(st.session_state.selected_model)
)

st.sidebar.subheader("System Message")
st.session_state.system_message = st.sidebar.text_area(
    "Set the system's behavior message:",
    st.session_state.system_message
)

# サイドバーで温度、Top-p、Max tokens を調整
st.sidebar.subheader("Generation Parameters")
st.session_state.temperature = st.sidebar.slider(
    "Temperature (Creativity)", min_value=0.0, max_value=1.0, value=st.session_state.temperature, step=0.01
)
st.session_state.top_p = st.sidebar.slider(
    "Top-p (Sampling)", min_value=0.0, max_value=1.0, value=st.session_state.top_p, step=0.01
)
st.session_state.max_tokens = st.sidebar.slider(
    "Max Tokens (Response Length)", min_value=100, max_value=12096, value=st.session_state.max_tokens, step=100
)

# システムメッセージを再設定
st.session_state.messages[0]["content"] = st.session_state.system_message

# チャット履歴を更新して表示
update_chat_history()

# 入力フォーム
with st.form(key="chat_form"):
    user_input = st.text_input("Your message:", "")
    submit_button = st.form_submit_button("Send")

    if submit_button and user_input.strip():
        generate_response(user_input)

# セッション履歴のリセット
if st.button("Reset Chat"):
    st.session_state.messages = [
        {"role": "system", "content": st.session_state.system_message}
    ]
    st.success("Chat history reset.")
    update_chat_history()
