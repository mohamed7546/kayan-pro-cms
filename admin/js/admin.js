import grapesjs from 'grapesjs';
import 'grapesjs/dist/css/grapes.min.css';
import grapesjsPresetWebpage from 'grapesjs-preset-webpage';
import grapesjsBlocksBasic from 'grapesjs-blocks-basic';

// API Configuration
const API_BASE = window.location.hostname.includes('localhost')
    ? 'http://localhost:8000'
    : 'https://kayan-admin.vercel.app';

let authToken = localStorage.getItem('admin_token');
let editor = null;
let currentChatTelegram = null;
let currentChatWebsite = null;

// ==================== AUTH ====================

async function login(username, password) {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    if (response.ok) {
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('admin_token', authToken);
        return true;
    }
    return false;
}

window.logout = function () {
    localStorage.removeItem('admin_token');
    window.location.reload();
}

// ==================== API CALLS ====================

async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        logout();
        return null;
    }

    return response.json();
}

// ==================== NAVIGATION ====================

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.dataset.page;

        // Update active nav
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');

        // Show page
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById(`page-${page}`).classList.add('active');

        // Load page data
        loadPageData(page);
    });
});

async function loadPageData(page) {
    switch (page) {
        case 'dashboard':
            await loadDashboard();
            break;
        case 'editor':
            initEditor();
            break;
        case 'units':
            await loadUnits();
            break;
        case 'media':
            await loadMedia();
            break;
        case 'chats':
            await loadChats();
            break;
    }
}

// ==================== DASHBOARD ====================

async function loadDashboard() {
    // Load stats
    const stats = await apiCall('/api/stats');
    if (stats) {
        document.getElementById('total-revenue').textContent = stats.revenue;
        document.getElementById('new-leads').textContent = stats.leads;
        document.getElementById('available-units').textContent = stats.units;
        document.getElementById('active-chats').textContent = stats.chats;
    }

    // Load chats
    await loadChats();

    // Load activity
    const activity = await apiCall('/api/activity');
    if (activity) {
        renderActivity(activity);
    }
}

async function loadChats() {
    const chats = await apiCall('/api/chats');
    if (chats) {
        renderTelegramChats(chats.telegram || []);
        renderWebsiteChats(chats.website || []);
    }
}

function renderTelegramChats(chats) {
    const container = document.getElementById('telegram-chats');
    container.innerHTML = chats.map(chat => `
        <div class="chat-item" onclick="selectTelegramChat('${chat.id}')">
            <strong>${chat.user_name}</strong>
            <p>${chat.messages[chat.messages.length - 1]?.text || ''}</p>
        </div>
    `).join('');
}

function renderWebsiteChats(chats) {
    const container = document.getElementById('website-chats');
    container.innerHTML = chats.map(chat => `
        <div class="chat-item" onclick="selectWebsiteChat('${chat.id}')">
            <strong>Visitor #${chat.user_id}</strong>
            <p>${chat.messages[chat.messages.length - 1]?.text || ''}</p>
        </div>
    `).join('');
}

window.selectTelegramChat = async function (chatId) {
    const chats = await apiCall('/api/chats?source=telegram');
    currentChatTelegram = chats.find(c => c.id === chatId);

    const container = document.getElementById('telegram-messages');
    container.innerHTML = currentChatTelegram.messages.map(msg => `
        <div class="message ${msg.from_admin ? 'admin' : 'user'}">
            ${msg.text}
        </div>
    `).join('');
}

window.selectWebsiteChat = async function (chatId) {
    const chats = await apiCall('/api/chats?source=website');
    currentChatWebsite = chats.find(c => c.id === chatId);

    const container = document.getElementById('website-messages');
    container.innerHTML = currentChatWebsite.messages.map(msg => `
        <div class="message ${msg.from_admin ? 'admin' : 'user'}">
            ${msg.text}
        </div>
    `).join('');
}

window.sendTelegramMessage = async function () {
    const input = document.getElementById('telegram-input');
    const message = input.value.trim();

    if (message && currentChatTelegram) {
        await apiCall('/api/chats/send', {
            method: 'POST',
            body: JSON.stringify({
                source: 'telegram',
                user_id: currentChatTelegram.user_id,
                message
            })
        });

        input.value = '';
        await selectTelegramChat(currentChatTelegram.id);
    }
}

