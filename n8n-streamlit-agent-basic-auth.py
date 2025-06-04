import streamlit as st
import requests
import uuid
import re
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




# # Khởi tạo tin nhắn "system" và "assistant"
# INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
# INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

# if "messages" not in st.session_state:
#     st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]



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
        content = response_data.get("content", "No output received")
        image_url = response_data.get('url', None)
        return content, image_url  # Return both content and image URL
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the LLM - {str(e)}", None

def extract_text(output):
    """Trích xuất văn bản từ chuỗi output (loại bỏ hình ảnh)"""
    # Loại bỏ tất cả các phần chứa hình ảnh
    text_only = re.sub(r'!\[.*?\]\(.*?\)', '', output)
    return text_only

def display_output(text, image_url):
    """Hiển thị văn bản và hình ảnh từ output"""
    # Trích xuất văn bản và hình ảnh
    print("Extracted image URL:", image_url)  # In ra URL hình ảnh đã trích xuất    
    if image_url:
        st.markdown(
            f"""
            <a href="{image_url}" target="_blank">
                <img src="{image_url}" alt="Biểu đồ SBUX" style="width: 100%; height: auto;">
            </a>
            """,
            unsafe_allow_html=True
        )

    
    # Hiển thị văn bản phân tích
    st.markdown(text, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Trợ lý AI", page_icon="🤖", layout="centered")
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
    # Hiển thị logo (nếu có)
    try:
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            st.image("logo.png")
    except:
        pass
    
    # Đọc nội dung tiêu đề từ file
    try:
        with open("00.xinchao.txt", "r", encoding="utf-8") as file:
            title_content = file.read()
    except Exception as e:
        title_content = "Lỗi đọc tiêu đề"

    print("title_content:", title_content)
    st.markdown(
        f"""<h1 style="text-align: center; font-size: 24px;">{title_content}</h1>""",
        unsafe_allow_html=True
    )

    # Khởi tạo session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    # Hiển thị lịch sử tin nhắn
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.markdown(f'<div class="assistant">{message["content"]}</div>', unsafe_allow_html=True)
        elif message["role"] == "user":
            st.markdown(f'<div class="user">{message["content"]}</div>', unsafe_allow_html=True)

    # Ô nhập liệu cho người dùng
    if prompt := st.chat_input("Nhập nội dung cần trao đổi ở đây nhé?"):
        # Gửi yêu cầu đến LLM và nhận phản hồi
        with st.spinner("Đang chờ phản hồi từ AI..."):
            llm_response, image_url = send_message_to_llm(st.session_state.session_id, prompt)
            print("LLM response:", llm_response)
    
        # Kiểm tra nếu phản hồi không phải lỗi và hiển thị phân tích kỹ thuật và hình ảnh (nếu có)
        if isinstance(llm_response, str) and "Error" in llm_response:
            st.error(llm_response)
        else:
            display_output(llm_response, image_url)

if __name__ == "__main__":
    main()