import asyncio
import sqlite3
import time
import random
import threading
import html
import urllib.parse
import os
import base64
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============ SUPABASE ============
from supabase import create_client, Client
from supabase.client import ClientOptions

SUPABASE_URL = "https://poxhawnlrqjvpqjliauaa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBveGhhd25scnFqdnBxbGlhdWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI1NjU3MjQsImV4cCI6MjEwODE0MTcyNH0.8VRo_yJwSUleT6GuEQDaRUxbVy_hQZddxL7E9RlDIow"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=ClientOptions(postgrest_client_timeout=30))

def sync_to_supabase(user_id):
    try:
        u = get_user(user_id)
        businesses = get_user_businesses(user_id)
        pets = get_user_pets(user_id)
        
        data = {
            "user_id": user_id,
            "nickname": u["nickname"],
            "balance": u["balance"],
            "rating": u["rating"],
            "vip_level": u["vip_level"],
            "neitcoins": u["neitcoins"],
            "business_level": sum(b["level"] for b in businesses),
            "pet_name": ", ".join(p["pet_name"] for p in pets) if pets else None,
            "pet_type": ", ".join(p["pet_type"] for p in pets) if pets else None,
            "avatar_url": None
        }
        supabase.table("players").upsert(data).execute()
    except Exception:
        pass

# ==================================

TOKEN = "8957645798:AAE0CExSEJk0jHoBkdc3LTVUHBFwucrx2yA"
ADMIN_ID = 1791177759
AWARD_PRICE = 100

BUSINESS_PRICE = 10_000
BUSINESS_BASE_SALARY = 60_000
BUSINESS_SALARY_PER_LEVEL = 60_000
BUSINESS_TAX = 50_000
BUSINESS_TAX_COOLDOWN = 2 * 60 * 60
BUSINESS_SALARY_COOLDOWN = 60 * 60
LEAF_COOLDOWN = 60 * 60
LEAF_MIN = 15
LEAF_MAX = 50
LEAVES_PER_LEVEL = 10
MAX_LEVEL = 1000

FARM_COOLDOWN = 60 * 60
FARM_MIN = 10
FARM_MAX = 200

BOT_BIRTHDAY = time.mktime(time.strptime("2026-09-22", "%Y-%m-%d"))

# ============ ПРЕМИУМ ЭМОДЗИ (ID) ============
PE_PROFILE = "5258515188490984344"
PE_NICK = "5235612653342177821"
PE_AVATAR = "5438416430624175981"
PE_RANK = "5794262515571498193"
PE_TOP_PLACE = "5771711424711626153"
PE_MAX = "5870984877884576308"
PE_BALANCE = "5188527446567195506"
PE_NEITCOINS = "4999002445444023072"
PE_VIP = "5228879463177019590"
PE_STREAK = "5366340737594051897"
PE_BIZ = "5258500422393415126"
PE_STAT = "5278778882848220741"
PE_WINS = "5318974936310627698"
PE_EARNED = "5215706742645599766"
PE_RING = "5285062991232922797"
PE_GIFT = "5893406892092297627"
PE_HEART = "5893406892092297627"
PE_BEAR = "5258056932660367858"
PE_AWARDS = "5440539497383087970"
# ===========================================

# ============ VIP СИСТЕМА ============
VIP_LEVELS = {
    1: {"name": "🥉 VIP Бронза", "price": 10, "bonus": 2},
    2: {"name": "🥈 VIP Серебро", "price": 30, "bonus": 3},
    3: {"name": "🥇 VIP Золото", "price": 100, "bonus": 15},
    4: {"name": "💎 VIP Платина", "price": 300, "bonus": 20},
    5: {"name": "👑 VIP Бриллиант", "price": 1000, "bonus": 40},
}

MAX_PETS_LIMITS = {0: 1, 1: 1, 2: 2, 3: 2, 4: 2, 5: 6}
MAX_BIZ_LIMITS = {0: 1, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2}

# ============ ПОДАРКИ ============
GIFTS = {
    "роза":       {"emoji": f'<tg-emoji emoji-id="{PE_HEART}">🌹</tg-emoji>', "name": "Роза",       "price": 500},
    "сердечко":   {"emoji": f'<tg-emoji emoji-id="{PE_HEART}">💗</tg-emoji>', "name": "Сердечко",   "price": 1000},
    "поцелуйчик": {"emoji": "💋", "name": "Поцелуйчик", "price": 1500},
    "мишка":      {"emoji": f'<tg-emoji emoji-id="{PE_BEAR}">🧸</tg-emoji>', "name": "Мишка",      "price": 2500},
    "кольцо":     {"emoji": f'<tg-emoji emoji-id="{PE_RING}">💍</tg-emoji>', "name": "Кольцо",     "price": 3500},
}

# ============ ПИТОМЦЫ ============
PET_INTERACT_COOLDOWN = 30 * 60
PET_PETS = {
    "fox":     {"emoji": "🦊", "name": "Лиса",   "desc": "Хитрая и пушистая"},
    "cat":     {"emoji": "🐱", "name": "Кошка",  "desc": "Мурлыкающая и ласковая"},
    "hamster": {"emoji": "🐹", "name": "Хомяк",  "desc": "Пухленький и запасливый"},
    "dog":     {"emoji": "🐶", "name": "Собака", "desc": "Верный друг"},
    "weasel":  {"emoji": "🦡", "name": "Ласка",  "desc": "Ловкая и игривая"},
    "ferret":  {"emoji": "🦦", "name": "Хорёк",  "desc": "Весёлый и озорной"},
}

def fmt(n):
    try:
        n = int(n)
    except (ValueError, TypeError):
        return str(n)
    if abs(n) < 10000:
        return str(n)
    return f"{n:,}".replace(",", ".")

# ============ БАЗА ============
# КОСТЫЛЬ ДЛЯ ВОССТАНОВЛЕНИЯ БАЗЫ НА RENDER
if os.path.exists("users_db.txt") and not os.path.exists("users.db"):
    try:
        with open("users_db.txt", "r", encoding="utf-8") as f:
            b64_data = f.read()
        with open("users.db", "wb") as f:
            f.write(base64.b64decode(b64_data))
    except Exception as e:
        print(f"Ошибка восстановления базы: {e}")

db = sqlite3.connect("users.db", check_same_thread=False)
cursor = db.cursor()
db_lock = threading.Lock()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        nickname TEXT,
        avatar TEXT DEFAULT 'default',
        custom_avatar_file_id TEXT DEFAULT NULL,
        last_daily REAL DEFAULT 0,
        last_work REAL DEFAULT 0,
        daily_streak INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        total_earned INTEGER DEFAULT 0,
        vip INTEGER DEFAULT 0,
        rating INTEGER DEFAULT 0,
        custom_avatar_allowed INTEGER DEFAULT 0,
        neitcoins INTEGER DEFAULT 0,
        vip_level INTEGER DEFAULT 0,
        last_farm REAL DEFAULT 0
    )
""")
db.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS businesses_v2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        level INTEGER DEFAULT 0,
        leaves INTEGER DEFAULT 0,
        tax_debt INTEGER DEFAULT 0,
        last_salary REAL DEFAULT 0,
        last_tax REAL DEFAULT 0,
        last_leaf REAL DEFAULT 0
    )
""")
db.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS pets_v2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        pet_type TEXT,
        pet_name TEXT,
        love INTEGER DEFAULT 0,
        trust INTEGER DEFAULT 0,
        hunger INTEGER DEFAULT 100,
        born_at REAL DEFAULT 0,
        last_feed REAL DEFAULT 0,
        last_pet REAL DEFAULT 0,
        last_play REAL DEFAULT 0,
        last_hunger_update REAL DEFAULT 0
    )