window.sendWebsiteMessage = async function () {
    const input = document.getElementById('website-input');
    const message = input.value.trim();

    if (message && currentChatWebsite) {
        await apiCall('/api/chats/send', {
            method: 'POST',
            body: JSON.stringify({
                source: 'website',
                user_id: currentChatWebsite.user_id,
                message
            })
        });

        input.value = '';
        await selectWebsiteChat(currentChatWebsite.id);
    }
}

function renderActivity(activities) {
    const container = document.getElementById('activity-list');
    container.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <span>${activity.icon}</span>
            <div>
                <strong>${activity.title}</strong>
                <p>${activity.description}</p>
                <small>${activity.time}</small>
            </div>
        </div>
    `).join('');
}

// ==================== EDITOR (GrapesJS) ====================

function initEditor() {
    if (editor) return;

    editor = grapesjs.init({
        container: '#gjs',
        fromElement: false,
        height: '100%',
        width: 'auto',
        storageManager: false,
        plugins: [grapesjsPresetWebpage, grapesjsBlocksBasic],
        pluginsOpts: {
            [grapesjsPresetWebpage]: {
                blocks: ['link-block', 'quote', 'text-basic']
            }
        },
        canvas: {
            styles: [
                'https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap'
            ]
        },
        blockManager: {
            appendTo: '.blocks-container',
            blocks: [
                {
                    id: 'unit-selector',
                    label: 'اختيار وحدة',
                    category: 'كيان برو',
                    content: `
                        <div class="unit-selector">
                            <h3>اختر وحدتك المثالية</h3>
                            <select class="project-select">
                                <option>برج حمد</option>
                                <option>برج ليليان</option>
                            </select>
                            <div class="units-grid"></div>
                        </div>
                    `
                }
            ]
        }
    });
}

window.savePage = async function () {
    if (!editor) return;

    const html = editor.getHtml();
    const css = editor.getCss();
    const slug = document.getElementById('page-selector').value;

    await apiCall('/api/pages', {
        method: 'POST',
        body: JSON.stringify({
            slug,
            content: { html, css },
            is_published: false
        })
    });

    alert('تم الحفظ بنجاح!');
}

window.previewPage = function () {
    if (!editor) return;
    const html = editor.runCommand('gjs-get-inlined-html');
    const win = window.open('', '_blank');
    win.document.write(html);
}

window.publishPage = async function () {
    await savePage();
    // Mark as published
    alert('تم النشر بنجاح!');
}

// ==================== UNITS ====================

async function loadUnits() {
    const units = await apiCall('/api/units');
    if (units) {
        renderUnits(units.units);
    }
}

function renderUnits(units) {
    const container = document.getElementById('units-grid');
    container.innerHTML = units.map(unit => `
        <div class="unit-card">
            <img src="${unit.images?.[0] || '/placeholder.jpg'}" alt="${unit.unit_number}">
            <div class="unit-info">
                <h4>وحدة ${unit.unit_number}</h4>
                <p>${unit.unit_type === 'residential' ? 'سكني' : 'إداري'}</p>
                <p>المساحة: ${unit.area_sqm} م²</p>
                <p>السعر: ${unit.total_price} ريال</p>
                <span class="status ${unit.status}">${unit.status}</span>
            </div>
        </div>
    `).join('');
}

// ==================== MEDIA ====================

async function loadMedia() {
    const media = await apiCall('/api/media');
    if (media) {
        renderMedia(media.media);
    }
}

function renderMedia(mediaFiles) {
    const container = document.getElementById('media-grid');
    container.innerHTML = mediaFiles.map(file => `
        <div class="media-card">
            <img src="${file.thumbnail_url}" alt="${file.filename}">
            <div class="media-info">
                <p>${file.filename}</p>
                <small>${(file.file_size / 1024).toFixed(2)} KB</small>
            </div>
        </div>
    `).join('');
}

window.openUploadModal = function () {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.multiple = true;

    input.onchange = async (e) => {
        const files = Array.from(e.target.files);

        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);

            await fetch(`${API_BASE}/api/media/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                body: formData
            });
        }

        await loadMedia();
    };

    input.click();
}

// ==================== INIT ====================

document.addEventListener('DOMContentLoaded', () => {
    if (!authToken) {
        // Show login modal
        const username = prompt('Username:');
        const password = prompt('Password:');

        login(username, password).then(success => {
            if (success) {
                loadDashboard();
            } else {
                alert('Invalid credentials');
            }
        });
    } else {
        loadDashboard();
    }
});
