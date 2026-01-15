from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import jwt
from datetime import datetime, timedelta

from .config import settings
from .services.supabase_service import db
from .services.image_optimizer import image_optimizer
from .services.chat_service import chat_service

app = FastAPI(title="Kayan Pro CMS API", version="2.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{settings.PUBLIC_DOMAIN}",
        f"https://{settings.ADMIN_DOMAIN}",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ==================== AUTH ====================

def create_access_token(data: dict):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/auth/login")
async def login(request: Request):
    """Admin login"""
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ==================== HEALTH CHECK ====================

# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Kayan Pro CMS API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

# ==================== SEED DATA (Temporary) ====================
@app.get("/api/seed")
async def seed_database():
    """Seed initial content for Homepage and Calculator"""
    try:
        # 1. Home Page
        home_html = """
        <div id="i7mm" class="gjs-row" style="height: 100vh; background: #1a1a1a; color: gold; display: flex; align-items: center; justify-content: center; text-align: center; font-family: 'Cairo', sans-serif;">
            <div id="im5l" class="gjs-cell">
                <h1 id="ix6t" style="font-size: 3rem; margin-bottom: 20px;">كيان برو - Kayan Pro</h1>
                <div id="iz1k" style="font-size: 1.5rem; margin-bottom: 30px;">استثمارك العقاري الأمثل في المملكة</div>
                <a id="il5v" href="/calculator" style="padding: 15px 30px; background: #c6a87c; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold;">احسب استثمارك الآن</a>
            </div>
        </div>
        """
        await db.save_page({
            "slug": "home",
            "title": "الرئيسية - كيان برو",
            "content": {"html": home_html, "css": "* { box-sizing: border-box; } body { margin: 0; background: #000; }"},
            "is_published": True
        })
        
        # 2. Calculator Page
        await db.save_page({
            "slug": "calculator",
            "title": "حاسبة الاستثمار",
            "content": {"html": "<div id='calculator-app'>Loading Calculator...</div>", "css": ""},
            "is_published": True
        })
        
        return {"status": "success", "message": "Database seeded successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==================== PROJECTS ====================

@app.get("/api/projects")
async def get_projects(status: Optional[str] = None):
    """Get all projects"""
    projects = await db.get_projects(status=status)
    return {"projects": projects}

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get single project"""
    project = await db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/api/projects")
async def create_project(request: Request, user=Depends(verify_token)):
    """Create new project (Admin only)"""
    data = await request.json()
    project = await db.create_project(data)
    return project

@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, request: Request, user=Depends(verify_token)):
    """Update project (Admin only)"""
    data = await request.json()
    project = await db.update_project(project_id, data)
    return project

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str, user=Depends(verify_token)):
    """Delete project (Admin only)"""
    await db.delete_project(project_id)
    return {"message": "Project deleted successfully"}

# ==================== UNITS ====================

@app.get("/api/units")
async def get_units(
    project_id: Optional[str] = None,
    unit_type: Optional[str] = None,
    status: Optional[str] = None
):
    """Get units with filters"""
    units = await db.get_units(project_id=project_id, unit_type=unit_type, status=status)
    return {"units": units}

@app.get("/api/units/{unit_id}")
async def get_unit(unit_id: str):
    """Get single unit"""
    unit = await db.get_unit(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@app.post("/api/units")
async def create_unit(request: Request, user=Depends(verify_token)):
    """Create new unit (Admin only)"""
    data = await request.json()
    unit = await db.create_unit(data)
    return unit

@app.put("/api/units/{unit_id}")
async def update_unit(unit_id: str, request: Request, user=Depends(verify_token)):
    """Update unit (Admin only)"""
    data = await request.json()
    unit = await db.update_unit(unit_id, data)
    return unit

@app.delete("/api/units/{unit_id}")
async def delete_unit(unit_id: str, user=Depends(verify_token)):
    """Delete unit (Admin only)"""
    await db.delete_unit(unit_id)
    return {"message": "Unit deleted successfully"}

# ==================== PAGES ====================

@app.get("/api/pages")
async def get_pages(published_only: bool = False):
    """Get all pages"""
    pages = await db.get_pages(published_only=published_only)
    return {"pages": pages}

@app.get("/api/pages/{slug}")
async def get_page(slug: str):
    """Get page by slug"""
    page = await db.get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@app.post("/api/pages")
async def save_page(request: Request, user=Depends(verify_token)):
    """Save page (Admin only)"""
    data = await request.json()
    page = await db.save_page(data)
    return page

@app.delete("/api/pages/{page_id}")
async def delete_page(page_id: str, user=Depends(verify_token)):
    """Delete page (Admin only)"""
    await db.delete_page(page_id)
    return {"message": "Page deleted successfully"}

# ==================== CONTENT BLOCKS ====================

@app.get("/api/blocks")
async def get_content_blocks(category: Optional[str] = None):
    """Get content blocks"""
    blocks = await db.get_content_blocks(category=category)
    return {"blocks": blocks}

@app.post("/api/blocks")
async def create_content_block(request: Request, user=Depends(verify_token)):
    """Create content block (Admin only)"""
    data = await request.json()
    block = await db.create_content_block(data)
    return block

# ==================== CHATS ====================

@app.get("/api/chats")
async def get_chats(source: Optional[str] = None, user=Depends(verify_token)):
    """Get all chats (Admin only)"""
    if source:
        chats = await db.get_chats(source=source)
    else:
        chats = await chat_service.get_all_active_chats()
    return chats

@app.post("/api/chats/send")
async def send_chat_message(request: Request, user=Depends(verify_token)):
    """Send message in chat (Admin only)"""
    data = await request.json()
    chat = await chat_service.save_message(
        source=data['source'],
        user_id=data['user_id'],
        user_name=data.get('user_name', 'Admin'),
        message=data['message'],
        is_from_admin=True
    )
    return chat

# ==================== LEADS ====================

@app.get("/api/leads")
async def get_leads(status: Optional[str] = None, user=Depends(verify_token)):
    """Get leads (Admin only)"""
    leads = await db.get_leads(status=status)
    return {"leads": leads}

@app.post("/api/leads")
async def create_lead(request: Request):
    """Create new lead (Public)"""
    data = await request.json()
    lead = await db.create_lead(data)
    return lead

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, request: Request, user=Depends(verify_token)):
    """Update lead (Admin only)"""
    data = await request.json()
    lead = await db.update_lead(lead_id, data)
    return lead

# ==================== MEDIA ====================

@app.get("/api/media")
async def get_media(tags: Optional[List[str]] = None, user=Depends(verify_token)):
    """Get media files (Admin only)"""
    media = await db.get_media(tags=tags)
    return {"media": media}

@app.post("/api/media/upload")
async def upload_media(file: UploadFile = File(...), user=Depends(verify_token)):
    """Upload and optimize media (Admin only)"""
    try:
        # Read file
        contents = await file.read()
        
        # Optimize image
        result = image_optimizer.optimize_image(contents, file.filename)
        
        if not result:
            raise HTTPException(status_code=500, detail="Image optimization failed")
        
        # Save to database
        media_data = {
            'filename': file.filename,
            'original_url': result['original_url'],
            'optimized_url': result['optimized_url'],
            'thumbnail_url': result['thumbnail_url'],
            'file_type': file.content_type,
            'file_size': result['file_size'],
            'width': result['width'],
            'height': result['height']
        }
        
        media = await db.create_media(media_data)
        return media
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/media/{media_id}")
async def delete_media(media_id: str, user=Depends(verify_token)):
    """Delete media (Admin only)"""
    await db.delete_media(media_id)
    return {"message": "Media deleted successfully"}

# ==================== TELEGRAM WEBHOOK ====================

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook"""
    try:
        data = await request.json()
        # Import bot handler
        from .bot import process_update
        await process_update(data)
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
