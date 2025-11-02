import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin
import random
import json

# -------- Ayarlar --------
BASE_URL = "https://www.hdfilmizle.life"
POSTERS_DIR = "posters"
INDEX_FILE = "index.html"
HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TOTAL_PAGES = 1500 # 1500 Sayfa film indir (1 sayfasa 30 tane var)

os.makedirs(POSTERS_DIR, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()

def fetch_page(page=1):
    url = f"{BASE_URL}/page/{page}/" if page > 1 else BASE_URL + "/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[!] Sayfa çekilemedi: {url} -> {e}")
        return ""

def parse_films(html):
    soup = BeautifulSoup(html, "html.parser")
    films = []
    seen_titles = set()
    
    for a in soup.select("a.poster"):
        title = (a.get("title") or (a.select_one(".title") and a.select_one(".title").text) or "").strip()
        href = a.get("href") or ""
        link = urljoin(BASE_URL, href)
        img = a.select_one("img")
        poster_src = ""
        if img:
            poster_src = img.get("data-src") or img.get("src") or ""
            poster_src = urljoin(BASE_URL, poster_src) if poster_src.startswith("/") else poster_src
        if not title and img and img.get("alt"):
            title = img.get("alt").strip()
        
        if title and poster_src and title not in seen_titles:
            films.append({"title": title, "poster_url": poster_src, "link": link})
            seen_titles.add(title)
    
    return films

def download_posters(films):
    for idx, f in enumerate(films):
        print(f"[+] Poster indiriliyor: {idx+1}/{len(films)} - {f['title']}")
        safe_name = sanitize_filename(f["title"])
        ext = os.path.splitext(f["poster_url"].split("?")[0])[1] or ".jpg"
        filename = f"{safe_name}{ext}"
        path = os.path.join(POSTERS_DIR, filename)
        f["poster_file"] = os.path.join(POSTERS_DIR, filename).replace("\\", "/")
        if os.path.exists(path):
            continue
        try:
            r = requests.get(f["poster_url"], headers=HEADERS, stream=True, timeout=20)
            r.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in r.iter_content(1024):
                    fh.write(chunk)
        except Exception as e:
            print(f"[-] Poster indirilemedi: {f['title']} -> {e}")
            f["poster_file"] = f["poster_url"]

def generate_netflix_html(films):
    squid_game = {
        "title": "Squid Game",
        "poster_file": "https://m.media-amazon.com/images/M/MV5BYWE3MDVkN2EtNjQ5MS00ZDQ4LTliNzYtMjc2YWMzMDEwMTA3XkEyXkFqcGdeQXVyMTEzMTI1Mjk3._V1_.jpg",
        "link": "https://www.hdfilmizle.life/dizi/squid-game-izle/"
    }
    
    films.insert(0, squid_game)
    random.shuffle(films[1:])
    chunk_size = len(films) // 8 if len(films) >= 8 else max(1, len(films) // 4)
    
    categories = {
        "🔥 Popüler Filmler": films[:chunk_size*2],
        "⭐ Yeni Eklenenler": films[chunk_size*2:chunk_size*3],
        "🎬 Aksiyon ve Macera": films[chunk_size*3:chunk_size*4],
        "😂 Komedi": films[chunk_size*4:chunk_size*5],
        "💔 Drama": films[chunk_size*5:chunk_size*6],
        "👻 Korku ve Gerilim": films[chunk_size*6:chunk_size*7],
        "🌟 IMDb Favorileri": films[chunk_size*7:],
        "🎭 Türkiye'den Filmler": films[:chunk_size]
    }
    
    hero_films = [squid_game] + random.sample(films[1:], min(4, len(films)-1))
    
    # Landing sayfası için rastgele posterler
    landing_posters = random.sample(films, min(20, len(films)))
    
    html = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HDFilmizle - Sınırsız film, dizi ve çok daha fazlası</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --netflix-red: #e50914;
    --netflix-black: #141414;
    --netflix-dark: #000000;
    --netflix-gray: #2f2f2f;
    --netflix-light: #e5e5e5;
}

body {
    background: var(--netflix-black);
    color: #fff;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow-x: hidden;
}

/* Landing Page */
.landing-page {
    min-height: 100vh;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.landing-bg {
    position: absolute;
    inset: 0;
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    grid-template-rows: repeat(4, 1fr);
    opacity: 0.15;
    animation: bgFade 3s ease-in-out infinite alternate;
}

.landing-bg img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    animation: posterFloat 20s ease-in-out infinite;
}

.landing-bg img:nth-child(even) {
    animation-direction: reverse;
    animation-duration: 25s;
}

@keyframes bgFade {
    0% { opacity: 0.1; }
    100% { opacity: 0.2; }
}

@keyframes posterFloat {
    0%, 100% { transform: scale(1) rotate(0deg); }
    50% { transform: scale(1.1) rotate(2deg); }
}

.landing-overlay {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.9) 100%);
}

.landing-content {
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 800px;
    padding: 40px;
}

.landing-logo {
    font-size: 72px;
    font-weight: bold;
    color: var(--netflix-red);
    margin-bottom: 30px;
    letter-spacing: 3px;
    text-shadow: 3px 3px 10px rgba(229,9,20,0.5);
    animation: logoGlow 2s ease-in-out infinite;
}

@keyframes logoGlow {
    0%, 100% { text-shadow: 3px 3px 10px rgba(229,9,20,0.5); }
    50% { text-shadow: 3px 3px 20px rgba(229,9,20,0.8), 0 0 30px rgba(229,9,20,0.6); }
}

.landing-slogan {
    font-size: 48px;
    font-weight: bold;
    margin-bottom: 20px;
    line-height: 1.2;
}

.landing-description {
    font-size: 24px;
    color: #ccc;
    margin-bottom: 40px;
    line-height: 1.5;
}

.landing-features {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-bottom: 40px;
    flex-wrap: wrap;
}

.feature-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
}

.feature-icon {
    font-size: 24px;
}

.landing-buttons {
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
}

.landing-btn {
    padding: 18px 40px;
    font-size: 20px;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 10px;
}

.landing-btn-primary {
    background: var(--netflix-red);
    color: #fff;
}

.landing-btn-primary:hover {
    background: #f40612;
    transform: scale(1.05);
}

.landing-btn-secondary {
    background: rgba(255,255,255,0.2);
    color: #fff;
    border: 2px solid #fff;
}

.landing-btn-secondary:hover {
    background: rgba(255,255,255,0.3);
    transform: scale(1.05);
}

