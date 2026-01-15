-- ==================== KAYAN PRO CMS DATABASE SCHEMA ====================
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== PROJECTS TABLE ====================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    location VARCHAR(255),
    cover_image_url TEXT,
    gallery JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'upcoming')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== UNITS TABLE ====================
CREATE TABLE units (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    unit_number VARCHAR(50) NOT NULL,
    unit_type VARCHAR(50) NOT NULL CHECK (unit_type IN ('residential', 'commercial')),
    floor_number INTEGER,
    area_sqm DECIMAL(10,2) NOT NULL,
    price_per_sqm DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) GENERATED ALWAYS AS (area_sqm * price_per_sqm) STORED,
    bedrooms INTEGER DEFAULT 0,
    bathrooms INTEGER DEFAULT 0,
    kitchens INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'available' CHECK (status IN ('available', 'reserved', 'sold')),
    images JSONB DEFAULT '[]'::jsonb,
    features JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== PAGES TABLE ====================
CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    meta_description TEXT,
    content JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== CONTENT BLOCKS TABLE ====================
CREATE TABLE content_blocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    html TEXT NOT NULL,
    css TEXT,
    thumbnail_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== CHATS TABLE ====================
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL CHECK (source IN ('telegram', 'website')),
    user_id VARCHAR(255) NOT NULL,
    user_name VARCHAR(255),
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'read', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== LEADS TABLE ====================
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    source VARCHAR(100),
    interested_in UUID REFERENCES units(id) ON DELETE SET NULL,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'lost')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== MEDIA TABLE ====================
CREATE TABLE media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_url TEXT NOT NULL,
    optimized_url TEXT,
    thumbnail_url TEXT,
    file_type VARCHAR(50),
    file_size INTEGER,
    width INTEGER,
    height INTEGER,
    alt_text VARCHAR(255),
    tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== INDEXES ====================
CREATE INDEX idx_units_project ON units(project_id);
CREATE INDEX idx_units_type ON units(unit_type);
CREATE INDEX idx_units_status ON units(status);
CREATE INDEX idx_chats_source ON chats(source);
CREATE INDEX idx_chats_user ON chats(user_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_pages_slug ON pages(slug);

-- ==================== TRIGGERS FOR UPDATED_AT ====================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_units_updated_at BEFORE UPDATE ON units
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pages_updated_at BEFORE UPDATE ON pages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chats_updated_at BEFORE UPDATE ON chats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== SAMPLE DATA ====================
-- Insert sample projects
INSERT INTO projects (name, name_ar, description, description_ar, location, status) VALUES
('Hamad Tower', 'برج حمد', 'Luxury residential and commercial tower', 'برج سكني وتجاري فاخر', 'Riyadh', 'active'),
('Lilian Tower', 'برج ليليان', 'Modern mixed-use development', 'مشروع متعدد الاستخدامات حديث', 'Jeddah', 'active');

-- Insert sample units (you'll need to replace project_id with actual UUIDs from above)
-- Run this after getting the project IDs:
-- SELECT id, name FROM projects;

-- Example (replace the UUID with actual project ID):
-- INSERT INTO units (project_id, unit_number, unit_type, floor_number, area_sqm, price_per_sqm, bedrooms, bathrooms, kitchens, status) VALUES
-- ('YOUR-PROJECT-UUID-HERE', '301', 'residential', 3, 120.5, 15000, 3, 2, 1, 'available');

-- ==================== ROW LEVEL SECURITY (RLS) ====================
-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE units ENABLE ROW LEVEL SECURITY;
ALTER TABLE pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE media ENABLE ROW LEVEL SECURITY;

-- Public read access for published content
CREATE POLICY "Public can view active projects" ON projects
    FOR SELECT USING (status = 'active');

CREATE POLICY "Public can view available units" ON units
    FOR SELECT USING (status IN ('available', 'reserved'));

CREATE POLICY "Public can view published pages" ON pages
    FOR SELECT USING (is_published = true);

-- Admin full access (you'll need to set up authentication)
-- For now, allow all operations (you can restrict this later)
CREATE POLICY "Allow all for authenticated users" ON projects
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON units
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON pages
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON content_blocks
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON chats
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON leads
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON media
    FOR ALL USING (true);

-- ==================== DONE! ====================
-- Your database is now ready for the Kayan Pro CMS!
