import streamlit as st
import requests
import uuid

# Hàm đọc nội dung từ file văn bản
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
            st.error(f"File {name_file} không tồn tại.")



# Constants

BEARER_TOKEN = st.secrets.get("BEARER_TOKEN")
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL")

def generate_session_id():
    return str(uuid.uuid4())

def send_message_to_llm(session_id, message):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print("Full response:", response_data)  # In ra toàn bộ dữ liệu trả về
        return response_data[0].get("output", "No output received")  # Trả về "output"
        # return response.json().get("output", "No output received")
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the LLM - {str(e)}"

def main():
    # Hiển thị logo (nếu có)
    try:
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            st.image("logo.png")
    except:
        pass
    # Hiển thị tiêu đề


    title_content = rfile("00.xinchao.txt")
    st.markdown(
        f"""<h1 style="text-align: center; font-size: 24px;">{title_content}</h1>""",
        unsafe_allow_html=True
    )

    # Khởi tạo session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    # CSS để căn chỉnh trợ lý bên trái, người hỏi bên phải, và thêm icon trợ lý
    st.markdown(
        """
        <style>
            .assistant {
                padding: 10px;
                border-radius: 10px;
                max-width: 75%;
                background: none; /* Màu trong suốt */
                text-align: left;
            }
            .user {
                padding: 10px;
                border-radius: 10px;
                max-width: 75%;
                background: none; /* Màu trong suốt */
                text-align: right;
                margin-left: auto;
            }
            .assistant::before { content: "🤖 "; font-weight: bold; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Hiển thị lịch sử tin nhắn
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.markdown(f'<div class="assistant">{message["content"]}</div>', unsafe_allow_html=True)
        elif message["role"] == "user":
            st.markdown(f'<div class="user">{message["content"]}</div>', unsafe_allow_html=True)

    # Ô nhập liệu cho người dùng
    if prompt := st.chat_input("Nhập nội dung cần trao đổi ở đây nhé?"):
        # Lưu tin nhắn người dùng
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user">{prompt}</div>', unsafe_allow_html=True)

        # Gửi yêu cầu đến LLM và nhận phản hồi
        with st.spinner("Đang chờ phản hồi từ AI..."):
            llm_response = send_message_to_llm(st.session_state.session_id, prompt)

        # Hiển thị và lưu phản hồi của trợ lý
        st.markdown(f'<div class="assistant">{llm_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": llm_response})

if __name__ == "__main__":
    main()