/* Auth Screens */
.auth-screen {
    position: fixed;
    inset: 0;
    background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 800"><rect fill="%23141414" width="1440" height="800"/></svg>');
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.auth-screen.show {
    display: flex;
}

.auth-box {
    background: rgba(0,0,0,0.85);
    padding: 60px 68px;
    border-radius: 8px;
    max-width: 450px;
    width: 90%;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    backdrop-filter: blur(10px);
}

.auth-logo {
    font-size: 48px;
    font-weight: bold;
    color: var(--netflix-red);
    text-align: center;
    margin-bottom: 28px;
    letter-spacing: 2px;
}

.auth-title {
    font-size: 32px;
    font-weight: 600;
    margin-bottom: 28px;
}

.input-group {
    margin-bottom: 16px;
}

.auth-input {
    width: 100%;
    padding: 16px 20px;
    background: #333;
    border: none;
    border-radius: 4px;
    color: #fff;
    font-size: 16px;
}

.auth-input:focus {
    outline: none;
    background: #454545;
}

.auth-btn {
    width: 100%;
    padding: 16px;
    background: var(--netflix-red);
    border: none;
    border-radius: 4px;
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 24px;
}

.auth-btn:hover {
    background: #f40612;
}

.auth-help {
    display: flex;
    justify-content: space-between;
    margin-top: 12px;
    font-size: 13px;
}

.auth-help a {
    color: #b3b3b3;
    text-decoration: none;
    cursor: pointer;
}

.auth-footer {
    margin-top: 16px;
    color: #737373;
    font-size: 16px;
}

.auth-footer a {
    color: #fff;
    text-decoration: none;
    cursor: pointer;
}

.help-modal {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.9);
    z-index: 10000;
    align-items: center;
    justify-content: center;
}

.help-modal.show {
    display: flex;
}

.help-content {
    background: #181818;
    padding: 40px;
    border-radius: 8px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

/* Header */
.header {
    position: fixed;
    top: 0;
    width: 100%;
    padding: 20px 50px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    transition: background 0.3s;
    background: linear-gradient(180deg, rgba(0,0,0,0.7) 10%, transparent);
}

.header.scrolled {
    background: rgba(20,20,20,0.98);
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 30px;
}

.logo {
    font-size: 36px;
    font-weight: bold;
    color: var(--netflix-red);
    text-decoration: none;
    letter-spacing: 2px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    cursor: pointer;
}

.nav {
    display: flex;
    gap: 20px;
}

.nav a {
    color: #e5e5e5;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
}

.nav a.active::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--netflix-red);
}

.header-right {
    display: flex;
    align-items: center;
    gap: 25px;
}

.search-container {
    position: relative;
}

.search-btn {
    background: none;
    border: none;
    color: #fff;
    font-size: 20px;
    cursor: pointer;
}

.search-box {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0,0,0,0.85);
    border: 1px solid #fff;
    display: flex;
    padding: 5px 10px;
    width: 0;
    opacity: 0;
    transition: all 0.3s;
    overflow: hidden;
}

.search-box.active {
    width: 280px;
    opacity: 1;
}

.search-input {
    background: none;
    border: none;
    color: #fff;
    outline: none;
    width: 100%;
    font-size: 14px;
}

.notification-btn {
    position: relative;
    background: none;
    border: none;
    color: #fff;
    font-size: 22px;
    cursor: pointer;
}

.notification-badge {
    position: absolute;
    top: 0;
    right: 0;
    background: var(--netflix-red);
    color: #fff;
    font-size: 10px;
    padding: 2px 5px;
    border-radius: 10px;
}

.notification-dropdown {
    position: absolute;
    top: 50px;
    right: 0;
    background: rgba(0,0,0,0.95);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 4px;
    min-width: 350px;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s;
    max-height: 400px;
    overflow-y: auto;
}

.notification-btn:hover .notification-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.notification-item {
    padding: 15px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.profile-menu {
    position: relative;
}

.profile-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: none;
    border: none;
    cursor: pointer;
    color: #fff;
}

.profile-avatar {
    width: 32px;
    height: 32px;
    border-radius: 4px;
    background: linear-gradient(135deg, var(--netflix-red), #ff4444);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.profile-dropdown {
    position: absolute;
    top: 50px;
    right: 0;
    background: rgba(0,0,0,0.95);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 4px;
    min-width: 200px;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s;
}

.profile-menu:hover .profile-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.dropdown-item {
    padding: 12px 16px;
    color: #fff;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.dropdown-item:hover {
    background: rgba(255,255,255,0.1);
}

.dropdown-divider {
    height: 1px;
    background: rgba(255,255,255,0.15);
}

/* Hero Slider */
.hero-slider {
    height: 90vh;
    position: relative;
    overflow: hidden;
    margin-bottom: 20px;
}

.hero-slide {
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0;
    transition: opacity 1s;
}

.hero-slide.active {
    opacity: 1;
}

.hero-slide::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(to right, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 40%, transparent 100%),
                linear-gradient(to top, rgba(20,20,20,0.9) 0%, transparent 50%);
    z-index: 1;
}

.hero-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    animation: slowZoom 20s ease-in-out infinite;
}

@keyframes slowZoom {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.hero-content {
    position: absolute;
    bottom: 35%;
    left: 50px;
    z-index: 2;
    max-width: 550px;
}

.hero-title {
    font-size: 56px;
    font-weight: bold;
    margin-bottom: 15px;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
}

.hero-description {
    font-size: 18px;
    line-height: 1.5;
    margin-bottom: 25px;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
}

.hero-buttons {
    display: flex;
    gap: 15px;
}

.btn {
    padding: 14px 32px;
    border: none;
    border-radius: 6px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.3s;
}

.btn-play {
    background: #fff;
    color: #000;
}

.btn-play:hover {
    background: rgba(255,255,255,0.85);
}

.btn-info {
    background: rgba(109,109,110,0.7);
    color: #fff;
}

.btn-info:hover {
    background: rgba(109,109,110,0.5);
}

.hero-nav {
    position: absolute;
    bottom: 30px;
    right: 50px;
    z-index: 2;
    display: flex;
    gap: 10px;
}

.hero-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: rgba(255,255,255,0.5);
    cursor: pointer;
}

.hero-dot.active {
    background: #fff;
    width: 32px;
    border-radius: 6px;
}

/* Categories */
.category {
    padding: 20px 50px;
    margin-bottom: 30px;
}

.category-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
}

.category-title {
    font-size: 24px;
    font-weight: bold;
}

.view-all {
    color: var(--netflix-red);
    font-size: 14px;
    cursor: pointer;
}

.movie-row {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    scroll-behavior: smooth;
    padding-bottom: 15px;
}

.movie-row::-webkit-scrollbar {
    height: 8px;
}

.movie-row::-webkit-scrollbar-thumb {
    background: #6d6d6e;
    border-radius: 4px;
}

.movie-card {
    min-width: 240px;
    cursor: pointer;
    transition: all 0.4s;
    position: relative;
    border-radius: 6px;
    overflow: hidden;
}

.movie-card:hover {
    transform: scale(1.15) translateY(-10px);
    z-index: 100;
}

.movie-card img {
    width: 100%;
    height: 360px;
    object-fit: cover;
}

.movie-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.3s;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 16px;
}

.movie-card:hover .movie-overlay {
    opacity: 1;
}

.movie-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
}

.movie-actions {
    display: flex;
    gap: 8px;
}

.icon-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.5);
    background: rgba(0,0,0,0.7);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.icon-btn.play {
    background: #fff;
    color: #000;
    border: none;
}

/* Comments Section */
.comments-section {
    background: var(--netflix-gray);
    padding: 30px;
    border-radius: 8px;
    margin-top: 20px;
}

.comments-section h3 {
    margin-bottom: 20px;
    font-size: 24px;
}

.comment-form {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
}

.comment-input {
    flex: 1;
    padding: 12px;
    background: #333;
    border: none;
    border-radius: 4px;
    color: #fff;
}

.comment-btn {
    padding: 12px 24px;
    background: var(--netflix-red);
    border: none;
    border-radius: 4px;
    color: #fff;
    cursor: pointer;
}

