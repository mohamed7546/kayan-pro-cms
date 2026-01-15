# 🏢 Kayan Pro CMS

> Advanced Real Estate Content Management System with Visual Editor, Multi-Currency Calculator & Dual-Chat System

[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?logo=vercel)](https://kayan-pro-cms.vercel.app)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?logo=supabase)](https://supabase.com)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)

## ✨ Features

### 🎨 Unified Premium Design

- **Dark Glassmorphism Theme** with gold accents (#cfb165)
- **Professional Fonts**: Cairo (Arabic) + Outfit (English)
- **Fully Responsive** across all devices
- **Smooth Animations** and micro-interactions

### 💰 Multi-Currency Calculator

- Support for **3 currencies**: EGP (default), SAR, JOD
- **Customizable limits**: 40% minimum down payment, 24 months max installment
- **Real-time calculations** with instant updates
- **ROI projections** based on AI market analysis

### 🛡️ Admin Dashboard

- **Visual Page Editor** with GrapesJS (drag & drop)
- **Dual Chat System**: Telegram + Website live chat
- **Unit Management**: Full CRUD for projects and units
- **Media Library**: Auto-optimization (WebP, compression, thumbnails)
- **JWT Authentication** for secure access

### ⚙️ Backend API

- **FastAPI** with 20+ endpoints
- **Supabase** PostgreSQL database (7 tables)
- **Image Optimization**: Auto-resize, WebP conversion, thumbnails
- **Row Level Security** for data protection
- **Telegram Bot Integration**

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Supabase account
- Cloudinary account
- Telegram Bot Token

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/mohamed7546/kayan-pro-cms.git
cd kayan-pro-cms
```

1. **Install dependencies**

```bash
# Frontend
npm install

# Backend
pip install -r requirements.txt
```

1. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your credentials
```

1. **Set up Supabase**

- Create a new project on Supabase
- Run the SQL schema from `database/schema.sql`
- Copy your API keys to `.env`

1. **Deploy to Vercel**

```bash
vercel --prod
```

## 📁 Project Structure

```
cms_version/
├── api/                    # FastAPI Backend
│   ├── index.py           # Main API (20+ endpoints)
│   ├── config.py          # Configuration
│   ├── bot.py             # Telegram bot logic
│   └── services/
│       ├── supabase_service.py
│       ├── image_optimizer.py
│       └── chat_service.py
│
├── admin/                 # Admin Panel
│   ├── index.html
│   ├── css/admin.css
│   └── js/admin.js
│
├── public/                # Public Website
│   ├── calculator.html
│   └── css/unified-theme.css
│
├── database/
│   └── schema.sql         # Supabase schema
│
└── vercel.json            # Deployment config
```

## 🎯 Environment Variables

```env
# Telegram
TELEGRAM_TOKEN=your_bot_token
ADMIN_ID=your_telegram_user_id

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
JWT_SECRET=your_random_secret_key

# Domains
PUBLIC_DOMAIN=your-domain.vercel.app
ADMIN_DOMAIN=your-admin-domain.vercel.app
```

## 📊 Database Schema

The system uses 7 main tables:

- **projects**: Real estate projects
- **units**: Individual units within projects
- **pages**: Dynamic website pages
- **content_blocks**: Reusable content components
- **chats**: Unified chat messages (Telegram + Website)
- **leads**: Customer inquiries
- **media**: Image and file storage metadata

## 🎨 Design System

### Colors

- **Primary**: `#1a1a1a` (Dark background)
- **Accent**: `#cfb165` (Gold)
- **Text**: `#ffffff` (Light)
- **Secondary**: `#888888` (Gray)

### Typography

- **Arabic**: Cairo (400, 600, 700)
- **English**: Outfit (400, 600, 700)

### Effects

- **Glassmorphism**: 5% opacity + 12px blur
- **Shadows**: Soft, layered shadows
- **Transitions**: 0.3s ease

## 🔧 API Endpoints

### Authentication

- `POST /api/auth/login` - Admin login

### Projects & Units

- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/units` - List units
- `POST /api/units` - Create unit

### Pages & Content

- `GET /api/pages` - List pages
- `POST /api/pages` - Create page
- `PUT /api/pages/{id}` - Update page

### Media

- `POST /api/media/upload` - Upload image (auto-optimized)
- `GET /api/media` - List media files

### Chat

- `GET /api/chats` - List conversations
- `POST /api/chats/send` - Send message

### Telegram

- `POST /api/webhook` - Telegram webhook

## 📱 Telegram Bot

The bot handles:

- Property inquiries
- Image uploads with AI analysis
- Unit recommendations
- Lead generation

**Bot Handle**: @Kayanprobot

## 🌐 Deployment

### Vercel (Recommended)

1. Connect your GitHub repository
2. Add environment variables
3. Deploy automatically on push

### Manual Deployment

```bash
# Build frontend
npm run build

# Start backend
uvicorn api.index:app --host 0.0.0.0 --port 8000
```

## 📸 Screenshots

### Calculator

![Calculator](https://via.placeholder.com/800x400?text=Multi-Currency+Calculator)

### Admin Dashboard

![Dashboard](https://via.placeholder.com/800x400?text=Admin+Dashboard)

### Visual Editor

![Editor](https://via.placeholder.com/800x400?text=GrapesJS+Editor)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is proprietary software. All rights reserved.

## 👨‍💻 Author

**Mohamed**

- GitHub: [@mohamed7546](https://github.com/mohamed7546)

## 🙏 Acknowledgments

- **FastAPI** for the amazing Python framework
- **Supabase** for the database platform
- **GrapesJS** for the visual editor
- **Vercel** for seamless deployment
- **Cloudinary** for image optimization

---

**Built with ❤️ for the real estate industry**
