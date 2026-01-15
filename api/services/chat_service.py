from typing import Dict, List, Optional
from datetime import datetime
from .supabase_service import db

class ChatService:
    """
    Unified chat management for Telegram and Website chats
    """
    
    @staticmethod
    async def save_message(source: str, user_id: str, user_name: str, message: str, is_from_admin: bool = False) -> Dict:
        """
        Save a chat message
        source: 'telegram' or 'website'
        """
        # Get existing chat or create new
        existing_chats = await db.get_chats(source=source)
        existing_chat = next((c for c in existing_chats if c['user_id'] == user_id), None)
        
        new_message = {
            'text': message,
            'timestamp': datetime.now().isoformat(),
            'from_admin': is_from_admin
        }
        
        if existing_chat:
            # Append to existing messages
            messages = existing_chat.get('messages', [])
            messages.append(new_message)
            
            chat_data = {
                'messages': messages,
                'updated_at': datetime.now().isoformat()
            }
            
            return await db.create_or_update_chat({
                **existing_chat,
                **chat_data
            })
        else:
            # Create new chat
            chat_data = {
                'source': source,
                'user_id': user_id,
                'user_name': user_name,
                'messages': [new_message],
                'status': 'active'
            }
            
            return await db.create_or_update_chat(chat_data)
    
    @staticmethod
    async def get_telegram_chats() -> List[Dict]:
        """Get all Telegram chats"""
        return await db.get_chats(source='telegram')
    
    @staticmethod
    async def get_website_chats() -> List[Dict]:
        """Get all website chats"""
        return await db.get_chats(source='website')
    
    @staticmethod
    async def get_all_active_chats() -> Dict[str, List[Dict]]:
        """Get all active chats grouped by source"""
        telegram_chats = await ChatService.get_telegram_chats()
        website_chats = await ChatService.get_website_chats()
        
        return {
            'telegram': telegram_chats,
            'website': website_chats
        }
    
    @staticmethod
    async def mark_as_read(chat_id: str) -> bool:
        """Mark chat as read"""
        chat = await db.get_chat(chat_id)
        if chat:
            await db.create_or_update_chat({
                **chat,
                'status': 'read',
                'updated_at': datetime.now().isoformat()
            })
            return True
        return False

# Singleton instance
chat_service = ChatService()