.comment-item {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 10px;
}

.comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.comment-author {
    font-weight: bold;
    color: var(--netflix-red);
}

.comment-date {
    font-size: 12px;
    color: #999;
}

.comment-text {
    color: #e5e5e5;
}

/* Modal */
.modal {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.85);
    z-index: 3000;
    align-items: center;
    justify-content: center;
}

.modal.show {
    display: flex;
}

.modal-content {
    background: var(--netflix-gray);
    border-radius: 8px;
    max-width: 900px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header-img {
    position: relative;
    height: 450px;
}

.modal-header-img::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, var(--netflix-gray) 0%, transparent 50%);
    z-index: 1;
}

.modal-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.modal-header-content {
    position: absolute;
    bottom: 30px;
    left: 40px;
    z-index: 2;
}

.modal-title {
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 15px;
}

.modal-buttons {
    display: flex;
    gap: 12px;
}

.close-modal-btn {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: rgba(0,0,0,0.8);
    border: none;
    color: #fff;
    font-size: 28px;
    cursor: pointer;
    z-index: 3;
}

.modal-body {
    padding: 30px 40px 40px;
}

.modal-description {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 20px;
}

/* Settings & Admin Panel */
.settings-panel {
    display: none;
    position: fixed;
    inset: 0;
    background: var(--netflix-black);
    z-index: 5000;
    overflow-y: auto;
    padding: 80px 50px 50px;
}

.settings-panel.show {
    display: block;
}

.settings-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 40px;
}

.settings-title {
    font-size: 36px;
    font-weight: bold;
}

.settings-section {
    background: var(--netflix-gray);
    padding: 30px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.settings-section h3 {
    font-size: 24px;
    margin-bottom: 20px;
    color: var(--netflix-red);
}

.setting-item {
    display: flex;
    justify-content: space-between;
    padding: 15px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.profile-input {
    width: 100%;
    padding: 12px;
    background: #333;
    border: none;
    border-radius: 4px;
    color: #fff;
    margin-bottom: 10px;
}

.user-list-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
    margin-bottom: 10px;
}

.user-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
    margin-left: 10px;
}

.badge-admin {
    background: var(--netflix-red);
}

.badge-moderator {
    background: #ffa500;
}

.badge-banned {
    background: #666;
    text-decoration: line-through;
}

/* My List & Profile Pages */
.my-list-page, .profile-page {
    display: none;
    padding: 120px 50px 50px;
    min-height: 100vh;
}

.my-list-page.show, .profile-page.show {
    display: block;
}

.page-title {
    font-size: 36px;
    font-weight: bold;
    margin-bottom: 30px;
}

.my-list-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 15px;
}

.profile-card {
    background: var(--netflix-gray);
    padding: 40px;
    border-radius: 8px;
    max-width: 600px;
    margin: 0 auto;
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 30px;
    margin-bottom: 30px;
}

.profile-avatar-large {
    width: 100px;
    height: 100px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--netflix-red), #ff4444);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    font-weight: bold;
}

.profile-info h2 {
    font-size: 32px;
    margin-bottom: 10px;
}

.profile-info p {
    color: #999;
}

.profile-section {
    margin-bottom: 25px;
}

.profile-section h3 {
    font-size: 20px;
    margin-bottom: 15px;
    color: var(--netflix-red);
}

/* Responsive */
@media (max-width: 768px) {
    .landing-logo { font-size: 48px; }
    .landing-slogan { font-size: 32px; }
    .landing-description { font-size: 18px; }
    .landing-features { flex-direction: column; gap: 15px; }
    .header { padding: 12px 20px; }
    .logo { font-size: 28px; }
    .nav { display: none; }
    .hero-slider { height: 70vh; }
    .hero-content { left: 20px; max-width: 90%; }
    .hero-title { font-size: 32px; }
    .category { padding: 12px 20px; }
    .movie-card { min-width: 160px; }
    .movie-card img { height: 240px; }
}
</style>
</head>
<body>

<!-- Landing Page -->
<div class="landing-page" id="landingPage">
    <div class="landing-bg">
"""
    
    for poster in landing_posters:
        html += f'        <img src="{poster["poster_file"]}" alt="{poster["title"]}">\n'
    
    html += """    </div>
    <div class="landing-overlay"></div>
    <div class="landing-content">
        <div class="landing-logo">HDFILMIZLE</div>
        <h1 class="landing-slogan">Sınırsız film, dizi ve çok daha fazlası</h1>
        <p class="landing-description">İstediğiniz zaman izleyin. İstediğiniz zaman iptal edin.</p>
        
        <div class="landing-features">
            <div class="feature-item">
                <span class="feature-icon">✓</span>
                <span>Ücretsiz İzle</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">✓</span>
                <span>HD Kalitede</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">✓</span>
                <span>Sınırsız İçerik</span>
            </div>
        </div>
        
        <div class="landing-buttons">
            <button class="landing-btn landing-btn-primary" onclick="showLoginScreen()">
                <span>🚀</span> Giriş Yap
            </button>
            <button class="landing-btn landing-btn-secondary" onclick="showRegisterScreen()">
                <span>📝</span> Kayıt Ol
            </button>
        </div>
    </div>
</div>

<!-- Login Screen -->
<div class="auth-screen" id="loginScreen">
    <div class="auth-box">
        <div class="auth-logo">HDFILMIZLE</div>
        <h1 class="auth-title">Oturum Aç</h1>
        <form onsubmit="login(event)">
            <div class="input-group">
                <input type="email" class="auth-input" placeholder="E-posta" required>
            </div>
            <div class="input-group">
                <input type="password" class="auth-input" placeholder="Şifre" required>
            </div>
            <button type="submit" class="auth-btn">Oturum Aç</button>
            <div class="auth-help">
                <label><input type="checkbox"> Beni hatırla</label>
                <a onclick="showHelp()">Yardım mı gerekiyor?</a>
            </div>
        </form>
        <div class="auth-footer">
            HDFilmizle'de yeni misiniz? <a onclick="showRegisterScreen()">Hemen kaydolun</a>.
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <a onclick="backToLanding()" style="color: #999; cursor: pointer;">← Ana Sayfaya Dön</a>
        </div>
    </div>
</div>

<!-- Register Screen -->
<div class="auth-screen" id="registerScreen">
    <div class="auth-box">
        <div class="auth-logo">HDFILMIZLE</div>
        <h1 class="auth-title">Kayıt Ol</h1>
        <form onsubmit="register(event)">
            <div class="input-group">
                <input type="text" class="auth-input" placeholder="Ad Soyad" required>
            </div>
            <div class="input-group">
                <input type="email" class="auth-input" placeholder="E-posta" required>
            </div>
            <div class="input-group">
                <input type="tel" class="auth-input" placeholder="Telefon Numarası">
            </div>
            <div class="input-group">
                <input type="password" class="auth-input" placeholder="Şifre (en az 6 karakter)" minlength="6" required>
            </div>
            <div class="input-group">
                <input type="password" class="auth-input" placeholder="Şifre Tekrar" minlength="6" required>
            </div>
            <button type="submit" class="auth-btn">Kayıt Ol</button>
        </form>
        <div class="auth-footer">
            Zaten hesabınız var mı? <a onclick="showLoginScreen()">Oturum açın</a>.
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <a onclick="backToLanding()" style="color: #999; cursor: pointer;">← Ana Sayfaya Dön</a>
        </div>
    </div>
