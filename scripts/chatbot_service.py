"""
Chatbot Service - Xử lý logic AI chatbot cho ứng dụng danh mục đầu tư.
Sử dụng Google Gemini API (miễn phí)
"""

import pandas as pd
import google.generativeai as genai
from datetime import datetime
import streamlit as st


class PortfolioChatbot:
    """Lớp xử lý chatbot hỗ trợ tư vấn danh mục đầu tư"""
    
    def __init__(self, api_key):
        """
        Khởi tạo chatbot với Google Gemini API key
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Sử dụng Gemini 2.5 Flash - model ổn định và nhanh nhất
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.conversation_history = []
        
    def get_system_prompt(self, portfolio_data=None):
        """
        Tạo system prompt cho chatbot với thông tin về danh mục
        
        Args:
            portfolio_data (dict): Dữ liệu danh mục đầu tư hiện tại
            
        Returns:
            str: System prompt
        """
        base_prompt = """Bạn là một trợ lý AI chuyên về đầu tư chứng khoán Việt Nam. 
Nhiệm vụ của bạn là:
- Tư vấn về các chiến lược đầu tư và tối ưu hóa danh mục
- Giải thích các chỉ số tài chính như Sharpe Ratio, CVaR, CDaR, Volatility
- Phân tích rủi ro và lợi nhuận của danh mục
- Giúp người dùng hiểu rõ hơn về các mô hình tối ưu hóa (Markowitz, HRP, Max Sharpe, Min Volatility, Min CVaR, Min CDaR)
- Trả lời các câu hỏi về thị trường chứng khoán Việt Nam

Hãy trả lời ngắn gọn, dễ hiểu và thân thiện. Sử dụng tiếng Việt."""

        if portfolio_data:
            base_prompt += f"\n\nThông tin danh mục hiện tại:\n{portfolio_data}"
            
        return base_prompt
    
    def add_message_to_history(self, role, content):
        """
        Thêm tin nhắn vào lịch sử hội thoại
        
        Args:
            role (str): 'user' hoặc 'assistant'
            content (str): Nội dung tin nhắn
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        
        # Giới hạn lịch sử chỉ giữ 10 tin nhắn gần nhất để tránh vượt token limit
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def generate_response(self, user_message, portfolio_context=None):
        """
        Sinh câu trả lời từ chatbot sử dụng Google Gemini
        
        Args:
            user_message (str): Câu hỏi từ người dùng
            portfolio_context (dict): Thông tin context về danh mục
            
        Returns:
            str: Câu trả lời từ chatbot
        """
        try:
            # Thêm tin nhắn của user vào lịch sử
            self.add_message_to_history("user", user_message)
            
            # Tạo prompt đầy đủ với system prompt và context
            full_prompt = self.get_system_prompt(portfolio_context) + "\n\n"
            
            # Thêm lịch sử hội thoại
            for msg in self.conversation_history[-6:]:  # Chỉ lấy 6 tin nhắn gần nhất
                role_label = "Người dùng" if msg["role"] == "user" else "Trợ lý"
                full_prompt += f"{role_label}: {msg['content']}\n\n"
            
            # Gọi Google Gemini API
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 1024,
                }
            )
            
            # Kiểm tra response có hợp lệ không
            if not response or not response.parts:
                return "Xin lỗi, tôi không thể tạo câu trả lời lúc này. Vui lòng thử lại."
            
            # Kiểm tra response có bị block không
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                return f"Câu hỏi bị chặn do: {response.prompt_feedback.block_reason}"
            
            assistant_message = response.text
            
            # Thêm response vào lịch sử
            self.add_message_to_history("assistant", assistant_message)
            
            return assistant_message
            
        except AttributeError as e:
            # Lỗi khi response không có text
            return "Xin lỗi, không thể lấy câu trả lời. Vui lòng thử câu hỏi khác."
        except Exception as e:
            error_message = f"Xin lỗi, đã có lỗi xảy ra: {str(e)}"
            if "API" in str(e) or "key" in str(e).lower():
                error_message = "Vui lòng kiểm tra GEMINI_API_KEY trong file config.py"
            return error_message
    
    def clear_history(self):
        """Xóa lịch sử hội thoại"""
        self.conversation_history = []
    
    def get_portfolio_context(self, selected_stocks=None, optimization_result=None):
        """
        Tạo context về danh mục đầu tư hiện tại
        
        Args:
            selected_stocks (list): Danh sách mã cổ phiếu đã chọn
            optimization_result (dict): Kết quả tối ưu hóa danh mục
            
        Returns:
            str: Thông tin context dạng text
        """
        context_parts = []
        
        if selected_stocks:
            context_parts.append(f"Các cổ phiếu đang xem xét: {', '.join(selected_stocks)}")
        
        if optimization_result:
            if "Trọng số danh mục" in optimization_result:
                weights_str = ", ".join([f"{k}: {v:.2%}" for k, v in optimization_result["Trọng số danh mục"].items()])
                context_parts.append(f"Trọng số phân bổ: {weights_str}")
            
            if "Lợi nhuận kỳ vọng" in optimization_result:
                context_parts.append(f"Lợi nhuận kỳ vọng: {optimization_result['Lợi nhuận kỳ vọng']:.2%}")
            
            if "Rủi ro (Độ lệch chuẩn)" in optimization_result:
                context_parts.append(f"Rủi ro: {optimization_result['Rủi ro (Độ lệch chuẩn)']:.2%}")
            
            if "Tỷ lệ Sharpe" in optimization_result:
                context_parts.append(f"Sharpe Ratio: {optimization_result['Tỷ lệ Sharpe']:.4f}")
        
        return "\n".join(context_parts) if context_parts else None


def create_quick_question_buttons():
    """
    Tạo các nút câu hỏi nhanh cho người dùng
    
    Returns:
        list: Danh sách các câu hỏi nhanh
    """
    quick_questions = [
        "Giải thích mô hình Markowitz",
        "Làm sao để giảm rủi ro danh mục?",
        "Nên đa dạng hóa bao nhiêu cổ phiếu?",
    ]
    return quick_questions