""")
db.commit()

# МИГРАЦИЯ СТАРЫХ ТАБЛИЦ
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='business'")
    if cursor.fetchone():
        cursor.execute("SELECT user_id, level, leaves, tax_debt, last_salary, last_tax, last_leaf FROM business")
        for b in cursor.fetchall():
            cursor.execute("INSERT INTO businesses_v2 (user_id, level, leaves, tax_debt, last_salary, last_tax, last_leaf) VALUES (?, ?, ?, ?, ?, ?, ?)", b)
        cursor.execute("DROP TABLE business")
        db.commit()
except: pass

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pets'")
    if cursor.fetchone():
        cursor.execute("SELECT user_id, pet_type, pet_name, love, trust, hunger, born_at, last_feed, last_pet, last_play, last_hunger_update FROM pets")
        for p in cursor.fetchall():
            cursor.execute("INSERT INTO pets_v2 (user_id, pet_type, pet_name, love, trust, hunger, born_at, last_feed, last_pet, last_play, last_hunger_update) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", p)
        cursor.execute("DROP TABLE pets")
        db.commit()
except: pass

cursor.execute("""
    CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        gift_key TEXT,
        from_user_id INTEGER,
        from_nick TEXT,
        comment TEXT DEFAULT '',
        given_at REAL
    )
""")
db.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS awards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        given_by INTEGER,
        given_at REAL
    )
""")
db.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS bans (
        user_id INTEGER PRIMARY KEY,
        reason TEXT,
        banned_at REAL
    )