</div>

<!-- Help Modal -->
<div class="help-modal" id="helpModal" onclick="closeHelp(event)">
    <div class="help-content" onclick="event.stopPropagation()">
        <h2>❓ Yardım ve Destek</h2>
        <p><strong>Şifrenizi mi unuttunuz?</strong></p>
        <p>Kayıtlı e-posta adresinize şifre sıfırlama bağlantısı gönderebiliriz.</p>
        <p><strong>Teknik destek:</strong></p>
        <p>📧 hdfilmizle.to@gmail.com<br>📱 WhatsApp: +90 555 123 4567</p>
        <button class="auth-btn" onclick="closeHelp()">Kapat</button>
    </div>
</div>

<!-- Main Content -->
<div id="mainContent" style="display:none;">

<header class="header" id="header">
    <div class="header-left">
        <a class="logo" onclick="showHome()">HDFILMIZLE</a>
        <nav class="nav">
            <a class="active" onclick="showHome()">Ana Sayfa</a>
            <a onclick="filterCategory('films')">Filmler</a>
            <a onclick="filterCategory('series')">Diziler</a>
            <a onclick="filterCategory('popular')">Yeni ve Popüler</a>
            <a onclick="showMyList()">Listem</a>
        </nav>
    </div>
    
    <div class="header-right">
        <div class="search-container">
            <button class="search-btn" onclick="toggleSearch()">🔍</button>
            <div class="search-box" id="searchBox">
                <input type="text" class="search-input" placeholder="Film, dizi ara..." id="searchInput" onkeyup="searchFilms()">
            </div>
        </div>
        
        <button class="notification-btn">
            🔔
            <span class="notification-badge">3</span>
            <div class="notification-dropdown">
                <div class="notification-item">
                    <strong>🆕 Yeni Dizi Eklendi!</strong>
                    <p style="margin: 5px 0 0 0; font-size: 13px;">Squid Game yayında</p>
                    <span style="font-size: 12px; color: #999;">2 saat önce</span>
                </div>
                <div class="notification-item">
                    <strong>⭐ İzleme Listeniz</strong>
                    <p style="margin: 5px 0 0 0; font-size: 13px;">5 yeni öneri var</p>
                    <span style="font-size: 12px; color: #999;">1 gün önce</span>
                </div>
                <div class="notification-item">
                    <strong>🎬 Haftalık Özel</strong>
                    <p style="margin: 5px 0 0 0; font-size: 13px;">En çok izlenen filmler</p>
                    <span style="font-size: 12px; color: #999;">3 gün önce</span>
                </div>
            </div>
        </button>
        
        <div class="profile-menu">
            <button class="profile-btn">
                <div class="profile-avatar" id="profileAvatar">K</div>
                <span>▼</span>
            </button>
            <div class="profile-dropdown">
                <div class="dropdown-item" onclick="showProfile()">👤 Profili Yönet</div>
                <div class="dropdown-item" onclick="showMyList()">⭐ Listem</div>
                <div class="dropdown-item" onclick="showSettings()">⚙️ Ayarlar</div>
                <div class="dropdown-item" id="adminPanelBtn" style="display:none;" onclick="showAdminPanel()">🔧 Admin Paneli</div>
                <div class="dropdown-item" id="modPanelBtn" style="display:none;" onclick="showAdminPanel()">🛡️ Moderatör Paneli</div>
                <div class="dropdown-divider"></div>
                <div class="dropdown-item" onclick="logout()">🚪 Çıkış Yap</div>
            </div>
        </div>
    </div>
</header>

<!-- Home Page -->
<div id="homePage">
<section class="hero-slider" id="heroSlider">
"""
    
    for idx, film in enumerate(hero_films):
        active_class = 'active' if idx == 0 else ''
        html += f"""    <div class="hero-slide {active_class}">
        <img src="{film['poster_file']}" alt="{film['title']}" class="hero-bg">
        <div class="hero-content">
            <h1 class="hero-title">{film['title']}</h1>
            <p class="hero-description">Yüksek kalitede izleme keyfini yaşayın. Binlerce film ve dizi arasından seçim yapın.</p>
            <div class="hero-buttons">
                <button class="btn btn-play" onclick="openFilm('{film['link']}')">▶ Oynat</button>
                <button class="btn btn-info" onclick="showModal({idx})">ℹ Bilgi</button>
            </div>
        </div>
    </div>
"""
    
    html += """    <div class="hero-nav">
"""
    for i in range(len(hero_films)):
        active_class = 'active' if i == 0 else ''
        html += f'        <div class="hero-dot {active_class}" onclick="goToSlide({i})"></div>\n'
    
    html += """    </div>
</section>

<div id="searchResults" style="display:none; padding: 20px 50px;">
    <h2 style="font-size: 24px; margin-bottom: 20px;">Arama Sonuçları</h2>
    <div id="searchGrid" class="movie-row"></div>
</div>

<div id="categories">
"""
    
    film_index = 0
    for category_name, category_films in categories.items():
        if not category_films:
            continue
            
        html += f"""<section class="category" data-category="{category_name}">
    <div class="category-header">
        <h2 class="category-title">{category_name}</h2>
        <a class="view-all">Tümünü Gör ›</a>
    </div>
    <div class="movie-row">
"""
        for film in category_films:
            html += f"""        <div class="movie-card" onclick="showModal({film_index})" data-title="{film['title']}">
            <img src="{film['poster_file']}" alt="{film['title']}">
            <div class="movie-overlay">
                <div class="movie-title">{film['title']}</div>
                <div class="movie-actions">
                    <button class="icon-btn play" onclick="event.stopPropagation(); openFilm('{film['link']}')">▶</button>
                    <button class="icon-btn" onclick="event.stopPropagation(); addToMyList({film_index})">+</button>
                    <button class="icon-btn" onclick="event.stopPropagation(); likeFilm({film_index})">👍</button>
                </div>
            </div>
        </div>
"""
            film_index += 1
        
        html += """    </div>
</section>
"""
    
    html += """</div>
</div>

<!-- My List Page -->
<div class="my-list-page" id="myListPage">
    <h1 class="page-title">📝 Listem</h1>
    <div class="my-list-grid" id="myListGrid">
        <p style="color: #999; font-size: 18px;">Listeniz boş. Film kartlarındaki '+' butonuna tıklayarak ekleyin!</p>
    </div>
</div>

<!-- Profile Page -->
<div class="profile-page" id="profilePage">
    <h1 class="page-title">👤 Profil Yönetimi</h1>
    <div class="profile-card">
        <div class="profile-header">
            <div class="profile-avatar-large">K</div>
            <div class="profile-info">
                <h2>Kullanıcı</h2>
                <p>kullanici@email.com</p>
            </div>
        </div>
        
        <div class="profile-section">
            <h3>Kişisel Bilgiler</h3>
            <input type="text" class="profile-input" placeholder="Ad Soyad" id="profileName">
            <input type="email" class="profile-input" placeholder="E-posta" id="profileEmail" readonly style="opacity: 0.6;">
            <input type="tel" class="profile-input" placeholder="Telefon" id="profilePhone">
        </div>
        
        <div class="profile-section">
            <h3>Şifre Değiştir</h3>
            <input type="password" class="profile-input" placeholder="Mevcut Şifre" id="currentPassword">
            <input type="password" class="profile-input" placeholder="Yeni Şifre" id="newPassword">
            <input type="password" class="profile-input" placeholder="Yeni Şifre Tekrar" id="newPasswordConfirm">
        </div>
        
        <button class="auth-btn" onclick="updateProfile()">Değişiklikleri Kaydet</button>
        <button class="auth-btn" style="background: #666; margin-top: 10px;" onclick="showHome()">Geri Dön</button>
    </div>
