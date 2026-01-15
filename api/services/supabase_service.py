from supabase import create_client, Client
from typing import List, Dict, Optional
import requests
import json
from ..config import settings

class SupabaseService:
    def __init__(self):
        self.use_jsonbin = False
        try:
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                self.client: Client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
            else:
                print("⚠️ Supabase credentials missing. Switching to JSONBin Fallback.")
                self.use_jsonbin = True
        except:
            self.use_jsonbin = True
            
        # JSONBin Config
        self.bin_url = f"https://api.jsonbin.io/v3/b/{settings.JSONBIN_ID}"
        self.headers = {
            "Content-Type": "application/json",
            "X-Master-Key": settings.JSONBIN_KEY,
            "X-Bin-Meta": "false"
        }

    # ==================== JSONBIN HELPERS ====================
    def _jb_read(self) -> Dict:
        try:
            r = requests.get(self.bin_url, headers=self.headers)
            return r.json() if r.status_code == 200 else {}
        except: return {}

    def _jb_write(self, data: Dict):
        try:
            requests.put(self.bin_url, headers=self.headers, json=data)
        except Exception as e: print(f"JSONBin Write Error: {e}")

    def _jb_get_collection(self, collection_name: str) -> List[Dict]:
        data = self._jb_read()
        return data.get(collection_name, [])

    def _jb_save_item(self, collection_name: str, item: Dict, id_field='id'):
        data = self._jb_read()
        if collection_name not in data: data[collection_name] = []
        
        # Check update or insert
        idx = next((i for i, x in enumerate(data[collection_name]) if x.get(id_field) == item.get(id_field)), -1)
        if idx >= 0:
            data[collection_name][idx] = {**data[collection_name][idx], **item}
        else:
            data[collection_name].append(item)
            
        self._jb_write(data)
        return item

    # ==================== PAGES ====================
    
    async def get_pages(self, published_only: bool = False) -> List[Dict]:
        if self.use_jsonbin:
            pages = self._jb_get_collection('pages')
            if published_only:
                pages = [p for p in pages if p.get('is_published')]
            return pages
            
        query = self.client.table('pages').select('*')
        if published_only:
            query = query.eq('is_published', True)
        response = query.execute()
        return response.data
    
    async def get_page(self, slug: str) -> Optional[Dict]:
        if self.use_jsonbin:
            pages = self._jb_get_collection('pages')
            return next((p for p in pages if p['slug'] == slug), None)

        response = self.client.table('pages').select('*').eq('slug', slug).execute()
        return response.data[0] if response.data else None
    
    async def save_page(self, page_data: Dict) -> Dict:
        if self.use_jsonbin:
            return self._jb_save_item('pages', page_data, id_field='slug')

        existing = await self.get_page(page_data['slug'])
        if existing:
            response = self.client.table('pages').update(page_data).eq('slug', page_data['slug']).execute()
        else:
            response = self.client.table('pages').insert(page_data).execute()
        return response.data[0]
    
    # ==================== PROJECTS & UNITS (Fallback Support) ====================
    async def get_units(self, status: Optional[str] = None) -> List[Dict]:
        if self.use_jsonbin:
            # Original JSONBin structure might be slightly different ('projects' -> 'units')
            # But let's assume we store 'units' list for CMS consistency
            return self._jb_get_collection('units')
        return [] # Simplified

# Singleton instance
db = SupabaseService()