""")
db.commit()

for col_sql in [
    "ALTER TABLE users ADD COLUMN rating INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN custom_avatar_file_id TEXT DEFAULT NULL",
    "ALTER TABLE users ADD COLUMN custom_avatar_allowed INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN neitcoins INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN vip_level INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN last_farm REAL DEFAULT 0",
]:
    try:
        cursor.execute(col_sql)
        db.commit()
    except sqlite3.OperationalError:
        pass

# ============ АВАТАРКИ ============
AVATARS = {
    "cat": {"file_id": "AgACAgIAAxkBAAONarK0RZLxCqeQEg_QwNMWzgcDKWsAAoAlaxsW6phJaQ-cCAteJTsBAAMCAAN4AAM9BA", "name": "🐱 Котик", "price": 100},
    "girl": {"file_id": "AgACAgIAAxkBAAOFarKzpvou9200o8uGbnQBl_hovZMAAnolaxsW6phJ_OGQMrOmaHgBAAMCAAN4AAM9BA", "name": "👧 Девушка", "price": 200},
    "phenibut": {"file_id": "AgACAgIAAxkBAAOJarKz_Ga1owtsuKZmX7hu3dTkniAAAn0laxsW6phJ11-qdlNFbSABAAMCAAN4AAM9BA", "name": "💊 Девушка на фене", "price": 500},
    "smoking_cat": {"file_id": "AgACAgIAAxkBAAOParK0W9mfZVH507MSA9VClDbUv5AAAoElaxsW6phJAbE5A40G8nABAAMCAAN4AAM9BA", "name": "🚬 Кот с сигаретой", "price": 300},
    "pushin": {"file_id": "AgACAgIAAxkBAAOLarK0IwlwS3sJrNNAr9Okr6mbgaEAAn4laxsW6phJhej7isAJzFMBAAMCAAN4AAM9BA", "name": "🔥 Пьюшин", "price": 400},
    "sleep": {"file_id": "AgACAgIAAxkBAAOHarKz2qTHaYNPryNd2v4kqj9CboYAAnslaxsW6phJRrYm7Lr3I6oBAAMCAAN4AAM9BA", "name": "😴 Сон", "price": 150},
}

SHOP = {
    "vip": {"name": f'<tg-emoji emoji-id="{PE_VIP}">💎</tg-emoji> VIP статус', "price": 500, "desc": "Красивый значок в профиле"},
    "своя_аватарка": {"name": f'<tg-emoji emoji-id="{PE_AVATAR}">🖼</tg-emoji> Своя аватарка', "price": 500, "desc": "Загрузить свою картинку"},
}

def top_inline(active="rating"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Рейтинг", callback_data="top_rating"),
         InlineKeyboardButton(text="💰 Деньги", callback_data="top_money")],
    ])

def pet_inline(pet_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍖 Покормить", callback_data=f"pet_feed_{pet_id}"),
         InlineKeyboardButton(text="🤚 Погладить", callback_data=f"pet_pet_{pet_id}")],
        [InlineKeyboardButton(text="🎾 Поиграть", callback_data=f"pet_play_{pet_id}")],
    ])

def pet_choose_inline(user_id):
    buttons = []
    row = []
    for key, info in PET_PETS.items():
        row.append(InlineKeyboardButton(text=f"{info['emoji']} {info['name']}", callback_data=f"pet_pick_{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def pets_list_inline(user_id):
    pets = get_user_pets(user_id)
    buttons = []
    for p in pets:
        info = PET_PETS.get(p["pet_type"], {"emoji": "🐾", "name": "Питомец"})
        buttons.append([InlineKeyboardButton(text=f"{info['emoji']} {p['pet_name']}", callback_data=f"mypet_{p['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def biz_list_inline(user_id):
    businesses = get_user_businesses(user_id)
    buttons = []
    for b in businesses:
        buttons.append([InlineKeyboardButton(text=f"💼 Бизнес #{b['id']} (Lvl {b['level']})", callback_data=f"mybiz_{b['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ============ ФУНКЦИИ БД ============
def is_banned(user_id):
    with db_lock:
        cursor.execute("SELECT 1 FROM bans WHERE user_id = ?", (user_id,))
        return cursor.fetchone() is not None

def ban_user(user_id, reason=""):
    with db_lock:
        cursor.execute("INSERT OR REPLACE INTO bans (user_id, reason, banned_at) VALUES (?, ?, ?)", (user_id, reason, time.time()))
        db.commit()

def unban_user(user_id):
    with db_lock:
        cursor.execute("DELETE FROM bans WHERE user_id = ?", (user_id,))
        db.commit()

def get_user(user_id, default_name="Игрок"):
    with db_lock:
        cursor.execute("""SELECT balance, nickname, avatar, last_daily, last_work, daily_streak,
                          wins, losses, total_earned, vip, rating, custom_avatar_file_id,
                          custom_avatar_allowed, neitcoins, vip_level, last_farm FROM users WHERE user_id = ?""", (user_id,))
        row = cursor.fetchone()
        if row is None:
            cursor.execute("INSERT INTO users (user_id, balance, nickname) VALUES (?, ?, ?)", (user_id, 100, default_name))
            db.commit()
            return {"balance":100,"nickname":default_name,"avatar":"default","last_daily":0,
                    "last_work":0,"daily_streak":0,"wins":0,"losses":0,"total_earned":0,"vip":0,
                    "rating":0,"custom_avatar_file_id":None,"custom_avatar_allowed":0,"neitcoins":0,"vip_level":0,"last_farm":0}
        return {"balance":row[0],"nickname":row[1],"avatar":row[2],"last_daily":row[3],
                "last_work":row[4],"daily_streak":row[5],"wins":row[6],"losses":row[7],
                "total_earned":row[8],"vip":row[9],"rating":row[10],
                "custom_avatar_file_id":row[11],"custom_avatar_allowed":row[12],
                "neitcoins":row[13],"vip_level":row[14],"last_farm":row[15]}

def upd(user_id, field, value):
    with db_lock:
        cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        db.commit()
    sync_to_supabase(user_id)

def inc(user_id, field, amount):
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return
    with db_lock:
        cursor.execute(f"UPDATE users SET {field} = {field} + ? WHERE user_id = ?", (amount, user_id))
        db.commit()
    sync_to_supabase(user_id)

def find_user_by_nick(nick):
    with db_lock:
        cursor.execute("SELECT user_id FROM users WHERE nickname = ?", (nick,))
        row = cursor.fetchone()
        return row[0] if row else None

def add_award(user_id, text, given_by):
    with db_lock:
        cursor.execute("INSERT INTO awards (user_id, text, given_by, given_at) VALUES (?, ?, ?, ?)", (user_id, text, given_by, time.time()))
        db.commit()

def get_awards(user_id):
    with db_lock:
        cursor.execute("SELECT id, text FROM awards WHERE user_id = ? ORDER BY id", (user_id,))
        return cursor.fetchall()

def remove_last_award(user_id):
    with db_lock:
        cursor.execute("SELECT id FROM awards WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        cursor.execute("DELETE FROM awards WHERE id = ?", (row[0],))
        db.commit()
        return row[0]

# ============ ФУНКЦИИ ПОДАРКОВ ============
def add_gift(user_id, gift_key, from_user_id, from_nick, comment=""):
    with db_lock:
        cursor.execute("INSERT INTO gifts (user_id, gift_key, from_user_id, from_nick, comment, given_at) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, gift_key, from_user_id, from_nick, comment, time.time()))
        db.commit()

def get_user_gifts(user_id):
    with db_lock:
        cursor.execute("SELECT gift_key, from_nick, comment, given_at FROM gifts WHERE user_id = ? ORDER BY id", (user_id,))
        return cursor.fetchall()

def get_user_gifts_detailed(user_id, limit=5):
    with db_lock:
        cursor.execute("SELECT gift_key, from_nick, comment FROM gifts WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
        return cursor.fetchall()

def get_user_notes(user_id):
    with db_lock:
        cursor.execute("SELECT id, gift_key, from_nick, comment FROM gifts WHERE user_id = ? AND comment != '' ORDER BY id DESC", (user_id,))
        return cursor.fetchall()

def delete_note(gift_id, user_id):
    with db_lock:
        cursor.execute("UPDATE gifts SET comment = '' WHERE id = ? AND user_id = ?", (gift_id, user_id))
        db.commit()

def count_gift(user_id, gift_key):
    with db_lock:
        cursor.execute("SELECT COUNT(*) FROM gifts WHERE user_id = ? AND gift_key = ?", (user_id, gift_key))
        return cursor.fetchone()[0]

def remove_one_gift(user_id, gift_key):
    with db_lock:
        cursor.execute("SELECT id FROM gifts WHERE user_id = ? AND gift_key = ? ORDER BY id DESC LIMIT 1", (user_id, gift_key))
        row = cursor.fetchone()
        if row is None:
            return False
        cursor.execute("DELETE FROM gifts WHERE id = ?", (row[0],))
        db.commit()
        return True

def get_gift_first_three(user_id):
    with db_lock:
        cursor.execute("SELECT gift_key FROM gifts WHERE user_id = ? ORDER BY id LIMIT 3", (user_id,))
        rows = cursor.fetchall()
        return [GIFTS[k]["emoji"] for (k,) in rows if k in GIFTS]

# ============ ФУНКЦИИ БИЗНЕСА (V2) ============
def get_user_businesses(user_id):
    with db_lock:
        cursor.execute("""SELECT id, level, leaves, tax_debt, last_salary, last_tax, last_leaf FROM businesses_v2 WHERE user_id = ?""", (user_id,))
        rows = cursor.fetchall()
        return [{"id": row[0], "level": row[1], "leaves": row[2], "tax_debt": row[3],
                 "last_salary": row[4], "last_tax": row[5], "last_leaf": row[6]} for row in rows]

def get_business(biz_id):
    with db_lock:
        cursor.execute("""SELECT id, user_id, level, leaves, tax_debt, last_salary, last_tax, last_leaf FROM businesses_v2 WHERE id = ?""", (biz_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {"id": row[0], "user_id": row[1], "level": row[2], "leaves": row[3], "tax_debt": row[4],
                "last_salary": row[5], "last_tax": row[6], "last_leaf": row[7]}

def create_business(user_id):
    now = time.time()
    with db_lock:
        cursor.execute("""INSERT INTO businesses_v2 (user_id, level, leaves, tax_debt, last_salary, last_tax, last_leaf)
                          VALUES (?, 0, 0, 0, ?, ?, ?)""", (user_id, now, now, now))
        db.commit()
    sync_to_supabase(user_id)

def upd_business(biz_id, field, value):
    with db_lock:
        cursor.execute(f"UPDATE businesses_v2 SET {field} = ? WHERE id = ?", (value, biz_id))
        db.commit()

def inc_business(biz_id, field, amount):
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return
    with db_lock:
        cursor.execute(f"UPDATE businesses_v2 SET {field} = {field} + ? WHERE id = ?", (amount, biz_id))
        db.commit()
    with db_lock:
        cursor.execute("SELECT user_id FROM businesses_v2 WHERE id = ?", (biz_id,))
        row = cursor.fetchone()
        if row: sync_to_supabase(row[0])

def delete_business(biz_id):
    with db_lock:
        cursor.execute("SELECT user_id FROM businesses_v2 WHERE id = ?", (biz_id,))
        row = cursor.fetchone()
        uid = row[0] if row else None
        cursor.execute("DELETE FROM businesses_v2 WHERE id = ?", (biz_id,))
        db.commit()
    if uid: sync_to_supabase(uid)

def check_and_apply_salary(biz):
    now = time.time()
    result = {"salary": 0, "tax_added": 0}
    
    if now - biz["last_salary"] >= BUSINESS_SALARY_COOLDOWN:
        if biz["tax_debt"] <= 0:
            hours_passed = int((now - biz["last_salary"]) // BUSINESS_SALARY_COOLDOWN)
            if hours_passed > 24:
                hours_passed = 24
            base_salary = (BUSINESS_BASE_SALARY + BUSINESS_SALARY_PER_LEVEL * biz["level"]) * hours_passed
            
            u = get_user(biz["user_id"])
            bonus_mult = 1.0
            
            pets = get_user_pets(biz["user_id"])
            pet_bonus_count = 0
            for p in pets:
                if p["love"] >= 50 and pet_bonus_count < 2:
                    bonus_mult += 0.10
                    pet_bonus_count += 1
            
            if u["vip_level"] in VIP_LEVELS:
                bonus_mult += (VIP_LEVELS[u["vip_level"]]["bonus"] / 100.0)
                
            salary = int(base_salary * bonus_mult)
            inc(biz["user_id"], "balance", salary)
            inc(biz["user_id"], "total_earned", salary)
            upd_business(biz["id"], "last_salary", now)
            result["salary"] = salary
        else:
            result["salary"] = -1
            
    if now - biz["last_tax"] >= BUSINESS_TAX_COOLDOWN:
        taxes_passed = int((now - biz["last_tax"]) // BUSINESS_TAX_COOLDOWN)
        if taxes_passed > 12:
            taxes_passed = 12
        total_tax = BUSINESS_TAX * taxes_passed
        inc_business(biz["id"], "tax_debt", total_tax)
        upd_business(biz["id"], "last_tax", now)
        result["tax_added"] = total_tax
    return result

def get_business_salary(level):
    return BUSINESS_BASE_SALARY + BUSINESS_SALARY_PER_LEVEL * level

# ============ ФУНКЦИИ ПИТОМЦЕВ (V2) ============
def get_user_pets(user_id):
    with db_lock:
        cursor.execute("""SELECT id, pet_type, pet_name, love, trust, hunger, born_at,
                          last_feed, last_pet, last_play, last_hunger_update
                          FROM pets_v2 WHERE user_id = ?""", (user_id,))
        rows = cursor.fetchall()
        return [{"id": r[0], "pet_type": r[1], "pet_name": r[2], "love": r[3], "trust": r[4],
                 "hunger": r[5], "born_at": r[6], "last_feed": r[7],
                 "last_pet": r[8], "last_play": r[9], "last_hunger_update": r[10]} for r in rows]

def get_pet(pet_id):
    with db_lock:
        cursor.execute("""SELECT id, user_id, pet_type, pet_name, love, trust, hunger, born_at,
                          last_feed, last_pet, last_play, last_hunger_update
                          FROM pets_v2 WHERE id = ?""", (pet_id,))
        r = cursor.fetchone()
        if r is None: return None
        return {"id": r[0], "user_id": r[1], "pet_type": r[2], "pet_name": r[3], "love": r[4], "trust": r[5],
                "hunger": r[6], "born_at": r[7], "last_feed": r[8],
                "last_pet": r[9], "last_play": r[10], "last_hunger_update": r[11]}

def create_pet(user_id, pet_type, pet_name):
    now = time.time()
    with db_lock:
        cursor.execute("""INSERT INTO pets_v2 (user_id, pet_type, pet_name, love, trust, hunger,
                          born_at, last_feed, last_pet, last_play, last_hunger_update)
                          VALUES (?, ?, ?, 0, 0, 100, ?, 0, 0, 0, ?)""",
                       (user_id, pet_type, pet_name, now, now))
        db.commit()
    sync_to_supabase(user_id)

def upd_pet(pet_id, field, value):
    with db_lock:
        cursor.execute(f"UPDATE pets_v2 SET {field} = ? WHERE id = ?", (value, pet_id))
        db.commit()
    with db_lock:
        cursor.execute("SELECT user_id FROM pets_v2 WHERE id = ?", (pet_id,))
        row = cursor.fetchone()
        if row: sync_to_supabase(row[0])

def inc_pet(pet_id, field, amount):
    with db_lock:
        cursor.execute(f"UPDATE pets_v2 SET {field} = {field} + ? WHERE id = ?", (amount, pet_id))
        db.commit()
    with db_lock:
        cursor.execute("SELECT user_id FROM pets_v2 WHERE id = ?", (pet_id,))
        row = cursor.fetchone()
        if row: sync_to_supabase(row[0])

def delete_pet(pet_id):
    with db_lock:
        cursor.execute("SELECT user_id FROM pets_v2 WHERE id = ?", (pet_id,))
        row = cursor.fetchone()
        uid = row[0] if row else None
        cursor.execute("DELETE FROM pets_v2 WHERE id = ?", (pet_id,))
        db.commit()
    if uid: sync_to_supabase(uid)

def update_pet_hunger(pet):
    now = time.time()
    hours_passed = int((now - pet["last_hunger_update"]) // 3600)
    if hours_passed > 0:
        if hours_passed > 24:
            hours_passed = 24
        new_hunger = max(0, pet["hunger"] - hours_passed)
        upd_pet(pet["id"], "hunger", new_hunger)
        upd_pet(pet["id"], "last_hunger_update", now)

def pet_love_rank(love):
    if love >= 81: return "❤️‍🔥 Родная душа"
    elif love >= 61: return "💕 Любимый"
    elif love >= 41: return "😊 Хороший друг"
    elif love >= 21: return "🙂 Друг"
    else: return "🥶 Незнакомец"

def pet_age_str(born_at):
    days = int((time.time() - born_at) // 86400)
    if days == 0: return "меньше дня"
    elif days == 1: return "1 день"
    elif days < 5: return f"{days} дня"
    else: return f"{days} дней"

def build_pet_text(pet):
    info = PET_PETS.get(pet["pet_type"], {"emoji": "🐾", "name": "Питомец"})
    if pet["hunger"] >= 70: hunger_status = "😊 Сыт"
    elif pet["hunger"] >= 40: hunger_status = "😐 Проголодался"
    elif pet["hunger"] >= 10: hunger_status = "😟 Голодный"
    else: hunger_status = "😢 Очень голодный"
    love_rank = pet_love_rank(pet["love"])
    text = (
        f'<tg-emoji emoji-id="{PE_STAT}">🐾</tg-emoji> <b>ПИТОМЕЦ</b>\n'
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{info['emoji']} <b>{html.escape(pet['pet_name'])}</b> ({info['name']})\n"
        f"📅 Возраст: <b>{pet_age_str(pet['born_at'])}</b>\n\n"
        f"❤️ Любовь: <b>{pet['love']}</b>/100 — {love_rank}\n"
        f"🤝 Доверие: <b>{pet['trust']}</b>/100\n"
        f"🍖 Голод: <b>{pet['hunger']}</b>/100 — {hunger_status}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<b>ВЗАИМОДЕЙСТВИЯ</b> (раз в 30 мин):\n"
        f"🍖 покормить — +5❤️ +3🤝\n"
        f"🤚 погладить — +3❤️ +5🤝\n"
        f"🎾 поиграть — +7❤️ +7🤝"
    )
    if pet["love"] >= 50:
        text += f"\n<tg-emoji emoji-id=\"{PE_BALANCE}\">💰</tg-emoji> <b>Бонус: +10% к зарплате бизнеса!</b>"
    return text

# ============ РАНГИ ============
def get_rank(rating):
    ranks = [(100000, "🌟 Бог"), (20000, "👑 Легенда"), (5000, "💎 Элита"), (1000, "🥇 Мастер"), (100, "🥈 Опытный"), (0, "🥉 Новичок")]
    for threshold, name in ranks:
        if rating >= threshold:
            return name
    return "🥉 Новичок"

def get_next_rank(rating):
    for t in [100, 1000, 5000, 20000, 100000]:
        if rating < t:
            return t
    return None

# ============ ТОПЫ ============
def build_top_rating(user_id):
    with db_lock:
        cursor.execute("SELECT user_id, nickname, rating FROM users ORDER BY rating DESC LIMIT 10")
        rows = cursor.fetchall()
        medals = ["🥇", "🥈", "🥉"]
        text = f"<b>ТОП 10 ПО РЕЙТИНГУ</b>\n"
        text += "━━━━━━━━━━━━━━━━\n\n"
        for i, (uid, nick, rating) in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i+1}."
            rank = get_rank(rating)
            text += f"{medal} <b>{html.escape(nick)}</b> — {rank}\n"
            text += f"   <tg-emoji emoji-id=\"{PE_TOP_PLACE}\">⭐</tg-emoji> <b>{fmt(rating)}</b>\n"
        cursor.execute("SELECT COUNT(*) FROM users WHERE rating > (SELECT rating FROM users WHERE user_id = ?)", (user_id,))
        place = cursor.fetchone()[0] + 1
        cursor.execute("SELECT nickname, rating FROM users WHERE user_id = ?", (user_id,))
        my = cursor.fetchone()
        if my:
            text += "\n━━━━━━━━━━━━━━━━\n"
            text += f"➡️ <b>#{place} {html.escape(my[0])}</b> — <tg-emoji emoji-id=\"{PE_TOP_PLACE}\">⭐</tg-emoji>{fmt(my[1])}"
        return text

def build_top_money(user_id):
    with db_lock:
        cursor.execute("SELECT user_id, nickname, balance FROM users ORDER BY balance DESC LIMIT 10")
        rows = cursor.fetchall()
        medals = ["🥇", "🥈", "🥉"]
        text = f"<b>ТОП 10 ПО ДЕНЬГАМ</b>\n"
        text += "━━━━━━━━━━━━━━━━\n\n"
        for i, (uid, nick, bal) in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i+1}."
            text += f"{medal} <b>{html.escape(nick)}</b> — <tg-emoji emoji-id=\"{PE_BALANCE}\">💰</tg-emoji><b>{fmt(bal)}</b>\n"
        cursor.execute("SELECT COUNT(*) FROM users WHERE balance > (SELECT balance FROM users WHERE user_id = ?)", (user_id,))
        place = cursor.fetchone()[0] + 1
        cursor.execute("SELECT nickname, balance FROM users WHERE user_id = ?", (user_id,))
        my = cursor.fetchone()
        if my:
            text += "\n━━━━━━━━━━━━━━━━\n"
            text += f"➡️ <b>#{place} {html.escape(my[0])}</b> — <tg-emoji emoji-id=\"{PE_BALANCE}\">💰</tg-emoji>{fmt(my[1])}"
        return text

def count_users_above_rating(rating):
    with db_lock:
        cursor.execute("SELECT COUNT(*) FROM users WHERE rating > ?", (rating,))
        return cursor.fetchone()[0]

# ============ БОТ ============
bot = Bot(token=TOKEN)
dp = Dispatcher()

waiting_for_photo = set()

@dp.message(lambda m: is_banned(m.from_user.id))
async def banned_handler(message: types.Message):
    return

# ============ ВОЗРАСТ БОТА ============
@dp.message(lambda m: m.text and m.text.lower().strip() in ("возраст", "о боте", "инфо", "информация"))
async def age_cmd(message: types.Message):
    now = time.time()
    days = int((now - BOT_BIRTHDAY) // 86400)
    hours = int(((now - BOT_BIRTHDAY) % 86400) // 3600)

    if days % 10 == 1 and days % 100 != 11:
        day_word = "день"
    elif days % 10 in (2, 3, 4) and days % 100 not in (12, 13, 14):
        day_word = "дня"
    else:
        day_word = "дней"

    with db_lock:
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(balance) FROM users")
        total_money = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(wins + losses) FROM users")
        total_games = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM pets_v2")
        total_pets = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM businesses_v2")
        total_biz = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM gifts")
        total_gifts = cursor.fetchone()[0]

    text = (
        f'<tg-emoji emoji-id="{PE_STAT}">🎂</tg-emoji> <b>ВОЗРАСТ БОТА</b>\n'
        f"━━━━━━━━━━━━━━━━\n\n"
        f"📅 Создан: <b>22 сентября 2026</b>\n"
        f"⏰ Возраст: <b>{days} {day_word}</b> и {hours} ч.\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f'<tg-emoji emoji-id="{PE_STAT}">📊</tg-emoji> <b>СТАТИСТИКА</b>\n'
        f"━━━━━━━━━━━━━━━━\n"
        f"👥 Юзеров: <b>{total_users}</b>\n"
        f'<tg-emoji emoji-id="{PE_BALANCE}">💰</tg-emoji> Монет в обороте: <b>{fmt(total_money)}</b>\n'
        f"🎮 Игр сыграно: <b>{total_games}</b>\n"
        f"🐾 Питомцев: <b>{total_pets}</b>\n"
        f'<tg-emoji emoji-id="{PE_BIZ}">💼</tg-emoji> Бизнесов: <b>{total_biz}</b>\n'
        f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji> Подарков: <b>{total_gifts}</b>'
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("start"))
@dp.message(lambda m: m.text and m.text.lower().strip() in ("старт", "начать", "привет", "хай", "меню"))
async def start_cmd(message: types.Message):
    u = get_user(message.from_user.id, message.from_user.first_name or "Игрок")
    nick = u["nickname"]
    await message.answer(
        f"👋 Привет, <b>{html.escape(nick)}</b>!\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "📋 <b>КОМАНДЫ</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "👤 <code>я</code> — профиль\n"
        f'<tg-emoji emoji-id="{PE_BALANCE}">💰</tg-emoji> <code>баланс</code> — баланс\n'
        f'<tg-emoji emoji-id="{PE_TOP_PLACE}">⭐</tg-emoji> <code>рейтинг</code> — рейтинг\n'
        f'<tg-emoji emoji-id="{PE_AWARDS}">🏅</tg-emoji> <code>награды</code> — награды\n'
        f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji> <code>бонус</code> — ежедневная награда\n'
        "⚒ <code>работа</code> — поработать\n"
        f'<tg-emoji emoji-id="{PE_NEITCOINS}">💎</tg-emoji> <code>фарм</code> — фарм Нейткоинов (раз в час)\n'
        f'<tg-emoji emoji-id="{PE_VIP}">👑</tg-emoji> <code>вип</code> — магазин VIP-статусов\n'
        f'<tg-emoji emoji-id="{PE_BIZ}">💼</tg-emoji> <code>мой бизнес</code> — список бизнесов\n'
        "🍃 <code>искать листочки</code> — найти\n"
        "🐾 <code>питомцы</code> — приют\n"
        f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji> <code>подарки</code> — магазин\n'
        "💌 <code>записки</code> — твои записки\n"
        "✏️ <code>ник НовыйНик</code> — сменить ник\n"
        "🛒 <code>магазин</code> — магазин\n"
        "🖼 <code>аватарки</code> — аватарки\n"
        "💸 <code>перевод Ник Сумма</code>\n"
        "🎰 <code>казино Сумма</code>\n"
        "🎲 <code>рулетка Сумма чёт/нечет</code>\n"
        "🏆 <code>топ</code> — топ\n"
        "🎂 <code>возраст</code> — о боте\n"
        "🌐 <code>сайт</code> — профиль на сайте\n\n"
        "💡 Напиши <b>'Нейт'</b> — и я отзовусь!",
        parse_mode="HTML"
    )

@dp.message(lambda m: m.photo)
async def photo_handler(message: types.Message):
    uid = message.from_user.id
    if uid not in waiting_for_photo:
        return
    u = get_user(uid, message.from_user.first_name or "Игрок")
    if uid != ADMIN_ID and not u["custom_avatar_allowed"]:
        waiting_for_photo.discard(uid)
        await message.answer("❌ Нет права. Купи 'своя_аватарка'")
        return
    file_id = message.photo[-1].file_id
    upd(uid, "custom_avatar_file_id", file_id)
    upd(uid, "avatar", "custom")
    waiting_for_photo.discard(uid)
    await message.answer("✅ Аватарка профиля поставлена!")

# ============ ФАРМ И VIP ============
@dp.message(lambda m: m.text and m.text.lower().strip() in ("фарм", "фармить", "нейткоины"))
async def farm_cmd(message: types.Message):
    uid = message.from_user.id
    u = get_user(uid)
    now = time.time()
    
    if now - u["last_farm"] < FARM_COOLDOWN:
        rem = int(FARM_COOLDOWN - (now - u["last_farm"]))
        await message.answer(f"⏳ Фармить можно через <b>{rem//60} мин</b>", parse_mode="HTML")
        return
        
    found = random.randint(FARM_MIN, FARM_MAX)
    if u["vip_level"] == 5:
        found *= 2
        
    inc(uid, "neitcoins", found)
    upd(uid, "last_farm", now)
    
    u = get_user(uid)
    await message.answer(
        f'<tg-emoji emoji-id="{PE_NEITCOINS}">💎</tg-emoji> <b>Ты нафармил {found} Нейткоинов!</b>\n\n'
        f"Теперь у тебя: <b>{u['neitcoins']}</b> 💎\n\n"
        f'<tg-emoji emoji-id="{PE_VIP}">👑</tg-emoji> Купить VIP: <code>вип</code>',
        parse_mode="HTML"
    )

@dp.message(lambda m: m.text and m.text.lower().strip() in ("вип", "vip", "вип магазин"))
async def vip_menu_cmd(message: types.Message):
    uid = message.from_user.id
    u = get_user(uid)
    
    text = f'<tg-emoji emoji-id="{PE_VIP}">👑</tg-emoji> <b>VIP СТАТУСЫ</b>\n'
    text += f"━━━━━━━━━━━━━━━━\n"
    text += f'<tg-emoji emoji-id="{PE_NEITCOINS}">💎</tg-emoji> Твои Нейткоины: <b>{u["neitcoins"]}</b>\n\n'
    
    for lvl, data in VIP_LEVELS.items():
        status = "✅ Куплен" if u["vip_level"] >= lvl else f"{data['price']} 💎"
        text += f"{data['name']} — {status}\n"
        text += f"   <i>+{data['bonus']}% к зарплате бизнеса</i>\n\n"
        
    text += f"━━━━━━━━━━━━━━━━\n"
    text += f"Твой текущий бонус: <b>+{VIP_LEVELS[u['vip_level']]['bonus'] if u['vip_level'] in VIP_LEVELS else 0}%</b>\n\n"
    text += f"💡 Купить: <code>купить вип 1</code> (где 1-5 это уровень)"
    
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().startswith("купить вип "))
async def buy_vip_cmd(message: types.Message):
    try:
        lvl = int(message.text.split()[2])
    except (ValueError, IndexError):
        await message.answer("❌ Неверный уровень. Напиши <code>вип</code> для списка.")
        return
        
    if lvl not in VIP_LEVELS:
        await message.answer("❌ Такого VIP нет.")
        return
        
    uid = message.from_user.id
    u = get_user(uid)
    
    if u["vip_level"] >= lvl:
        await message.answer("❌ У тебя уже есть этот VIP или выше.")
        return
        
    data = VIP_LEVELS[lvl]
    price = data["price"]
    
    if u["neitcoins"] < price:
        await message.answer(f"❌ Не хватает Нейткоинов.\nНужно: <b>{price}</b> 💎\nУ тебя: <b>{u['neitcoins']}</b> 💎")
        return
        
    inc(uid, "neitcoins", -price)
    upd(uid, "vip_level", lvl)
    
    await message.answer(f"✅ <b>Ты купил {data['name']}!</b>\n\n"
                         f"Теперь твоя зарплата бизнеса увеличена на <b>+{data['bonus']}%</b>!\n"
                         f'<tg-emoji emoji-id="{PE_NEITCOINS}">💎</tg-emoji> Осталось Нейткоинов: <b>{get_user(uid)["neitcoins"]}</b>', parse_mode="HTML")

# ============ ПОДАРКИ ============
@dp.message(lambda m: m.text and m.text.lower().strip() in ("подарки", "магазин подарков"))
async def gifts_cmd(message: types.Message):
    uid = message.from_user.id
    get_user(uid, message.from_user.first_name or "Игрок")

    text = f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji> <b>МАГАЗИН ПОДАРКОВ</b>\n'
    text += "━━━━━━━━━━━━━━━━\n\n"
    for key, info in GIFTS.items():
        text += f"{info['emoji']} <b>{info['name']}</b> — {fmt(info['price'])}<tg-emoji emoji-id=\"{PE_BALANCE}\">💰</tg-emoji>\n"

    my_gifts = get_user_gifts(uid)
    if my_gifts:
        counts = {}
        for row in my_gifts:
            gift_key = row[0]
            counts[gift_key] = counts.get(gift_key, 0) + 1
        text += "\n━━━━━━━━━━━━━━━━\n"
        text += "📦 <b>ТВОИ ПОДАРКИ</b>\n"
        text += "━━━━━━━━━━━━━━━━\n"
        for key, count in counts.items():
            if key in GIFTS:
                info = GIFTS[key]
                text += f"{info['emoji']} {info['name']} × <b>{count}</b>\n"

    text += "\n━━━━━━━━━━━━━━━━\n"
    text += "🛍 Купить: <code>купить подарок роза</code>\n"
    text += "🎁 Подарить: <code>подарить @ник роза [Комментарий]</code>\n"
    text += "💸 Продать: <code>продать подарок роза</code> (за 50%)"

    await message.answer(text, parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().startswith("купить подарок"))
async def buy_gift_cmd(message: types.Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: <code>купить подарок роза</code>\nПосмотри <code>подарки</code>", parse_mode="HTML")
        return
    gift_key = parts[2].strip().lower()

    if gift_key not in GIFTS:
        await message.answer(f"❌ Нет такого подарка. Напиши <code>подарки</code>", parse_mode="HTML")
        return

    info = GIFTS[gift_key]
    u = get_user(message.from_user.id, message.from_user.first_name or "Игрок")

    if u["balance"] < info["price"]:
        await message.answer(f"❌ Не хватает монет.\nНужно: <b>{fmt(info['price'])}</b>💰\nУ тебя: <b>{fmt(u['balance'])}</b>💰", parse_mode="HTML")
        return

    inc(message.from_user.id, "balance", -info["price"])
    add_gift(message.from_user.id, gift_key, message.from_user.id, u["nickname"], "")

    new_bal = get_user(message.from_user.id)["balance"]
    await message.answer(
        f"✅ <b>Ты купил:</b> {info['emoji']} {info['name']}\n\n"
        f"💰 Снято: <b>{fmt(info['price'])}</b>\n"
        f"💰 Осталось: <b>{fmt(new_bal)}</b>",
        parse_mode="HTML"
    )

@dp.message(lambda m: m.text and m.text.lower().startswith("подарить"))
async def gift_someone_cmd(message: types.Message):
    raw = message.text[8:].strip()
    if not raw:
        await message.answer(
            "<b>Использование:</b>\n"
            "• <code>подарить @ник роза</code>\n"
            "• <code>подарить @ник роза С днём рождения!</code>\n"
            "• Ответь реплаем: <code>подарить роза Комментарий</code>",
            parse_mode="HTML"
        )
        return

    target = None
    gift_key = None
    comment = ""

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        parts = raw.split(maxsplit=1)
        gift_key = parts[0].strip().lower()
        if len(parts) >= 2:
            comment = parts[1].strip()
    else:
        parts = raw.split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Использование: <code>подарить @ник роза [Комментарий]</code>", parse_mode="HTML")
            return
        nick = parts[0].strip().lstrip("@")
        gift_key = parts[1].strip().lower()
        if len(parts) >= 3:
            comment = parts[2].strip()
        target_id = find_user_by_nick(nick)
        if target_id is None:
            await message.answer(f"❌ '{html.escape(nick)}' не найден. Пусть он напишет боту.", parse_mode="HTML")
            return
        target = type("obj", (object,), {"id": target_id, "first_name": nick})()

    if gift_key not in GIFTS:
        await message.answer(f"❌ '{html.escape(gift_key)}' — нет такого подарка. Напиши <code>подарки</code>", parse_mode="HTML")
        return

    if target.id == message.from_user.id:
        await message.answer("❌ Себе дарить нельзя (купи себе через <code>купить подарок</code>)", parse_mode="HTML")
        return

    if target.id == bot.id:
        await message.answer("❌ Боту дарить нельзя 😄")
        return

    if len(comment) > 200:
        comment = comment[:200]

    info = GIFTS[gift_key]
    sender = get_user(message.from_user.id, message.from_user.first_name or "Игрок")

    if sender["balance"] < info["price"]:
        await message.answer(f"❌ Не хватает монет.\nНужно: <b>{fmt(info['price'])}</b>💰\nУ тебя: <b>{fmt(sender['balance'])}</b>💰", parse_mode="HTML")
        return

    inc(message.from_user.id, "balance", -info["price"])
    get_user(target.id, getattr(target, "first_name", "Игрок"))
    add_gift(target.id, gift_key, message.from_user.id, sender["nickname"], comment)

    new_bal = get_user(message.from_user.id)["balance"]
    answer = f"✅ Ты подарил {info['emoji']} <b>{info['name']}</b> → <b>{html.escape(target.first_name)}</b>\n"
    if comment:
        answer += f"💌 Комментарий: <i>«{html.escape(comment)}»</i>\n"
    answer += f"\n💰 Снято: <b>{fmt(info['price'])}</b>\n"
    answer += f"💰 Осталось: <b>{fmt(new_bal)}</b>"
    await message.answer(answer, parse_mode="HTML")

    try:
        notif = (
            f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji> <b>ТЕБЕ ПОДАРОК!</b>\n\n'
            f"{info['emoji']} {info['name']}\n"
            f"📝 От: <b>{html.escape(sender['nickname'])}</b>\n"
        )
        if comment:
            notif += f"💌 <i>«{html.escape(comment)}»</i>\n"
        notif += f"\n💡 Напиши <code>я</code> чтоб посмотреть в профиле"
        await bot.send_message(target.id, notif, parse_mode="HTML")
    except Exception:
        pass

@dp.message(lambda m: m.text and m.text.lower().startswith("продать подарок"))
async def sell_gift_cmd(message: types.Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: <code>продать подарок роза</code>", parse_mode="HTML")
        return
    gift_key = parts[2].strip().lower()

    if gift_key not in GIFTS:
        await message.answer(f"❌ Нет такого подарка. Напиши <code>подарки</code>", parse_mode="HTML")
        return

    info = GIFTS[gift_key]
    uid = message.from_user.id
    count = count_gift(uid, gift_key)

    if count <= 0:
        await message.answer(f"❌ У тебя нет подарка {info['emoji']} {info['name']}", parse_mode="HTML")
        return

    remove_one_gift(uid, gift_key)
    sell_price = info["price"] // 2
    inc(uid, "balance", sell_price)

    new_bal = get_user(uid)["balance"]
    await message.answer(
        f"💸 Ты продал {info['emoji']} <b>{info['name']}</b>\n\n"
        f"💰 Получено: <b>{fmt(sell_price)}</b> (50%)\n"
        f"💰 Баланс: <b>{fmt(new_bal)}</b>",
        parse_mode="HTML"
    )

# ============ ЗАПИСКИ К ПОДАРКАМ ============
@dp.message(lambda m: m.text and m.text.lower().strip() in ("записки", "мои записки"))
async def my_notes_cmd(message: types.Message):
    uid = message.from_user.id
    get_user(uid, message.from_user.first_name or "Игрок")

    rows = get_user_notes(uid)

    if not rows:
        await message.answer("💌 У тебя нет записок к подаркам 😢\n\nКогда тебе подарят с запиской — они появятся тут.")
        return

    text = f"💌 <b>ТВОИ ЗАПИСКИ</b> ({len(rows)})\n"
    text += "━━━━━━━━━━━━━━━━\n\n"
    for i, (gift_id, gift_key, from_nick, comment) in enumerate(rows, 1):
        if gift_key in GIFTS:
            emoji = GIFTS[gift_key]["emoji"]
        else:
            emoji = f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji>'
        text += f"<b>{i}.</b> {emoji} от <b>{html.escape(from_nick)}</b>:\n"
        text += f"   <i>«{html.escape(comment)}»</i>\n\n"

    text += "━━━━━━━━━━━━━━━━\n"
    text += f"Удалить: <code>удалить записку НОМЕР</code>\nНапример: <code>удалить записку 1</code>"
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().startswith("удалить записку "))
async def delete_note_cmd(message: types.Message):
    uid = message.from_user.id
    get_user(uid, message.from_user.first_name or "Игрок")

    arg = message.text[16:].strip()

    try:
        num = int(arg)
    except ValueError:
        await message.answer("❌ Номер должен быть числом.\nНапиши <code>записки</code> чтоб увидеть список.", parse_mode="HTML")
        return

    if num <= 0:
        await message.answer("❌ Номер должен быть > 0")
        return

    rows = get_user_notes(uid)

    if not rows:
        await message.answer("💌 У тебя нет записок")
        return

    if num > len(rows):
        await message.answer(f"❌ У тебя только <b>{len(rows)}</b> записок. Напиши <code>записки</code> чтоб увидеть список.", parse_mode="HTML")
        return

    gift_id, gift_key, from_nick, comment = rows[num - 1]
    delete_note(gift_id, uid)

    emoji = GIFTS.get(gift_key, {"emoji": f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji>'})["emoji"]

    await message.answer(
        f"✅ <b>Записка удалена!</b>\n\n"
        f"{emoji} от <b>{html.escape(from_nick)}</b>:\n"
        f"❌ <i>«{html.escape(comment)}»</i>\n\n"
        f"💡 Сам подарок остался в профиле",
        parse_mode="HTML"
    )

# ============ ПРОФИЛЬ ============
@dp.message(lambda m: m.text and m.text.lower().strip() in ("я", "профиль", "акк", "аккаунт"))
async def profile_cmd(message: types.Message):
    uid = message.from_user.id
    u = get_user(uid, message.from_user.first_name or "Игрок")
    vip_icon = " 💎" if u["vip"] else ""

    gift_emojis = get_gift_first_three(uid)
    gifts_str = "".join(gift_emojis)

    if u["avatar"] == "custom" and u["custom_avatar_file_id"]:
        avatar_file_id = u["custom_avatar_file_id"]
        avatar_name = "📸 Своя"
    elif u["avatar"] in AVATARS:
        avatar_file_id = AVATARS[u["avatar"]]["file_id"]
        avatar_name = AVATARS[u["avatar"]]["name"]
    else:
        avatar_file_id = None
        avatar_name = "🐱 Стандарт"

    rank = get_rank(u["rating"])
    next_threshold = get_next_rank(u["rating"])
    progress = f"📈 До след. ранга: <b>{fmt(next_threshold - u['rating'])}</b>" if next_threshold else f'<tg-emoji emoji-id="{PE_MAX}">🌟</tg-emoji> <b>Максимум!</b>'
    place = count_users_above_rating(u["rating"]) + 1

    awards = get_awards(uid)
    if awards:
        awards_text = f'<tg-emoji emoji-id="{PE_AWARDS}">🏅</tg-emoji> <b>НАГРАДЫ</b>\n'
        for _, t in awards:
            awards_text += f"🎖 {html.escape(t)}\n"
    else:
        awards_text = f'<tg-emoji emoji-id="{PE_AWARDS}">🏅</tg-emoji> Наград пока нет'

    businesses = get_user_businesses(uid)
    biz_text = ""
    if businesses:
        biz_text += f"\n<tg-emoji emoji-id=\"{PE_BIZ}\">💼</tg-emoji> Бизнесы ({len(businesses)}):"
        for b in businesses:
            biz_text += f"\n   #{b['id']} - {b['level']} lvl | 🍃 {fmt(b['leaves'])}"
    else:
        biz_text = f"\n<tg-emoji emoji-id=\"{PE_BIZ}\">💼</tg-emoji> Бизнесов нет"

    pets = get_user_pets(uid)
    pet_text = ""
    if pets:
        pet_text += f"\n🐾 Питомцы ({len(pets)}):"
        for p in pets:
            info = PET_PETS.get(p["pet_type"], {"emoji": "🐾"})
            pet_text += f"\n   {info['emoji']} {html.escape(p['pet_name'])} (❤️{p['love']})"
    else:
        pet_text = "\n🐾 Питомцев нет"
        
    vip_name = VIP_LEVELS[u["vip_level"]]["name"] if u["vip_level"] in VIP_LEVELS else "Нет"
    vip_text = f"\n<tg-emoji emoji-id=\"{PE_VIP}\">👑</tg-emoji> VIP: <b>{vip_name}</b>"

    my_gifts = get_user_gifts(uid)
    if my_gifts:
        counts = {}
        for row in my_gifts:
            gift_key = row[0]
            counts[gift_key] = counts.get(gift_key, 0) + 1
        gifts_list_text = f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji> <b>ПОДАРКИ</b>\n'
        for key, cnt in counts.items():
            if key in GIFTS:
                info = GIFTS[key]
                gifts_list_text += f"{info['emoji']} {info['name']} × <b>{cnt}</b>\n"

        recent = get_user_gifts_detailed(uid, 5)
        recent_with_comment = [r for r in recent if r[2]]
        if recent_with_comment:
            gifts_list_text += "\n💌 <b>ПОСЛЕДНИЕ ЗАПИСКИ</b>\n"
            for (gift_key, from_nick, comment) in recent_with_comment[:3]:
                if gift_key in GIFTS:
                    emoji = GIFTS[gift_key]["emoji"]
                    short_comment = comment[:50] + "..." if len(comment) > 50 else comment
                    gifts_list_text += f"{emoji} от <b>{html.escape(from_nick)}</b>:\n   <i>«{html.escape(short_comment)}»</i>\n"
    else:
        gifts_list_text = f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji> Подарков нет'

    nick_line = f'<tg-emoji emoji-id="{PE_NICK}">🏷</tg-emoji> Ник: <b>{html.escape(u["nickname"])}</b>{vip_icon}'
    if gifts_str:
        nick_line += f" {gifts_str}"

    text = (
        f'<tg-emoji emoji-id="{PE_PROFILE}">👤</tg-emoji> <b>ПРОФИЛЬ ИГРОКА</b>\n'
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{nick_line}\n"
        f'<tg-emoji emoji-id="{PE_AVATAR}">🖼</tg-emoji> Аватар: {avatar_name}\n\n'
        f'<tg-emoji emoji-id="{PE_RANK}">🎖</tg-emoji> Ранг: <b>{rank}</b>\n'
        f'<tg-emoji emoji-id="{PE_TOP_PLACE}">⭐</tg-emoji> Рейтинг: <b>{fmt(u["rating"])}</b>\n'
        f"🏆 Место в топе: <b>#{place}</b>\n"
        f"{progress}\n\n"
        f'<tg-emoji emoji-id="{PE_BALANCE}">💰</tg-emoji> Баланс: <b>{fmt(u["balance"])}</b> монет\n'
        f'<tg-emoji emoji-id="{PE_NEITCOINS}">💎</tg-emoji> Нейткоины: <b>{u["neitcoins"]}</b>{vip_text}\n'
        f'<tg-emoji emoji-id="{PE_STREAK}">🔥</tg-emoji> Стрик: <b>{u["daily_streak"]}</b> дн.{biz_text}{pet_text}\n\n'
        f"━━━━━━━━━━━━━━━━\n"
        f'<tg-emoji emoji-id="{PE_STAT}">📊</tg-emoji> <b>СТАТИСТИКА</b>\n'
        f"━━━━━━━━━━━━━━━━\n"
        f'<tg-emoji emoji-id="{PE_WINS}">🎰</tg-emoji> Побед: <b>{u["wins"]}</b> | Поражений: <b>{u["losses"]}</b>\n'
        f'<tg-emoji emoji-id="{PE_EARNED}">📈</tg-emoji> Всего заработано: <b>{fmt(u["total_earned"])}</b>\n\n'
        f"━━━━━━━━━━━━━━━━\n"
        f"{gifts_list_text}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{awards_text}\n\n"
        f"🆔 <code>{uid}</code>"
    )

    if avatar_file_id:
        try:
            if len(text) <= 1024:
                await message.answer_photo(photo=avatar_file_id, caption=text, parse_mode="HTML")
                return
            else:
                await message.answer_photo(photo=avatar_file_id, caption="👤 Профиль (текст ниже 👇)")
                await message.answer(text, parse_mode="HTML")
                return
        except Exception:
            pass
    await message.answer(text, parse_mode="HTML")

# ОСТАЛЬНЫЕ КОМАНДЫ ОСТАЛИСЬ ПРЕЖНИМИ (ПИТОМЦЫ, БИЗНЕС, КАЗИНО, АДМИНКА, САЙТ)
# Вставь их сюда из своего предыдущего кода...

# --- КОСТЫЛЬ ДЛЯ RENDER (чтобы не выдавал ошибку портов) ---
import http.server
import socketserver

def run_dummy_server():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# -----------------------------------------------------------

@dp.message()
async def echo(message: types.Message):
    if not message.text: return
    text_lower = message.text.lower().strip()
    if text_lower.startswith("нейт"):
        u = get_user(message.from_user.id, message.from_user.first_name or "Игрок")
        nick = u["nickname"]
        answers = [
            f"Привет, <b>{html.escape(nick)}</b>! Я тут! 🤖",
            f"Ась, <b>{html.escape(nick)}</b>? Что случилось? 👀",
            f"Я здесь, <b>{html.escape(nick)}</b>! Чем помочь? ✨",
            f"Чего звал, <b>{html.escape(nick)}</b>? 😎",
            f"Тут я, тут! Не кричи 😄",
        ]
        await message.answer(random.choice(answers), parse_mode="HTML")
        return
    if message.chat.type in ("group", "supergroup"): return
    await message.answer("🤔 Напиши <code>меню</code>", parse_mode="HTML")

async def main():
    print("Бот запущен! Премиум-эмодзи активны.")
    await dp.start_polling(bot)

asyncio.run(main()) 