</div>

<!-- Settings Page -->
<div class="settings-panel" id="settingsPanel">
    <div class="settings-header">
        <h1 class="settings-title">⚙️ Ayarlar</h1>
        <button class="auth-btn" style="width: auto; padding: 12px 24px;" onclick="closeSettings()">Kapat</button>
    </div>
    
    <div class="settings-section">
        <h3>🎬 Oynatma Ayarları</h3>
        <div class="setting-item">
            <span>Otomatik Oynat</span>
            <span>Açık</span>
        </div>
        <div class="setting-item">
            <span>Video Kalitesi</span>
            <select style="background: #333; color: #fff; border: none; padding: 8px; border-radius: 4px;">
                <option>Otomatik</option>
                <option>1080p</option>
                <option>720p</option>
            </select>
        </div>
    </div>
</div>

<!-- Admin Panel -->
<div class="settings-panel" id="adminPanel">
    <div class="settings-header">
        <h1 class="settings-title">🔧 Yönetici Paneli</h1>
        <button class="auth-btn" style="width: auto; padding: 12px 24px;" onclick="closeAdminPanel()">Kapat</button>
    </div>
    
    <!-- Film Ekleme -->
    <div class="settings-section">
        <h3>➕ Yeni Film Ekle</h3>
        <input type="text" id="adminFilmTitle" class="profile-input" placeholder="Film Adı">
        <input type="url" id="adminFilmPoster" class="profile-input" placeholder="Poster URL">
        <input type="url" id="adminFilmLink" class="profile-input" placeholder="HDFilmizle.life Linki">
        <button class="auth-btn" onclick="addFilmByAdmin()">Film Ekle</button>
    </div>
    
    <!-- Film Listesi -->
    <div class="settings-section">
        <h3>🎬 Tüm Filmler (<span id="totalFilmsCount">0</span>)</h3>
        <input type="text" id="adminSearchInput" class="profile-input" placeholder="Film ara..." onkeyup="filterAdminFilms()">
        <div id="adminFilmsList" style="max-height: 400px; overflow-y: auto;"></div>
    </div>
    
    <!-- Kullanıcı Yönetimi (Sadece Admin) -->
    <div class="settings-section" id="userManagementSection">
        <h3>👥 Kullanıcı Yönetimi</h3>
        <input type="text" id="userSearchInput" class="profile-input" placeholder="Kullanıcı ara (e-posta veya ad)..." onkeyup="filterUsers()">
        <div id="usersList" style="max-height: 500px; overflow-y: auto;"></div>
    </div>
</div>

<!-- Modal -->
<div id="modal" class="modal" onclick="closeModal(event)">
    <div class="modal-content" onclick="event.stopPropagation()">
        <button class="close-modal-btn" onclick="closeModal()">×</button>
        <div class="modal-header-img">
            <img id="modalImg" src="" alt="" class="modal-img">
            <div class="modal-header-content">
                <h2 id="modalTitle" class="modal-title"></h2>
                <div class="modal-buttons">
                    <button class="btn btn-play" id="modalPlayBtn">▶ Oynat</button>
                    <button class="btn btn-info" style="background: rgba(255,255,255,0.2);" id="modalAddBtn">+ Listem</button>
                </div>
            </div>
        </div>
        <div class="modal-body">
            <p class="modal-description">Muhteşem görselliği, etkileyici oyunculuğu ve sürükleyici hikayesiyle izleyicileri büyüleyen bu yapım.</p>
            
            <!-- Yorumlar -->
            <div class="comments-section">
                <h3>💬 Yorumlar (<span id="commentCount">0</span>)</h3>
                <div class="comment-form">
                    <input type="text" id="commentInput" class="comment-input" placeholder="Yorumunuzu yazın...">
                    <button class="comment-btn" onclick="addComment()">Gönder</button>
                </div>
                <div id="commentsContainer"></div>
            </div>
        </div>
    </div>
</div>

</div>

<script>
const allFilms = [
"""
    
    for film in films:
        title_escaped = film['title'].replace('"', '\\"').replace("'", "\\'")
        html += f"""    {{title: "{title_escaped}", poster: "{film['poster_file']}", link: "{film['link']}"}},
"""
    
    html += """];

let myList = [];
let currentUser = null;
let isLoggedIn = false;
let isAdmin = false;
let isModerator = false;
let currentFilmIndex = null;

const ADMIN_EMAIL = 'admin@hdfilmizle.life';

// LocalStorage Functions
function getUsers() {
    const users = localStorage.getItem('hdfilmizle_users');
    return users ? JSON.parse(users) : [];
}

function saveUser(user) {
    const users = getUsers();
    users.push(user);
    localStorage.setItem('hdfilmizle_users', JSON.stringify(users));
}

function updateUser(email, updates) {
    const users = getUsers();
    const index = users.findIndex(u => u.email === email);
    if (index !== -1) {
        users[index] = { ...users[index], ...updates };
        localStorage.setItem('hdfilmizle_users', JSON.stringify(users));
    }
}

function findUser(email, password) {
    const users = getUsers();
    return users.find(u => u.email === email && u.password === password);
}

function loadFilms() {
    const saved = localStorage.getItem('hdfilmizle_films');
    if (saved) {
        const parsed = JSON.parse(saved);
        allFilms.length = 0;
        allFilms.push(...parsed);
    }
}

function saveFilms() {
    localStorage.setItem('hdfilmizle_films', JSON.stringify(allFilms));
}

function getComments(filmTitle) {
    const comments = localStorage.getItem('hdfilmizle_comments');
    const all = comments ? JSON.parse(comments) : {};
    return all[filmTitle] || [];
}

function saveComment(filmTitle, comment) {
    const comments = localStorage.getItem('hdfilmizle_comments');
    const all = comments ? JSON.parse(comments) : {};
    if (!all[filmTitle]) all[filmTitle] = [];
    all[filmTitle].push(comment);
    localStorage.setItem('hdfilmizle_comments', JSON.stringify(all));
}

loadFilms();

// Landing & Auth Functions
function showLoginScreen() {
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('loginScreen').classList.add('show');
}

function showRegisterScreen() {
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('registerScreen').classList.add('show');
}

function backToLanding() {
    document.getElementById('loginScreen').classList.remove('show');
    document.getElementById('registerScreen').classList.remove('show');
    document.getElementById('landingPage').style.display = 'flex';
}

function showHelp() {
    document.getElementById('helpModal').classList.add('show');
}

function closeHelp(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('helpModal').classList.remove('show');
}

