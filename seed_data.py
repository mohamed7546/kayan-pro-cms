import asyncio
import os
from api.services.supabase_service import db

# Minimal GrapesJS-compatible HTML for Home
HOME_HTML = """
<div id="i7mm" class="gjs-row" style="height: 100vh; background: #1a1a1a; color: gold; display: flex; align-items: center; justify-content: center; text-align: center; font-family: 'Cairo', sans-serif;">
  <div id="im5l" class="gjs-cell">
    <h1 id="ix6t" style="font-size: 3rem; margin-bottom: 20px;">كيان برو - Kayan Pro</h1>
    <div id="iz1k" style="font-size: 1.5rem; margin-bottom: 30px;">استثمارك العقاري الأمثل في المملكة</div>
    <a id="il5v" href="/calculator" style="padding: 15px 30px; background: #c6a87c; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold;">احسب استثمارك الآن</a>
  </div>
</div>
<div class="gjs-row" style="padding: 50px 20px; background: #111; color: #fff; font-family: 'Cairo', sans-serif;">
  <div class="gjs-cell">
    <h2 style="text-align: center; color: #c6a87c;">مشاريعنا المميزة</h2>
    <div id="project-list" style="display: flex; gap: 20px; justify-content: center; margin-top: 30px; flex-wrap: wrap;">
       <!-- Dynamic Project List Block -->
       <div class="project-card" style="border: 1px solid #333; padding: 20px; width: 300px;">
          <h3>برج حمد</h3>
          <p>تفاصيل المشروع...</p>
       </div>
       <div class="project-card" style="border: 1px solid #333; padding: 20px; width: 300px;">
          <h3>برج ليليان</h3>
          <p>تفاصيل المشروع...</p>
       </div>
    </div>
  </div>
</div>
"""

CSS = """
* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: 'Cairo', sans-serif; background: #000; }
"""

async def seed():
    print("🌱 Seeding Pages...")
    
    # 1. Home Page
    print("   Creating Home Page...")
    await db.save_page({
        "slug": "home",
        "title": "الرئيسية - كيان برو",
        "content": {"html": HOME_HTML, "css": CSS},
        "is_published": True
    })
    
    # 2. Calculator Page
    print("   Creating Calculator Page (Dynamic Wrapper)...")
    await db.save_page({
        "slug": "calculator",
        "title": "حاسبة الاستثمار",
        "content": {"html": "<div id='calculator-app'>Loading Calculator...</div>", "css": ""},
        "is_published": True
    })
    
    print("✅ Seeding Complete!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed())
