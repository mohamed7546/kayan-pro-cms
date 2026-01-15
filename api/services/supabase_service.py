from supabase import create_client, Client
from typing import List, Dict, Optional
from ..config import settings

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    # ==================== PROJECTS ====================
    
    async def get_projects(self, status: Optional[str] = None) -> List[Dict]:
        """Get all projects, optionally filtered by status"""
        query = self.client.table('projects').select('*')
        if status:
            query = query.eq('status', status)
        response = query.execute()
        return response.data
    
    async def get_project(self, project_id: str) -> Optional[Dict]:
        """Get single project by ID"""
        response = self.client.table('projects').select('*').eq('id', project_id).execute()
        return response.data[0] if response.data else None
    
    async def create_project(self, project_data: Dict) -> Dict:
        """Create new project"""
        response = self.client.table('projects').insert(project_data).execute()
        return response.data[0]
    
    async def update_project(self, project_id: str, project_data: Dict) -> Dict:
        """Update existing project"""
        response = self.client.table('projects').update(project_data).eq('id', project_id).execute()
        return response.data[0]
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        self.client.table('projects').delete().eq('id', project_id).execute()
        return True
    
    # ==================== UNITS ====================
    
    async def get_units(self, project_id: Optional[str] = None, unit_type: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """Get units with optional filters"""
        query = self.client.table('units').select('*, projects(*)')
        if project_id:
            query = query.eq('project_id', project_id)
        if unit_type:
            query = query.eq('unit_type', unit_type)
        if status:
            query = query.eq('status', status)
        response = query.execute()
        return response.data
    
    async def get_unit(self, unit_id: str) -> Optional[Dict]:
        """Get single unit by ID"""
        response = self.client.table('units').select('*, projects(*)').eq('id', unit_id).execute()
        return response.data[0] if response.data else None
    
    async def create_unit(self, unit_data: Dict) -> Dict:
        """Create new unit"""
        response = self.client.table('units').insert(unit_data).execute()
        return response.data[0]
    
    async def update_unit(self, unit_id: str, unit_data: Dict) -> Dict:
        """Update existing unit"""
        response = self.client.table('units').update(unit_data).eq('id', unit_id).execute()
        return response.data[0]
    
    async def delete_unit(self, unit_id: str) -> bool:
        """Delete unit"""
        self.client.table('units').delete().eq('id', unit_id).execute()
        return True
    
    # ==================== PAGES ====================
    
    async def get_pages(self, published_only: bool = False) -> List[Dict]:
        """Get all pages"""
        query = self.client.table('pages').select('*')
        if published_only:
            query = query.eq('is_published', True)
        response = query.execute()
        return response.data
    
    async def get_page(self, slug: str) -> Optional[Dict]:
        """Get page by slug"""
        response = self.client.table('pages').select('*').eq('slug', slug).execute()
        return response.data[0] if response.data else None
    
    async def save_page(self, page_data: Dict) -> Dict:
        """Create or update page"""
        existing = await self.get_page(page_data['slug'])
        if existing:
            response = self.client.table('pages').update(page_data).eq('slug', page_data['slug']).execute()
        else:
            response = self.client.table('pages').insert(page_data).execute()
        return response.data[0]
    
    async def delete_page(self, page_id: str) -> bool:
        """Delete page"""
        self.client.table('pages').delete().eq('id', page_id).execute()
        return True
    
    # ==================== CONTENT BLOCKS ====================
    
    async def get_content_blocks(self, category: Optional[str] = None) -> List[Dict]:
        """Get content blocks"""
        query = self.client.table('content_blocks').select('*')
        if category:
            query = query.eq('category', category)
        response = query.execute()
        return response.data
    
    async def create_content_block(self, block_data: Dict) -> Dict:
        """Create new content block"""
        response = self.client.table('content_blocks').insert(block_data).execute()
        return response.data[0]
    
    # ==================== CHATS ====================
    
    async def get_chats(self, source: Optional[str] = None, status: str = 'active') -> List[Dict]:
        """Get chats"""
        query = self.client.table('chats').select('*').eq('status', status)
        if source:
            query = query.eq('source', source)
        response = query.order('updated_at', desc=True).execute()
        return response.data
    
    async def get_chat(self, chat_id: str) -> Optional[Dict]:
        """Get single chat"""
        response = self.client.table('chats').select('*').eq('id', chat_id).execute()
        return response.data[0] if response.data else None
    
    async def create_or_update_chat(self, chat_data: Dict) -> Dict:
        """Create or update chat"""
        # Check if chat exists by user_id and source
        existing = self.client.table('chats').select('*').eq('user_id', chat_data['user_id']).eq('source', chat_data['source']).execute()
        
        if existing.data:
            # Update existing chat
            response = self.client.table('chats').update(chat_data).eq('id', existing.data[0]['id']).execute()
        else:
            # Create new chat
            response = self.client.table('chats').insert(chat_data).execute()
        
        return response.data[0]
    
    # ==================== LEADS ====================
    
    async def get_leads(self, status: Optional[str] = None) -> List[Dict]:
        """Get leads"""
        query = self.client.table('leads').select('*, units(*, projects(*))')
        if status:
            query = query.eq('status', status)
        response = query.order('created_at', desc=True).execute()
        return response.data
    
    async def create_lead(self, lead_data: Dict) -> Dict:
        """Create new lead"""
        response = self.client.table('leads').insert(lead_data).execute()
        return response.data[0]
    
    async def update_lead(self, lead_id: str, lead_data: Dict) -> Dict:
        """Update lead"""
        response = self.client.table('leads').update(lead_data).eq('id', lead_id).execute()
        return response.data[0]
    
    # ==================== MEDIA ====================
    
    async def get_media(self, tags: Optional[List[str]] = None) -> List[Dict]:
        """Get media files"""
        query = self.client.table('media').select('*')
        if tags:
            query = query.contains('tags', tags)
        response = query.order('created_at', desc=True).execute()
        return response.data
    
    async def create_media(self, media_data: Dict) -> Dict:
        """Create media record"""
        response = self.client.table('media').insert(media_data).execute()
        return response.data[0]
    
    async def delete_media(self, media_id: str) -> bool:
        """Delete media"""
        self.client.table('media').delete().eq('id', media_id).execute()
        return True

# Singleton instance
db = SupabaseService()