function login(e) {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;
    const password = e.target.querySelector('input[type="password"]').value;
    
    const user = findUser(email, password);
    
    if (!user) {
        alert('❌ E-posta veya şifre hatalı!');
        return;
    }
    
    // Ban kontrolü
    if (user.bannedUntil && new Date(user.bannedUntil) > new Date()) {
        const days = Math.ceil((new Date(user.bannedUntil) - new Date()) / (1000 * 60 * 60 * 24));
        alert(`🚫 Hesabınız ${days} gün boyunca yasaklandı!`);
        return;
    }
    
    currentUser = email;
    isLoggedIn = true;
    isAdmin = (email === ADMIN_EMAIL) || user.role === 'admin';
    isModerator = user.role === 'moderator' || isAdmin;
    
    if (isAdmin) {
        document.getElementById('adminPanelBtn').style.display = 'flex';
    } else if (isModerator) {
        document.getElementById('modPanelBtn').style.display = 'flex';
    }
    
    const userName = user.name || email.split('@')[0];
    document.getElementById('profileAvatar').textContent = userName.charAt(0).toUpperCase();
    document.querySelector('.profile-info h2').textContent = userName;
    document.querySelector('.profile-info p').textContent = email;
    document.querySelector('#profileName').value = userName;
    document.querySelector('#profileEmail').value = email;
    document.querySelector('#profilePhone').value = user.phone || '';
    
    if (user.myList) myList = user.myList;
    
    document.getElementById('loginScreen').classList.remove('show');
    document.getElementById('mainContent').style.display = 'block';
    
    alert(`${isAdmin ? '👑 Admin' : isModerator ? '🛡️ Moderatör' : '✅'} Hoş geldiniz, ${userName}!`);
    
    setTimeout(() => startHeroSlider(), 100);
}

function register(e) {
    e.preventDefault();
    const name = e.target.querySelector('input[type="text"]').value.trim();
    const email = e.target.querySelector('input[type="email"]').value.trim();
    const phone = e.target.querySelector('input[type="tel"]').value.trim();
    const password = e.target.querySelectorAll('input[type="password"]')[0].value;
    const passwordConfirm = e.target.querySelectorAll('input[type="password"]')[1].value;
    
    if (!name || name.length < 3) {
        alert('❌ Ad Soyad en az 3 karakter olmalıdır!');
        return;
    }
    
    if (password.length < 6) {
        alert('❌ Şifre en az 6 karakter olmalıdır!');
        return;
    }
    
    if (password !== passwordConfirm) {
        alert('❌ Şifreler eşleşmiyor!');
        return;
    }
    
    const users = getUsers();
    if (users.some(u => u.email === email)) {
        alert('❌ Bu e-posta zaten kayıtlı!');
        return;
    }
    
    const newUser = {
        name, email, phone, password,
        role: 'user',
        myList: [],
        createdAt: new Date().toISOString()
    };
    
    saveUser(newUser);
    alert(`✅ Kayıt başarılı! Hoş geldiniz ${name}!`);
    e.target.reset();
    showLoginScreen();
}

function logout() {
    if (confirm('Çıkış yapmak istediğinizden emin misiniz?')) {
        if (currentUser) {
            updateUser(currentUser, { myList });
        }
        currentUser = null;
        isLoggedIn = false;
        isAdmin = false;
        isModerator = false;
        myList = [];
        document.getElementById('adminPanelBtn').style.display = 'none';
        document.getElementById('modPanelBtn').style.display = 'none';
        document.getElementById('mainContent').style.display = 'none';
        document.getElementById('landingPage').style.display = 'flex';
        alert('👋 Çıkış yapıldı!');
    }
}

// Navigation
function showHome() {
    document.getElementById('homePage').style.display = 'block';
    document.getElementById('myListPage').classList.remove('show');
    document.getElementById('profilePage').classList.remove('show');
    document.getElementById('settingsPanel').classList.remove('show');
    document.getElementById('adminPanel').classList.remove('show');
    document.querySelectorAll('.category').forEach(cat => cat.style.display = 'block');
    document.querySelectorAll('.nav a').forEach(a => a.classList.remove('active'));
    document.querySelector('.nav a').classList.add('active');
    window.scrollTo(0, 0);
}

function filterCategory(type) {
    showHome();
    const categories = document.querySelectorAll('.category');
    event.target.classList.add('active');
    
    if (type === 'films') {
        categories.forEach(cat => {
            const title = cat.querySelector('.category-title').textContent.toLowerCase();
            cat.style.display = title.includes('film') || title.includes('aksiyon') || title.includes('komedi') || title.includes('drama') || title.includes('korku') || title.includes('imdb') || title.includes('türkiye') ? 'block' : 'none';
        });
    } else if (type === 'series') {
        categories.forEach(cat => {
            const title = cat.querySelector('.category-title').textContent.toLowerCase();
            cat.style.display = title.includes('yeni') || title.includes('popüler') ? 'block' : 'none';
        });
    } else if (type === 'popular') {
        categories.forEach(cat => {
            const title = cat.querySelector('.category-title').textContent.toLowerCase();
            cat.style.display = title.includes('popüler') || title.includes('yeni') || title.includes('imdb') ? 'block' : 'none';
        });
    }
    window.scrollTo(0, 600);
}

function showMyList() {
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('myListPage').classList.add('show');
    document.getElementById('profilePage').classList.remove('show');
    document.getElementById('settingsPanel').classList.remove('show');
    document.getElementById('adminPanel').classList.remove('show');
    renderMyList();
    window.scrollTo(0, 0);
}

function showProfile() {
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('myListPage').classList.remove('show');
    document.getElementById('profilePage').classList.add('show');
    document.getElementById('settingsPanel').classList.remove('show');
    document.getElementById('adminPanel').classList.remove('show');
    window.scrollTo(0, 0);
}

function showSettings() {
    document.getElementById('settingsPanel').classList.add('show');
    document.getElementById('adminPanel').classList.remove('show');
}

function closeSettings() {
    document.getElementById('settingsPanel').classList.remove('show');
}

// Admin Panel
function showAdminPanel() {
    if (!isAdmin && !isModerator) {
        alert('❌ Yetkiniz yok!');
        return;
    }
    
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('myListPage').classList.remove('show');
    document.getElementById('profilePage').classList.remove('show');
    document.getElementById('settingsPanel').classList.remove('show');
    document.getElementById('adminPanel').classList.add('show');
    
    // Kullanıcı yönetimi sadece admin için
    document.getElementById('userManagementSection').style.display = isAdmin ? 'block' : 'none';
    
    renderAdminFilmsList();
    if (isAdmin) renderUsersList();
    window.scrollTo(0, 0);
}

function closeAdminPanel() {
    document.getElementById('adminPanel').classList.remove('show');
    showHome();
}

function addFilmByAdmin() {
    const title = document.getElementById('adminFilmTitle').value.trim();
    const poster = document.getElementById('adminFilmPoster').value.trim();
    const link = document.getElementById('adminFilmLink').value.trim();
    
    if (!title || !poster || !link) {
        alert('❌ Tüm alanları doldurun!');
        return;
    }
    
    if (!link.includes('hdfilmizle.life')) {
        alert('❌ Link hdfilmizle.life sitesinden olmalıdır!');
        return;
    }
    
    if (allFilms.some(f => f.title === title)) {
        alert('❌ Bu film zaten listede!');
        return;
    }
    
    allFilms.unshift({ title, poster, link });
    saveFilms();
    
    document.getElementById('adminFilmTitle').value = '';
    document.getElementById('adminFilmPoster').value = '';
    document.getElementById('adminFilmLink').value = '';
    
    alert(`✅ "${title}" eklendi!`);
    renderAdminFilmsList();
    location.reload();
}

