import requests
import asyncio
from typing import Dict, Any
from .config import settings
from .services.supabase_service import db
from .services.nlp_service import NLPCommandProcessor
from .services.chat_service import chat_service

# Initialize NLP Processor
nlp = NLPCommandProcessor()

async def send_message(chat_id: str, text: str):
    """Send message to Telegram user"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

async def process_update(data: Dict[str, Any]):
    """Process incoming Telegram update"""
    if 'message' not in data:
        return

    message = data['message']
    chat_id = str(message['chat']['id'])
    user_id = str(message['from']['id'])
    user_name = message['from'].get('first_name', 'Unknown')
    text = message.get('text', '')

    # 1. Save message to database
    await chat_service.save_message(
        source='telegram',
        user_id=user_id,
        user_name=user_name,
        message=text
    )

    # 2. Check if user is Admin
    is_admin = str(user_id) == settings.ADMIN_ID
    
    # 3. Process Command (Dual Mode)
    if is_admin:
        # --- ADMIN MODE: Execute Commands ---
        command_type, parsed_data = nlp.process_command(text)
        
        if command_type == "update_price":
            # Logic to update price in DB
            await send_message(chat_id, f"⚙️ جاري تحديث السعر... \n{parsed_data}")
            # Actual DB update logic would go here
            await send_message(chat_id, "✅ تم تحديث السعر بنجاح!")
            
        elif command_type == "add_unit":
            await send_message(chat_id, f"🏠 جاري إضافة الوحدة... \n{parsed_data}")
            # Actual DB insert logic
            await send_message(chat_id, "✅ تم إضافة الوحدة بنجاح!")
            
        elif command_type == "unknown":
            # If admin speaks normally, fall back to AI or just echo
            response = await ask_groq_ai(text, persona="admin_assistant")
            await send_message(chat_id, response)
            # Save bot response
            await chat_service.save_message(source='telegram', user_id=user_id, user_name="Bot", message=response, is_from_admin=True)

    else:
        # --- SALES MODE: Customer Support ---
        # 1. Check if user is asking for search
        command_type, parsed_data = nlp.process_command(text)
        
        if command_type == "search_units":
            # Perform DB search
            units = await db.get_units(status='available')
            # Filter logic (simplified)
            count = len(units)
            await send_message(chat_id, f"🔍 لقيت لك {count} وحدات متاحة تناسب طلبك.")
        else:
            # 2. General AI Chat (Groq)
            response = await ask_groq_ai(text, persona="sales_agent")
            await send_message(chat_id, response)
            # Save bot response
            await chat_service.save_message(source='telegram', user_id=user_id, user_name="Bot", message=response, is_from_admin=True)

async def ask_groq_ai(text: str, persona: str = "sales_agent") -> str:
    """Get response from Groq AI"""
    if not settings.GROQ_API_KEY:
        return "⚠️ عذراً، خدمة الذكاء الاصطناعي غير مفعلة حالياً."

    system_prompt = ""
    if persona == "sales_agent":
        system_prompt = """
        أنت "مساعد كيان برو" العقاري. شغلك تساعد العملاء يلاقوا وحدات في مشاريعنا (برج حمد، برج ليليان).
        - اتكلم مصري عامية ("يا فندم"، "من عينيا").
        - خليك مؤدب ومحترم جداً.
        - هدفك إنك تاخد رقم تليفون العميل عشان المبيعات يكلموه.
        """
    else:
        system_prompt = """
        أنت مساعد شخصي لمدير النظام.
        - نفذ الأوامر بدقة.
        - لو الأمر مش واضح، اطلب توضيح.
        """

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "عذراً، في مشكلة في الاتصال بالذكاء الاصطناعي."
    except Exception as e:
        return f"حدث خطأ: {str(e)}"
