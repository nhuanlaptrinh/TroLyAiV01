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
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the LLM - {str(e)}"

def extract_image_url(output):
    """Trích xuất URL hình ảnh từ chuỗi output sử dụng regex."""
    url_pattern = r'!\[.*?\]\((.*?)\)'  # Regex để tìm URL hình ảnh trong markdown (định dạng: ![alt](url))
    match = re.search(url_pattern, output)
    if match:
        return match.group(1)  # Trả về URL hình ảnh tìm được
    else:
        return None  # Nếu không tìm thấy URL hình ảnh

def extract_text(output):
    """Trích xuất văn bản từ chuỗi output (loại bỏ hình ảnh)"""
    # Loại bỏ tất cả các phần chứa hình ảnh
    text_only = re.sub(r'!\[.*?\]\(.*?\)', '', output)
    return text_only

def display_output(output):
    """Hiển thị văn bản và hình ảnh từ output"""
    # Trích xuất văn bản và hình ảnh
    text = extract_text(output)
    image_url = extract_image_url(output)
    # Nếu tìm thấy URL hình ảnh, hiển thị hình ảnh và cho phép bấm vào
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
    # CSS cho styling chat
    st.markdown("""
    <style>
    .user {
        
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .assistant {
        
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
        title_content = "Trợ lý AI"

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
        if message["role"] == "user":
            st.markdown(f'<div class="user">{message["content"]}</div>', unsafe_allow_html=True)
        elif message["role"] == "assistant":
            display_output(message["content"])

    # Ô nhập liệu cho người dùng
    if prompt := st.chat_input("Nhập nội dung cần trao đổi ở đây nhé?"):
        # Lưu tin nhắn của user vào session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Hiển thị tin nhắn user vừa gửi
        st.markdown(f'<div class="user">{prompt}</div>', unsafe_allow_html=True)

        # Gửi yêu cầu đến LLM và nhận phản hồi
        with st.spinner("Đang chờ phản hồi từ AI..."):
            llm_response = send_message_to_llm(st.session_state.session_id, prompt)

        # Lưu phản hồi của AI vào session state
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        
        # Hiển thị phản hồi của AI
        display_output(llm_response)

        # Rerun để cập nhật giao diện
        st.rerun()

if __name__ == "__main__":
    main()