function deleteFilmByAdmin(index) {
    const film = allFilms[index];
    if (confirm(`"${film.title}" silinecek. Emin misiniz?`)) {
        allFilms.splice(index, 1);
        saveFilms();
        alert(`🗑️ "${film.title}" silindi!`);
        renderAdminFilmsList();
        location.reload();
    }
}

function renderAdminFilmsList() {
    const container = document.getElementById('adminFilmsList');
    document.getElementById('totalFilmsCount').textContent = allFilms.length;
    
    if (allFilms.length === 0) {
        container.innerHTML = '<p style="color: #999; text-align: center;">Henüz film eklenmemiş.</p>';
        return;
    }
    
    container.innerHTML = '';
    allFilms.forEach((film, index) => {
        const item = document.createElement('div');
        item.className = 'user-list-item';
        item.innerHTML = `
            <div style="display: flex; align-items: center; gap: 15px;">
                <img src="${film.poster}" alt="${film.title}" style="width: 60px; height: 90px; object-fit: cover; border-radius: 4px;">
                <div>
                    <strong>${film.title}</strong>
                    <p style="font-size: 12px; color: #999; margin-top: 5px;">${film.link}</p>
                </div>
            </div>
            <button onclick="deleteFilmByAdmin(${index})" class="auth-btn" style="width: auto; padding: 8px 16px; background: #dc3545; margin: 0;">Sil</button>
        `;
        container.appendChild(item);
    });
}

function filterAdminFilms() {
    const query = document.getElementById('adminSearchInput').value.toLowerCase();
    const items = document.querySelectorAll('#adminFilmsList .user-list-item');
    items.forEach(item => {
        const title = item.querySelector('strong').textContent.toLowerCase();
        item.style.display = title.includes(query) ? 'flex' : 'none';
    });
}

// User Management (Admin only)
function renderUsersList() {
    const container = document.getElementById('usersList');
    const users = getUsers();
    
    container.innerHTML = '';
    users.forEach(user => {
        const item = document.createElement('div');
        item.className = 'user-list-item';
        
        const badges = [];
        if (user.email === ADMIN_EMAIL || user.role === 'admin') badges.push('<span class="user-badge badge-admin">ADMIN</span>');
        if (user.role === 'moderator') badges.push('<span class="user-badge badge-moderator">MODERATÖR</span>');
        if (user.bannedUntil && new Date(user.bannedUntil) > new Date()) badges.push('<span class="user-badge badge-banned">BANLI</span>');
        
        item.innerHTML = `
            <div>
                <strong>${user.name}</strong> ${badges.join(' ')}
                <p style="font-size: 12px; color: #999; margin-top: 5px;">${user.email}</p>
            </div>
            <div style="display: flex; gap: 8px;">
                ${user.email !== ADMIN_EMAIL && user.role !== 'admin' ? `
                    ${user.role === 'moderator' ? 
                        `<button onclick="removeModerator('${user.email}')" class="auth-btn" style="width: auto; padding: 8px 12px; background: #ff9800; margin: 0;">Moderatörlüğü Kaldır</button>` :
                        `<button onclick="makeModerator('${user.email}')" class="auth-btn" style="width: auto; padding: 8px 12px; background: #4caf50; margin: 0;">Moderatör Yap</button>`
                    }
                    <button onclick="banUser('${user.email}')" class="auth-btn" style="width: auto; padding: 8px 12px; background: #dc3545; margin: 0;">Banla</button>
                ` : ''}
            </div>
        `;
        container.appendChild(item);
    });
}

function filterUsers() {
    const query = document.getElementById('userSearchInput').value.toLowerCase();
    const items = document.querySelectorAll('#usersList .user-list-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? 'flex' : 'none';
    });
}

function makeModerator(email) {
    updateUser(email, { role: 'moderator' });
    alert(`✅ ${email} artık moderatör!`);
    renderUsersList();
}

function removeModerator(email) {
    updateUser(email, { role: 'user' });
    alert(`✅ ${email} moderatörlükten çıkarıldı!`);
    renderUsersList();
}

function banUser(email) {
    const days = prompt('Kaç gün banlanacak? (1, 5, 7, 30, 365)', '1');
    if (!days) return;
    
    const bannedUntil = new Date();
    bannedUntil.setDate(bannedUntil.getDate() + parseInt(days));
    
    updateUser(email, { bannedUntil: bannedUntil.toISOString() });
    alert(`🚫 ${email} ${days} gün banlandı!`);
    renderUsersList();
}

// Hero Slider
let currentSlide = 0;
let sliderInterval;

function startHeroSlider() {
    sliderInterval = setInterval(() => {
        currentSlide = (currentSlide + 1) % """ + str(len(hero_films)) + """;
        goToSlide(currentSlide);
    }, 8000);
}

function goToSlide(index) {
    currentSlide = index;
    const slides = document.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.hero-dot');
    
    slides.forEach((slide, i) => slide.classList.toggle('active', i === index));
    dots.forEach((dot, i) => dot.classList.toggle('active', i === index));
    
    clearInterval(sliderInterval);
    startHeroSlider();
}

// Search
let searchActive = false;

function toggleSearch() {
    searchActive = !searchActive;
    const searchBox = document.getElementById('searchBox');
    
    if (searchActive) {
        searchBox.classList.add('active');
        document.getElementById('searchInput').focus();
    } else {
        searchBox.classList.remove('active');
        document.getElementById('searchInput').value = '';
        document.getElementById('searchResults').style.display = 'none';
        document.getElementById('categories').style.display = 'block';
    }
}

