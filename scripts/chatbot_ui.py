"""
Chatbot UI Component - Giao diện chatbox tích hợp vào dashboard.
"""

import streamlit as st
from scripts.chatbot_service import PortfolioChatbot, create_quick_question_buttons


def initialize_chatbot_session():
    """Khởi tạo session state cho chatbot"""
    if 'chatbot' not in st.session_state:
        try:
            from scripts.config import GEMINI_API_KEY
            
            # Kiểm tra API key có hợp lệ không
            if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key-here":
                st.session_state.chatbot = None
                st.session_state.chatbot_error = "Chưa cấu hình GEMINI_API_KEY trong config.py"
            else:
                st.session_state.chatbot = PortfolioChatbot(GEMINI_API_KEY)
                
        except (ImportError, AttributeError) as e:
            st.session_state.chatbot = None
            st.session_state.chatbot_error = f"Lỗi import: {str(e)}"
        except Exception as e:
            st.session_state.chatbot = None
            st.session_state.chatbot_error = f"Lỗi khởi tạo chatbot: {str(e)}"
    
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
        # Thêm tin nhắn chào mở đầu từ chatbot
        if st.session_state.chatbot is not None:
            welcome_message = """Xin chào! 👋 

Tôi là trợ lý AI của Portfolio Dashboard. Tôi có thể giúp bạn:
- Giải thích các chỉ số tài chính (Sharpe Ratio, volatility, return...)
- Tư vấn về chiến lược đầu tư và phân bổ danh mục
- Phân tích rủi ro và lợi nhuận
- Giải đáp các câu hỏi về tối ưu hóa danh mục

Hãy chọn câu hỏi gợi ý bên dưới hoặc đặt câu hỏi của bạn!"""
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": welcome_message
            })
    
    if 'show_quick_questions' not in st.session_state:
        st.session_state.show_quick_questions = True


def render_chatbot_sidebar(portfolio_context=None):
    """
    Render giao diện chatbot trong sidebar
    
    Args:
        portfolio_context (dict): Context về danh mục đầu tư hiện tại
    """
    # Khởi tạo chatbot session
    initialize_chatbot_session()
    
    # Tạo expander cho chatbot
    with st.sidebar.expander("Trợ lý AI", expanded=False):
        st.markdown("### Hỏi đáp với AI")
        st.markdown("Đặt câu hỏi về đầu tư, chiến lược, hoặc các chỉ số tài chính")
        
        # Kiểm tra lỗi cấu hình
        if st.session_state.chatbot is None:
            st.warning(st.session_state.get('chatbot_error', 'Lỗi khởi tạo chatbot'))
            st.info("Vui lòng thêm `GEMINI_API_KEY = 'your-api-key'` vào file scripts/config.py\n\nLấy API key miễn phí tại: https://makersuite.google.com/app/apikey")
            return
        
        # Container với chiều cao cố định và thanh cuộn
        chat_container = st.container(height=400)
        with chat_container:
            # Hiển thị lịch sử chat
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Hiển thị các câu hỏi gợi ý nếu có ít hơn 2 tin nhắn (chỉ có welcome message)
            if len(st.session_state.chat_messages) <= 1 and st.session_state.show_quick_questions:
                st.markdown("---")
                st.markdown("**Câu hỏi gợi ý:**")
                quick_questions = create_quick_question_buttons()
                
                for i, question in enumerate(quick_questions):
                    if st.button(question, key=f"quick_q_{i}", use_container_width=True):
                        handle_user_message(question, portfolio_context)
                        st.session_state.show_quick_questions = False
                        st.rerun()
        
        # Input chat
        user_input = st.chat_input("Nhập câu hỏi của bạn...")
        
        if user_input:
            handle_user_message(user_input, portfolio_context)
            st.session_state.show_quick_questions = False
            st.rerun()
        
        # Nút xóa lịch sử chat
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Xóa lịch sử", use_container_width=True):
                st.session_state.chat_messages = []
                st.session_state.chatbot.clear_history()
                st.session_state.show_quick_questions = True
                # Thêm lại tin nhắn chào
                welcome_message = """Xin chào! 

Tôi là trợ lý AI của Portfolio Dashboard. Tôi có thể giúp bạn:
- Giải thích các chỉ số tài chính (Sharpe Ratio, volatility, return...)
- Tư vấn về chiến lược đầu tư và phân bổ danh mục
- Phân tích rủi ro và lợi nhuận
- Giải đáp các câu hỏi về tối ưu hóa danh mục

Hãy chọn câu hỏi gợi ý bên dưới hoặc đặt câu hỏi của bạn!"""
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": welcome_message
                })
                st.rerun()
        
        with col2:
            if st.button("Hiện gợi ý", use_container_width=True):
                st.session_state.show_quick_questions = True
                st.rerun()


def handle_user_message(user_message, portfolio_context=None):
    """
    Xử lý tin nhắn từ người dùng
    
    Args:
        user_message (str): Tin nhắn từ người dùng
        portfolio_context (dict): Context về danh mục
    """
    # Thêm tin nhắn user vào chat
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Lấy context text nếu có
    context_text = None
    if portfolio_context:
        context_text = st.session_state.chatbot.get_portfolio_context(
            selected_stocks=portfolio_context.get('selected_stocks'),
            optimization_result=portfolio_context.get('optimization_result')
        )
    
    # Sinh response từ chatbot
    response = st.session_state.chatbot.generate_response(
        user_message, 
        context_text
    )
    
    # Thêm response vào chat
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": response
    })


def get_current_portfolio_context():
    """
    Lấy context về danh mục đầu tư hiện tại từ session state
    
    Returns:
        dict: Context về danh mục
    """
    context = {}
    
    # Lấy danh sách cổ phiếu đã chọn
    if 'manual_selected_stocks' in st.session_state and st.session_state.manual_selected_stocks:
        context['selected_stocks'] = st.session_state.manual_selected_stocks
    elif 'auto_selected_stocks' in st.session_state and st.session_state.auto_selected_stocks:
        context['selected_stocks'] = st.session_state.auto_selected_stocks
    
    # Có thể thêm optimization result nếu có trong session
    # context['optimization_result'] = st.session_state.get('last_optimization_result')
    
    return context if context else None
