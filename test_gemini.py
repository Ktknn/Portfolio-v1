"""
Test chatbot với Google Gemini API
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from scripts.chatbot_service import PortfolioChatbot
    from scripts.config import GEMINI_API_KEY
    
    print("=" * 60)
    print("TEST CHATBOT VỚI GOOGLE GEMINI")
    print("=" * 60)
    
    # Kiểm tra API key
    if GEMINI_API_KEY == "your-gemini-api-key-here":
        print("\n⚠️  Chưa cấu hình GEMINI_API_KEY!")
        print("Vui lòng:")
        print("1. Truy cập: https://makersuite.google.com/app/apikey")
        print("2. Tạo API key miễn phí")
        print("3. Cập nhật vào file scripts/config.py")
        sys.exit(1)
    
    print("\n✅ API key đã được cấu hình")
    print("🔄 Đang khởi tạo chatbot với Google Gemini...")
    
    # Khởi tạo chatbot
    chatbot = PortfolioChatbot(GEMINI_API_KEY)
    print("✅ Chatbot đã sẵn sàng!\n")
    
    # Test với một câu hỏi đơn giản
    question = "Sharpe Ratio là gì? Giải thích ngắn gọn bằng tiếng Việt."
    print(f"🙋 Câu hỏi: {question}")
    print("-" * 60)
    
    response = chatbot.generate_response(question)
    print(f"🤖 Trả lời:\n{response}")
    print("-" * 60)
    
    print("\n✅ Test thành công! Chatbot với Google Gemini hoạt động bình thường.")
    print("💡 Bây giờ bạn có thể chạy: streamlit run scripts/dashboard.py")
    print("\n🎉 Lưu ý: Google Gemini MIỄN PHÍ và không giới hạn!")
    
except Exception as e:
    print(f"\n❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()
