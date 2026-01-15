"""
NLP Command Processor for Arabic Telegram Bot Commands
Understands natural language commands in Egyptian Arabic
"""

import re
from typing import Dict, Optional, Tuple

class NLPCommandProcessor:
    def __init__(self):
        # Project name mappings
        self.project_map = {
            "حمد": "hamad-tower",  # Mapping to seeded UUIDs later or handled dynamically
            "الحمد": "hamad-tower",
            "hamad": "hamad-tower",
            "ليليان": "lilian-tower",
            "lilian": "lilian-tower"
        }
        
        # Number words in Arabic
        self.number_words = {
            "واحد": 1, "اتنين": 2, "ثلاثة": 3, "اربعة": 4, "خمسة": 5,
            "ستة": 6, "سبعة": 7, "ثمانية": 8, "تسعة": 9, "عشرة": 10,
            "عشر": 10, "عشرين": 20, "ثلاثين": 30, "اربعين": 40, "خمسين": 50
        }
    
    def extract_project_id(self, text: str) -> Optional[str]:
        """Extract project ID from text"""
        text_lower = text.lower()
        for key, project_id in self.project_map.items():
            if key in text_lower:
                return project_id
        return None
    
    def extract_numbers(self, text: str) -> list:
        """Extract all numbers from text (both digits and words)"""
        numbers = []
        
        # Extract digit numbers
        digit_matches = re.findall(r'\d+', text)
        numbers.extend([int(n) for n in digit_matches])
        
        # Extract word numbers
        for word, num in self.number_words.items():
            if word in text:
                numbers.append(num)
        
        return numbers
    
    def parse_price_update(self, text: str) -> Optional[Dict]:
        """
        Parse price update commands like:
        - "غير سعر الشقة 110م في الدور 10 لـ 2000000"
        - "عدل سعر الوحدة 110 متر دور 10 السعر 2 مليون"
        """
        # Check if it's a price update command
        price_keywords = ["غير سعر", "عدل سعر", "حدث سعر", "السعر", "price"]
        if not any(kw in text for kw in price_keywords):
            return None
        
        result = {}
        
        # Extract project
        result["project_id"] = self.extract_project_id(text)
        
        # Extract area (متر/م)
        area_match = re.search(r'(\d+)\s*(?:م|متر)', text)
        if area_match:
            result["area"] = int(area_match.group(1))
        
        # Extract floor (دور)
        floor_match = re.search(r'(?:دور|الدور)\s*(\d+)', text)
        if floor_match:
            result["floor"] = int(floor_match.group(1))
        
        # Extract price
        # Look for "لـ" or "السعر" followed by number
        price_match = re.search(r'(?:لـ|السعر|يبقى)\s*(\d+(?:,\d+)*)', text)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            result["new_price"] = int(price_str)
        
        # Handle "مليون" (million)
        if "مليون" in text:
            numbers = self.extract_numbers(text)
            if numbers:
                # Last number before "مليون" is likely the price
                for i, num in enumerate(numbers):
                    if i < len(numbers) - 1:  # Not the last number
                        result["new_price"] = num * 1000000
        
        return result if len(result) > 1 else None
    
    def parse_add_unit(self, text: str) -> Optional[Dict]:
        """
        Parse add unit commands like:
        - "اضف وحدة جديدة 2 غرفة 1 حمام دور 5 مساحة 120م سعر المتر 16000"
        """
        add_keywords = ["اضف وحدة", "وحدة جديدة", "add unit"]
        if not any(kw in text for kw in add_keywords):
            return None
        
        result = {}
        
        # Extract project
        result["project_id"] = self.extract_project_id(text)
        
        # Extract bedrooms
        bedrooms_match = re.search(r'(\d+)\s*(?:غرفة|غرف)', text)
        if bedrooms_match:
            result["bedrooms"] = int(bedrooms_match.group(1))
        
        # Extract bathrooms
        bathrooms_match = re.search(r'(\d+)\s*(?:حمام|حمامات)', text)
        if bathrooms_match:
            result["bathrooms"] = int(bathrooms_match.group(1))
        
        # Extract floor
        floor_match = re.search(r'(?:دور|الدور)\s*(\d+)', text)
        if floor_match:
            result["floor_number"] = int(floor_match.group(1))
        
        # Extract area
        area_match = re.search(r'(?:مساحة|المساحة)\s*(\d+)', text)
        if area_match:
            result["area_sqm"] = int(area_match.group(1))
        
        # Extract price per meter
        price_match = re.search(r'(?:سعر المتر|المتر)\s*(\d+)', text)
        if price_match:
            result["price_per_meter"] = int(price_match.group(1))
        
        return result if len(result) > 1 else None
    
    def parse_content_update(self, text: str) -> Optional[Dict]:
        """
        Parse content update commands like:
        - "غير النص اللي في الهيرو"
        - "حط صورة جديدة لبرج الحمد"
        - "شيل البلوك اللي فوق"
        """
        result = {}
        
        # Check for text update
        if any(kw in text for kw in ["غير النص", "عدل النص", "النص"]):
            result["action"] = "update_text"
            
            # Extract block ID
            if "هيرو" in text or "hero" in text:
                result["block_id"] = "hero_text"
            elif "عنوان" in text or "title" in text:
                result["block_id"] = "title"
        
        # Check for image update
        elif any(kw in text for kw in ["حط صورة", "غير الصورة", "صورة جديدة"]):
            result["action"] = "update_image"
            
            if "هيرو" in text or "hero" in text:
                result["block_id"] = "hero_image"
        
        # Check for block removal
        elif any(kw in text for kw in ["شيل", "امسح", "احذف"]):
            result["action"] = "delete_block"
        
        # Extract project
        result["project_id"] = self.extract_project_id(text)
        
        return result if "action" in result else None
    
    def parse_search_units(self, text: str) -> Optional[Dict]:
        """
        Parse unit search commands like:
        - "ابحث عن شقة 2 غرفة في الدور الخامس"
        - "عايز وحدة 3 غرف سعرها اقل من 2 مليون"
        """
        search_keywords = ["ابحث", "عايز", "محتاج", "search", "find"]
        if not any(kw in text for kw in search_keywords):
            return None
        
        result = {"filters": {}}
        
        # Extract project
        result["project_id"] = self.extract_project_id(text)
        
        # Extract bedrooms
        bedrooms_match = re.search(r'(\d+)\s*(?:غرفة|غرف)', text)
        if bedrooms_match:
            result["filters"]["bedrooms"] = int(bedrooms_match.group(1))
        
        # Extract bathrooms
        bathrooms_match = re.search(r'(\d+)\s*(?:حمام|حمامات)', text)
        if bathrooms_match:
            result["filters"]["bathrooms"] = int(bathrooms_match.group(1))
        
        # Extract floor
        floor_match = re.search(r'(?:دور|الدور)\s*(\d+)', text)
        if floor_match:
            result["filters"]["floor_number"] = int(floor_match.group(1))
        
        # Extract price range
        if "اقل من" in text or "أقل من" in text:
            price_match = re.search(r'(?:اقل من|أقل من)\s*(\d+)', text)
            if price_match:
                result["filters"]["price_max"] = int(price_match.group(1))
                if "مليون" in text:
                    result["filters"]["price_max"] *= 1000000
        
        if "اكتر من" in text or "أكتر من" in text:
            price_match = re.search(r'(?:اكتر من|أكتر من)\s*(\d+)', text)
            if price_match:
                result["filters"]["price_min"] = int(price_match.group(1))
                if "مليون" in text:
                    result["filters"]["price_min"] *= 1000000
        
        return result if result["filters"] else None
    
    def process_command(self, text: str) -> Tuple[str, Optional[Dict]]:
        """
        Main method to process any command and return (command_type, parsed_data)
        """
        # Try to parse as different command types
        
        # Price update
        price_data = self.parse_price_update(text)
        if price_data:
            return ("update_price", price_data)
        
        # Add unit
        add_data = self.parse_add_unit(text)
        if add_data:
            return ("add_unit", add_data)
        
        # Content update
        content_data = self.parse_content_update(text)
        if content_data:
            return ("update_content", content_data)
        
        # Search units
        search_data = self.parse_search_units(text)
        if search_data:
            return ("search_units", search_data)
        
        # Unknown command
        return ("unknown", None)