function searchFilms() {
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    const searchResults = document.getElementById('searchResults');
    const searchGrid = document.getElementById('searchGrid');
    const categories = document.getElementById('categories');
    
    if (query.length < 2) {
        searchResults.style.display = 'none';
        categories.style.display = 'block';
        return;
    }
    
    const seen = new Set();
    const results = allFilms.filter(film => {
        if (film.title.toLowerCase().includes(query) && !seen.has(film.title)) {
            seen.add(film.title);
            return true;
        }
        return false;
    });
    
    searchGrid.innerHTML = '';
    
    if (results.length === 0) {
        searchGrid.innerHTML = '<p style="color: #999;">Sonuç bulunamadı.</p>';
    } else {
        results.forEach(film => {
            const filmIndex = allFilms.findIndex(f => f.title === film.title);
            searchGrid.innerHTML += `
                <div class="movie-card" onclick="showModal(${filmIndex})">
                    <img src="${film.poster}" alt="${film.title}">
                    <div class="movie-overlay">
                        <div class="movie-title">${film.title}</div>
                        <div class="movie-actions">
                            <button class="icon-btn play" onclick="event.stopPropagation(); openFilm('${film.link}')">▶</button>
                            <button class="icon-btn" onclick="event.stopPropagation(); addToMyList(${filmIndex})">+</button>
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    searchResults.style.display = 'block';
    categories.style.display = 'none';
}

// My List
function addToMyList(index) {
    if (!isLoggedIn) {
        alert('❌ Lütfen önce giriş yapın!');
        return;
    }
    const film = allFilms[index];
    if (!myList.some(f => f.title === film.title)) {
        myList.push(film);
        updateUser(currentUser, { myList });
        alert(`✅ "${film.title}" listenize eklendi!`);
    } else {
        alert(`ℹ️ "${film.title}" zaten listenizde!`);
    }
}

function removeFromMyList(title) {
    myList = myList.filter(f => f.title !== title);
    updateUser(currentUser, { myList });
    renderMyList();
    alert('🗑️ Film listenizden kaldırıldı!');
}

function renderMyList() {
    const grid = document.getElementById('myListGrid');
    
    if (myList.length === 0) {
        grid.innerHTML = '<p style="color: #999; font-size: 18px;">Listeniz boş.</p>';
        return;
    }
    
    grid.innerHTML = '';
    myList.forEach(film => {
        const filmIndex = allFilms.findIndex(f => f.title === film.title);
        grid.innerHTML += `
            <div class="movie-card" onclick="showModal(${filmIndex})">
                <img src="${film.poster}" alt="${film.title}">
                <div class="movie-overlay">
                    <div class="movie-title">${film.title}</div>
                    <div class="movie-actions">
                        <button class="icon-btn play" onclick="event.stopPropagation(); openFilm('${film.link}')">▶</button>
                        <button class="icon-btn" onclick="event.stopPropagation(); removeFromMyList('${film.title.replace(/'/g, "\\'")}')">🗑️</button>
                    </div>
                </div>
            </div>
        `;
    });
}

function likeFilm(index) {
    const film = allFilms[index];
    alert(`"${film.title}" beğenildi! ❤️`);
}

function updateProfile() {
    if (!isLoggedIn) {
        alert('❌ Lütfen önce giriş yapın!');
        return;
    }
    
    const name = document.getElementById('profileName').value.trim();
    const phone = document.getElementById('profilePhone').value.trim();
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const newPasswordConfirm = document.getElementById('newPasswordConfirm').value;
    
    const users = getUsers();
    const user = users.find(u => u.email === currentUser);
    
    if (!user) {
        alert('❌ Kullanıcı bulunamadı!');
        return;
    }
    
    if (currentPassword || newPassword || newPasswordConfirm) {
        if (currentPassword !== user.password) {
            alert('❌ Mevcut şifre yanlış!');
            return;
        }
        
        if (newPassword.length < 6) {
            alert('❌ Yeni şifre en az 6 karakter olmalıdır!');
            return;
        }
        
        if (newPassword !== newPasswordConfirm) {
            alert('❌ Yeni şifreler eşleşmiyor!');
            return;
        }
        
        updateUser(currentUser, { name, phone, password: newPassword });
        
        document.getElementById('currentPassword').value = '';
        document.getElementById('newPassword').value = '';
        document.getElementById('newPasswordConfirm').value = '';
        
        alert('✅ Profil ve şifre güncellendi!');
    } else {
        updateUser(currentUser, { name, phone });
        alert('✅ Profil bilgileri güncellendi!');
    }
    
    document.querySelector('.profile-info h2').textContent = name;
    document.getElementById('profileAvatar').textContent = name.charAt(0).toUpperCase();
}

// Modal & Comments
function showModal(index) {
    const film = allFilms[index];
    if (!film) return;
    
    currentFilmIndex = index;
    
    document.getElementById('modalImg').src = film.poster;
    document.getElementById('modalTitle').textContent = film.title;
    document.getElementById('modalPlayBtn').onclick = () => openFilm(film.link);
    document.getElementById('modalAddBtn').onclick = () => addToMyList(index);
    document.getElementById('modal').classList.add('show');
    document.body.style.overflow = 'hidden';
    
    renderComments(film.title);
}

function closeModal(event) {
    if (event && event.target !== event.currentTarget && !event.target.classList.contains('close-modal-btn')) return;
    document.getElementById('modal').classList.remove('show');
    document.body.style.overflow = 'auto';
    currentFilmIndex = null;
}

function openFilm(link) {
    window.open(link, '_blank');
}

function renderComments(filmTitle) {
    const comments = getComments(filmTitle);
    const container = document.getElementById('commentsContainer');
    document.getElementById('commentCount').textContent = comments.length;
    
    if (comments.length === 0) {
        container.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Henüz yorum yok. İlk yorumu siz yapın!</p>';
        return;
    }
    
    container.innerHTML = '';
    comments.forEach(comment => {
        const div = document.createElement('div');
        div.className = 'comment-item';
        div.innerHTML = `
            <div class="comment-header">
                <span class="comment-author">${comment.author}</span>
                <span class="comment-date">${new Date(comment.date).toLocaleDateString('tr-TR')}</span>
            </div>
            <p class="comment-text">${comment.text}</p>
        `;
        container.appendChild(div);
    });
}

function addComment() {
    if (!isLoggedIn) {
        alert('❌ Yorum yapmak için giriş yapın!');
        return;
    }
    
    const input = document.getElementById('commentInput');
    const text = input.value.trim();
    
    if (!text) {
        alert('❌ Yorum boş olamaz!');
        return;
    }
    
    if (currentFilmIndex === null) return;
    
    const film = allFilms[currentFilmIndex];
    const users = getUsers();
    const user = users.find(u => u.email === currentUser);
    
    const comment = {
        author: user?.name || 'Anonim',
        text: text,
        date: new Date().toISOString()
    };
    
    saveComment(film.title, comment);
    input.value = '';
    renderComments(film.title);
    alert('✅ Yorumunuz eklendi!');
}

// Header scroll
window.addEventListener('scroll', () => {
    const header = document.getElementById('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        closeHelp();
        if (searchActive) toggleSearch();
    }
});

console.log('🎬 HDFilmizle yüklendi!');
console.log(`📊 ${allFilms.length} film mevcut`);
</script>
</body>
</html>
"""
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] {INDEX_FILE} oluşturuldu.")

if __name__ == "__main__":
    print("="*60)
    print("🎬 HDFilmizle Netflix Clone")
    print("="*60)
    
    all_films = []
    seen_titles = set()
    
    for page in range(1, TOTAL_PAGES+1):
        print(f"\n[📄] Sayfa {page}/{TOTAL_PAGES} çekiliyor...")
        html = fetch_page(page)
        if not html:
            continue
        films = parse_films(html)
        if films:
            unique_films = [f for f in films if f['title'] not in seen_titles]
            for f in unique_films:
                seen_titles.add(f['title'])
            all_films.extend(unique_films)
            print(f"    ✓ {len(unique_films)} film bulundu")
    
    if not all_films:
        print("\n[!] Film bulunamadı.")
        exit(1)
    
    print(f"\n{'='*60}")
    print(f"[✓] {len(all_films)} film bulundu")
    print(f"{'='*60}\n")
    
    print("[📥] Posterler indiriliyor...")
    download_posters(all_films)
    
    print(f"\n{'='*60}")
    print("[🎨] HTML oluşturuluyor...")
    generate_netflix_html(all_films)
    
    print(f"{'='*60}")
    print("✅ Tamamlandı!")
    print(f"📂 {INDEX_FILE} dosyasını açın")
    print(f"🎬 {len(all_films)} film hazır!")
    print(f"{'='*60}")