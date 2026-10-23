import asyncio
import sqlite3
import time
import random
import threading
import html
import urllib.parse
import os
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

TOKEN = "8957645798:AAGsdPMabVxXFT02d_9UuSS4j5XVDOV8xNc"
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
    if businesses:
        biz_text = f"\n<tg-emoji emoji-id=\"{PE_BIZ}\">💼</tg-emoji> Бизнесы ({len(businesses)}):"
        for b in businesses:
            biz_text += f"\n   #{b['id']} - {b['level']} lvl | 🍃 {fmt(b['leaves'])}"
    else:
        biz_text = f"\n<tg-emoji emoji-id=\"{PE_BIZ}\">💼</tg-emoji> Бизнесов нет"

    pets = get_user_pets(uid)
    if pets:
        pet_text = f"\n🐾 Питомцы ({len(pets)}):"
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

# ============ ПРИЮТ ПИТОМЦЕВ ============
@dp.message(lambda m: m.text and m.text.lower().strip() in ("питомцы", "приют"))
async def pets_shelter_cmd(message: types.Message):
    uid = message.from_user.id
    u = get_user(uid, message.from_user.first_name or "Игрок")
    pets = get_user_pets(uid)
    
    max_pets = MAX_PETS_LIMITS.get(u["vip_level"], 1)
    
    if len(pets) >= max_pets:
        if u["vip_level"] >= 4:
             await message.answer(
                f"🏠 <b>ПРИЮТ ПИТОМЦЕВ</b>\n\n"
                f"У тебя уже максимум питомцев ({len(pets)}/{max_pets}).\n"
                f"Но у тебя есть VIP Платина/Бриллиант! Ты можешь сдать питомца в приют, чтобы освободить место.\n\n"
                f"💡 Напиши <code>питомцы</code> и выбери питомца, чтобы сдать его.",
                reply_markup=pets_list_inline(uid),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"🏠 <b>ПРИЮТ ПИТОМЦЕВ</b>\n\n"
                f"У тебя уже максимум питомцев ({len(pets)}/{max_pets}).\n"
                f"Чтобы завести больше, купи VIP Серебро (2 питомца) или Бриллиант (6 питомцев).",
                parse_mode="HTML"
            )
        return
        
    text = "🏠 <b>ПРИЮТ ПИТОМЦЕВ</b>\n"
    text += "━━━━━━━━━━━━━━━━\n\n"
    text += f"Твои питомцы: <b>{len(pets)}/{max_pets}</b>\n\n"
    text += "Выбери себе друга:\n\n"
    for key, info in PET_PETS.items():
        text += f"{info['emoji']} <b>{info['name']}</b> — {info['desc']}\n"
    text += "\n💡 Выбери кнопкой ниже — бесплатно!"
    await message.answer(text, reply_markup=pet_choose_inline(uid), parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().strip() == "питомец")
async def my_pets_cmd(message: types.Message):
    uid = message.from_user.id
    get_user(uid, message.from_user.first_name or "Игрок")
    pets = get_user_pets(uid)
    if not pets:
        await message.answer("❌ У тебя нет питомцев!\n\n🏠 Напиши <code>питомцы</code> чтоб зайти в приют", parse_mode="HTML")
        return
    await message.answer("🐾 <b>ТВОИ ПИТОМЦЫ</b>\nВыбери питомца:", reply_markup=pets_list_inline(uid), parse_mode="HTML")

@dp.callback_query(lambda c: c.data.startswith("pet_pick_"))
async def pet_pick_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    u = get_user(uid, callback.from_user.first_name or "Игрок")
    pet_type = callback.data[9:]
    
    max_pets = MAX_PETS_LIMITS.get(u["vip_level"], 1)
    pets = get_user_pets(uid)
    
    if len(pets) >= max_pets:
        try:
            await callback.answer(f"❌ У тебя максимум питомцев ({max_pets}). Купи VIP.", show_alert=True)
        except Exception:
            pass
        return
        
    if pet_type not in PET_PETS:
        try:
            await callback.answer("❌ Неизвестный питомец")
        except Exception:
            pass
        return
        
    info = PET_PETS[pet_type]
    create_pet(uid, pet_type, info["name"])
    try:
        await callback.answer(f"✅ {info['emoji']} {info['name']} теперь твой!")
    except Exception:
        pass
    try:
        await callback.message.edit_text(
            f"✅ Ты выбрал: {info['emoji']} <b>{info['name']}</b>\n\n"
            f"📛 Имя питомца: <b>{info['name']}</b>\n"
            f"💡 Чтобы дать своё имя — напиши <code>назвать питомца {info['name']} НовоеИмя</code>\n\n"
            f"Напиши <code>питомцы</code> чтобы посмотреть всех.",
            parse_mode="HTML"
        )
    except Exception:
        pass

@dp.callback_query(lambda c: c.data.startswith("mypet_"))
async def mypet_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pet_id = int(callback.data[6:])
    pet = get_pet(pet_id)
    if not pet or pet["user_id"] != uid:
        try:
            await callback.answer("❌ Ошибка")
        except Exception:
            pass
        return
    update_pet_hunger(pet)
    pet = get_pet(pet_id)
    text = build_pet_text(pet)
    u = get_user(uid)
    
    kb = pet_inline(pet_id)
    if u["vip_level"] >= 4:
        kb.inline_keyboard.append([InlineKeyboardButton(text="🚪 Сдать в приют", callback_data=f"pet_drop_{pet_id}")])
        
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass

@dp.callback_query(lambda c: c.data.startswith("pet_drop_"))
async def pet_drop_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pet_id = int(callback.data[9:])
    pet = get_pet(pet_id)
    u = get_user(uid)
    
    if not pet or pet["user_id"] != uid:
        try: await callback.answer("❌ Ошибка")
        except: pass
        return
        
    if u["vip_level"] < 4:
        try: await callback.answer("❌ Нужен VIP Платина+", show_alert=True)
        except: pass
        return
        
    delete_pet(pet_id)
    try: await callback.answer(f"✅ {pet['pet_name']} сдан в приют!")
    except: pass
    try:
        await callback.message.edit_text(f"✅ Питомец <b>{html.escape(pet['pet_name'])}</b> сдан в приют.\nТы можешь завести нового!", parse_mode="HTML")
    except Exception:
        pass

def check_pet_cooldown(pet, field, cooldown):
    now = time.time()
    last = pet[field]
    if now - last < cooldown:
        return int(cooldown - (now - last))
    return 0

@dp.callback_query(lambda c: c.data.startswith("pet_feed_"))
async def pet_feed_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pet_id = int(callback.data[9:])
    pet = get_pet(pet_id)
    if not pet or pet["user_id"] != uid:
        try: await callback.answer("❌ Ошибка")
        except: pass
        return
    rem = check_pet_cooldown(pet, "last_feed", PET_INTERACT_COOLDOWN)
    if rem > 0:
        try: await callback.answer(f"⏳ Через {rem//60} мин", show_alert=True)
        except: pass
        return
    now = time.time()
    upd_pet(pet_id, "last_feed", now)
    inc_pet(pet_id, "hunger", 40)
    inc_pet(pet_id, "love", 5)
    inc_pet(pet_id, "trust", 3)
    pet = get_pet(pet_id)
    if pet["hunger"] > 100: upd_pet(pet_id, "hunger", 100)
    if pet["love"] > 100: upd_pet(pet_id, "love", 100)
    if pet["trust"] > 100: upd_pet(pet_id, "trust", 100)
    
    info = PET_PETS.get(pet["pet_type"], {"emoji": "🐾"})
    try: await callback.answer(f"🍖 {info['emoji']} доволен!")
    except: pass
    pet = get_pet(pet_id)
    text = build_pet_text(pet)
    u = get_user(uid)
    kb = pet_inline(pet_id)
    if u["vip_level"] >= 4:
        kb.inline_keyboard.append([InlineKeyboardButton(text="🚪 Сдать в приют", callback_data=f"pet_drop_{pet_id}")])
    try: await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except: pass

@dp.callback_query(lambda c: c.data.startswith("pet_pet_"))
async def pet_pet_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pet_id = int(callback.data[8:])
    pet = get_pet(pet_id)
    if not pet or pet["user_id"] != uid:
        try: await callback.answer("❌ Ошибка")
        except: pass
        return
    rem = check_pet_cooldown(pet, "last_pet", PET_INTERACT_COOLDOWN)
    if rem > 0:
        try: await callback.answer(f"⏳ Через {rem//60} мин", show_alert=True)
        except: pass
        return
    now = time.time()
    upd_pet(pet_id, "last_pet", now)
    inc_pet(pet_id, "love", 3)
    inc_pet(pet_id, "trust", 5)
    pet = get_pet(pet_id)
    if pet["love"] > 100: upd_pet(pet_id, "love", 100)
    if pet["trust"] > 100: upd_pet(pet_id, "trust", 100)
    
    info = PET_PETS.get(pet["pet_type"], {"emoji": "🐾"})
    try: await callback.answer(f"🤚 {info['emoji']} мурлычет!")
    except: pass
    pet = get_pet(pet_id)
    text = build_pet_text(pet)
    u = get_user(uid)
    kb = pet_inline(pet_id)
    if u["vip_level"] >= 4:
        kb.inline_keyboard.append([InlineKeyboardButton(text="🚪 Сдать в приют", callback_data=f"pet_drop_{pet_id}")])
    try: await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except: pass

@dp.callback_query(lambda c: c.data.startswith("pet_play_"))
async def pet_play_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pet_id = int(callback.data[9:])
    pet = get_pet(pet_id)
    if not pet or pet["user_id"] != uid:
        try: await callback.answer("❌ Ошибка")
        except: pass
        return
    rem = check_pet_cooldown(pet, "last_play", PET_INTERACT_COOLDOWN)
    if rem > 0:
        try: await callback.answer(f"⏳ Через {rem//60} мин", show_alert=True)
        except: pass
        return
    now = time.time()
    upd_pet(pet_id, "last_play", now)
    inc_pet(pet_id, "love", 7)
    inc_pet(pet_id, "trust", 7)
    pet = get_pet(pet_id)
    if pet["love"] > 100: upd_pet(pet_id, "love", 100)
    if pet["trust"] > 100: upd_pet(pet_id, "trust", 100)
    
    info = PET_PETS.get(pet["pet_type"], {"emoji": "🐾"})
    try: await callback.answer(f"🎾 {info['emoji']} весело играет!")
    except: pass
    pet = get_pet(pet_id)
    text = build_pet_text(pet)
    u = get_user(uid)
    kb = pet_inline(pet_id)
    if u["vip_level"] >= 4:
        kb.inline_keyboard.append([InlineKeyboardButton(text="🚪 Сдать в приют", callback_data=f"pet_drop_{pet_id}")])
    try: await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except: pass

@dp.message(lambda m: m.text and m.text.lower().startswith("назвать питомца "))
async def pet_rename_cmd(message: types.Message):
    uid = message.from_user.id
    parts = message.text[16:].strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: <code>назвать питомца СтароеИмя НовоеИмя</code>")
        return
    old_name, new_name = parts[0].strip(), parts[1].strip()
    
    if len(new_name) < 1 or len(new_name) > 20:
        await message.answer("❌ Имя 1-20 символов")
        return
        
    pets = get_user_pets(uid)
    for p in pets:
        if p["pet_name"].lower() == old_name.lower():
            upd_pet(p["id"], "pet_name", new_name)
            info = PET_PETS.get(p["pet_type"], {"emoji": "🐾"})
            await message.answer(f"{info['emoji']} Питомца зовут: <b>{html.escape(new_name)}</b>", parse_mode="HTML")
            return
    await message.answer(f"❌ Питомец с именем '{html.escape(old_name)}' не найден.")

# ============ БИЗНЕС ============
def build_business_text(biz):
    check_result = check_and_apply_salary(biz)
    biz = get_business(biz["id"])
    
    salary_per_hour = get_business_salary(biz["level"])
    
    u = get_user(biz["user_id"])
    if u["vip_level"] in VIP_LEVELS:
        salary_per_hour = int(salary_per_hour * (1 + VIP_LEVELS[u["vip_level"]]["bonus"] / 100.0))
        
    pets = get_user_pets(biz["user_id"])
    pet_bonus_count = 0
    for p in pets:
        if p["love"] >= 50 and pet_bonus_count < 2:
            salary_per_hour = int(salary_per_hour * 1.10)
            pet_bonus_count += 1

    leaves_to_next = LEAVES_PER_LEVEL - (biz["leaves"] % LEAVES_PER_LEVEL)
    if biz["level"] >= MAX_LEVEL:
        leaves_info = "🔝 <b>Максимум!</b>"
    else:
        leaves_info = f"📈 До след. уровня: <b>{leaves_to_next}</b> 🍃"
    now = time.time()
    sec_salary = max(0, int(BUSINESS_SALARY_COOLDOWN - (now - biz["last_salary"])))
    sec_tax = max(0, int(BUSINESS_TAX_COOLDOWN - (now - biz["last_tax"])))
    sec_leaf = max(0, int(LEAF_COOLDOWN - (now - biz["last_leaf"])))
    def time_str(sec):
        h = sec // 3600
        m = (sec % 3600) // 60
        if h > 0: return f"{h}ч {m}мин"
        return f"{m}мин"
        
    text = (
        f"💼 <b>БИЗНЕС #{biz['id']}</b>\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"📊 Уровень: <b>{biz['level']}</b> / {MAX_LEVEL}\n"
        f"💰 Зарплата: <b>{fmt(salary_per_hour)}</b>/час\n"
    )
    if biz["tax_debt"] > 0:
        text += f"🚨 НАЛОГИ (долг): <b>{fmt(biz['tax_debt'])}</b>💰\n"
        text += f"⚠️ <b>Зарплата заблокирована до оплаты!</b>\n\n"
    else:
        text += f"✅ Налоги: оплачены\n\n"
    text += f"🍃 Листочки: <b>{biz['leaves']}</b>\n{leaves_info}\n\n"
    text += f"⏰ Следующая зарплата: <b>{time_str(sec_salary)}</b>\n"
    text += f"💸 Следующий налог: <b>{time_str(sec_tax)}</b> (+{fmt(BUSINESS_TAX)})\n"
    text += f"🍃 Листочки через: <b>{time_str(sec_leaf)}</b>"
    extra = None
    if check_result:
        if check_result["salary"] > 0:
            extra = f"💰 Начислена зарплата: <b>+{fmt(check_result['salary'])}</b>"
        elif check_result["salary"] == -1:
            extra = "🚫 Зарплата не начислена — есть долг по налогам!"
        if check_result["tax_added"] > 0:
            if extra: extra += f"\n💸 Начислен налог: <b>+{fmt(check_result['tax_added'])}</b>"
            else: extra = f"💸 Начислен налог: <b>+{fmt(check_result['tax_added'])}</b>"
    return text, extra

def business_inline(biz_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍃 Искать листочки", callback_data=f"biz_leaf_{biz_id}"),
         InlineKeyboardButton(text="⬆️ Прокачать", callback_data=f"biz_up_{biz_id}")],
        [InlineKeyboardButton(text="💸 Оплатить налоги", callback_data=f"biz_tax_{biz_id}")],
    ])

@dp.message(lambda m: m.text and m.text.lower().strip() in ("мой бизнес", "бизнес"))
async def business_cmd(message: types.Message):
    uid = message.from_user.id
    businesses = get_user_businesses(uid)
    if not businesses:
        await message.answer(
            f"💼 <b>У тебя нет бизнесов!</b>\n\n"
            f"💰 Цена: <b>{fmt(BUSINESS_PRICE)}</b>\n"
            f"📊 Уровень: 0\n"
            f"💵 Зарплата: <b>{fmt(get_business_salary(0))}</b>/час\n\n"
            f"Купить: <code>купить бизнес</code>",
            parse_mode="HTML"
        )
        return
        
    text = "💼 <b>ТВОИ БИЗНЕСЫ</b>\nВыбери бизнес для управления:"
    await message.answer(text, reply_markup=biz_list_inline(uid), parse_mode="HTML")

@dp.callback_query(lambda c: c.data.startswith("mybiz_"))
async def mybiz_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    biz_id = int(callback.data[6:])
    biz = get_business(biz_id)
    if not biz or biz["user_id"] != uid:
        try: await callback.answer("❌ Ошибка")
        except: pass
        return
        
    text, extra = build_business_text(biz)
    if extra:
        try: await callback.message.answer(extra, parse_mode="HTML")
        except: pass
    try:
        await callback.message.edit_text(text, reply_markup=business_inline(biz_id), parse_mode="HTML")
    except: pass

@dp.message(lambda m: m.text and m.text.lower().strip() in ("купить бизнес", "купить_бизнес"))
async def buy_business_cmd(message: types.Message):
    uid = message.from_user.id
    u = get_user(uid, message.from_user.first_name or "Игрок")
    businesses = get_user_businesses(uid)
    
    max_biz = MAX_BIZ_LIMITS.get(u["vip_level"], 1)
    
    if len(businesses) >= max_biz:
        await message.answer(f"❌ У тебя уже максимум бизнесов ({max_biz}).\nКупи VIP Золото (2 бизнеса) или Бриллиант.", parse_mode="HTML")
        return
        
    if u["balance"] < BUSINESS_PRICE:
        await message.answer(f"❌ Не хватает монет.\nНужно: <b>{fmt(BUSINESS_PRICE)}</b>💰\nУ тебя: <b>{fmt(u['balance'])}</b>💰", parse_mode="HTML")
        return
    inc(uid, "balance", -BUSINESS_PRICE)
    create_business(uid)
    await message.answer(f"✅ <b>Бизнес куплен!</b>\n\n💼 Напиши <code>мой бизнес</code>", parse_mode="HTML")

@dp.callback_query(lambda c: c.data.startswith("biz_leaf_"))
async def biz_leaf_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    biz_id = int(callback.data[9:])
    biz = get_business(biz_id)
    if not biz or biz["user_id"] != uid:
        try: await callback.answer("❌ Ошибка")
        except: pass
        return
    now = time.time()
    if now - biz["last_leaf"] < LEAF_COOLDOWN:
        rem = int(LEAF_COOLDOWN - (now - biz["last_leaf"]))
        try: await callback.answer(f"⏳ Через {rem//60} мин", show_alert=True)
        except: pass
        return
    found = random.randint(LEAF_MIN, LEAF_MAX)
    inc_business(biz_id, "leaves", found)
    upd_business(biz_id, "last_leaf", now)
    try: await callback.answer(f"🍃 +{found} листочков!", show_alert=True)
    except: pass
    text, extra = build_business_text(get_business(biz_id))
    try: await callback.message.edit_text(text, reply_markup=business_inline(biz_id), parse_mode="HTML")
    except: pass

@dp.callback_query(lambda c: c.data.startswith("biz_up_"))
async def biz_up_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    biz_id = int(callback.data[7:])
    biz = get_business(biz_id)
    if not biz or biz["user_id"] != uid:
        try: await callback.answer("❌ Ошибка")
        except: pass
        return
        
    if biz["level"] >= MAX_LEVEL:
        try: await callback.answer("🔝 Максимум!", show_alert=True)
        except: pass
        return
    if biz["leaves"] < LEAVES_PER_LEVEL:
        try: await callback.answer(f"❌ Нужно {LEAVES_PER_LEVEL} 🍃", show_alert=True)
        except: pass
        return
        
    inc_business(biz_id, "leaves", -LEAVES_PER_LEVEL)
    inc_business(biz_id, "level", 1)
    try: await callback.answer(f"✅ Прокачано! Уровень {biz['level']+1}", show_alert=True)
    except: pass
    text, extra = build_business_text(get_business(biz_id))
    try: await callback.message.edit_text(text, reply_markup=business_inline(biz_id), parse_mode="HTML")
    except: pass

@dp.callback_query(lambda c: c.data.startswith("biz_tax_"))
async def biz_tax_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    biz_id = int(callback.data[8:])
    biz = get_business(biz_id)
    u = get_user(uid)
    if not biz or biz["user_id"] != uid:
        try: await callback.answer("❌ Ошибка")
        except: pass
        return
        
    if biz["tax_debt"] <= 0:
        try: await callback.answer("✅ Долгов нет", show_alert=True)
        except: pass
        return
    if u["balance"] < biz["tax_debt"]:
        try: await callback.answer(f"❌ Нужно {fmt(biz['tax_debt'])}💰", show_alert=True)
        except: pass
        return
        
    debt = biz["tax_debt"]
    inc(uid, "balance", -debt)
    upd_business(biz_id, "tax_debt", 0)
    upd_business(biz_id, "last_tax", time.time())
    try: await callback.answer(f"✅ Оплачено {fmt(debt)}💰", show_alert=True)
    except: pass
    text, extra = build_business_text(get_business(biz_id))
    try: await callback.message.edit_text(text, reply_markup=business_inline(biz_id), parse_mode="HTML")
    except: pass

# ============ ПРОЧИЕ КОМАНДЫ ============
@dp.message(lambda m: m.text and m.text.lower().strip() in ("аватарка", "своя аватарка", "моя аватарка"))
async def custom_avatar_cmd(message: types.Message):
    u = get_user(message.from_user.id)
    uid = message.from_user.id
    if uid == ADMIN_ID or u["custom_avatar_allowed"]:
        waiting_for_photo.add(uid)
        await message.answer("📸 Отправь мне фото — поставлю как аватарку.\n\n(Жду фото...)")
    else:
        await message.answer("❌ Нет права. Купи <code>своя_аватарка</code> (500💰)", parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().strip() in ("награды", "мои награды"))
async def my_awards_cmd(message: types.Message):
    awards = get_awards(message.from_user.id)
    if not awards:
        await message.answer(f'<tg-emoji emoji-id="{PE_AWARDS}">🏅</tg-emoji> У тебя пока нет наград 😢', parse_mode="HTML")
        return
    text = f'<tg-emoji emoji-id="{PE_AWARDS}">🏅</tg-emoji> <b>ТВОИ НАГРАДЫ</b> ({len(awards)})\n'
    text += "━━━━━━━━━━━━━━━━\n"
    for _, award in awards:
        text += f"🎖 {html.escape(award)}\n"
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().strip() in ("магазин", "шоп", "shop"))
async def shop_cmd(message: types.Message):
    text = "🛒 <b>МАГАЗИН</b>\n"
    text += "━━━━━━━━━━━━━━━━\n\n"
    for key, item in SHOP.items():
        text += f"<code>{key}</code> — <b>{item['name']}</b> — {fmt(item['price'])}💰\n"
        text += f"   <i>{item['desc']}</i>\n\n"
    text += "Купить: <code>купить ключ</code>"
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().strip() in ("аватарки", "авы", "готовые аватарки"))
async def avatars_menu_cmd(message: types.Message):
    u = get_user(message.from_user.id)
    text = "🖼 <b>ГОТОВЫЕ АВАТАРКИ</b>\n"
    text += "━━━━━━━━━━━━━━━━\n"
    text += f"💰 Баланс: <b>{fmt(u['balance'])}</b>\n\n"
    for key, item in AVATARS.items():
        text += f"<code>{key}</code> — {item['name']} — {fmt(item['price'])}💰\n"
    text += "\nКупить: <code>купить_аву ключ</code>\n"
    text += "Своя: <code>аватарка</code>"
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().startswith("купить_аву "))
async def buy_avatar_cmd(message: types.Message):
    key = message.text[11:].strip().lower()
    if key not in AVATARS:
        await message.answer("❌ Нет. Напиши <code>аватарки</code>", parse_mode="HTML")
        return
    u = get_user(message.from_user.id)
    item = AVATARS[key]
    if u["balance"] < item["price"]:
        await message.answer(f"❌ Нужно {fmt(item['price'])}, у тебя {fmt(u['balance'])}", parse_mode="HTML")
        return
    inc(message.from_user.id, "balance", -item["price"])
    upd(message.from_user.id, "avatar", key)
    await message.answer(f"✅ <b>{item['name']}</b>\nНапиши <code>я</code>", parse_mode="HTML")
    try:
        await message.answer_photo(photo=item["file_id"], caption="✨")
    except Exception:
        pass

@dp.message(lambda m: m.text and m.text.lower().startswith("купить ") and not m.text.lower().startswith("купить_аву") and not m.text.lower().startswith("купить бизнес") and not m.text.lower().startswith("купить подарок") and not m.text.lower().startswith("купить вип"))
async def buy_cmd(message: types.Message):
    key = message.text[7:].strip().lower()
    if key not in SHOP:
        await message.answer("❌ Напиши <code>магазин</code>", parse_mode="HTML")
        return
    u = get_user(message.from_user.id)
    item = SHOP[key]
    if u["balance"] < item["price"]:
        await message.answer(f"❌ Нужно {fmt(item['price'])}, у тебя {fmt(u['balance'])}", parse_mode="HTML")
        return
    if key == "vip":
        if u["vip"]:
            await message.answer("💎 Уже есть")
            return
        upd(message.from_user.id, "vip", 1)
    elif key == "своя_аватарка":
        if u["custom_avatar_allowed"]:
            await message.answer("🖼 Уже есть. Напиши <code>аватарка</code>", parse_mode="HTML")
            return
        upd(message.from_user.id, "custom_avatar_allowed", 1)
        inc(message.from_user.id, "balance", -item["price"])
        waiting_for_photo.add(message.from_user.id)
        await message.answer("✅ Куплено!\n\n📸 Отправь мне фото — поставлю как аватарку.\n\n(Жду фото...)")
        return
    inc(message.from_user.id, "balance", -item["price"])
    await message.answer(f"✅ <b>{item['name']}</b>!", parse_mode="HTML")

@dp.message(lambda m: m.text and (m.text.lower().startswith("перевод ") or m.text.lower().startswith("перевести ") or m.text.lower().strip() in ("перевод", "перевести")))
async def pay_cmd(message: types.Message):
    text_lower = message.text.lower()
    if text_lower.startswith("перевести"):
        arg_start = 9
    elif text_lower.startswith("перевод"):
        arg_start = 7
    else:
        arg_start = len(message.text)
    raw = message.text[arg_start:].strip()
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if not raw:
            await message.answer("Использование: ответь на сообщение и напиши:\n<code>перевод Сумма</code>", parse_mode="HTML")
            return
        try:
            amount = int(raw)
        except ValueError:
            await message.answer("❌ Сумма должна быть числом")
            return
        if target.id == message.from_user.id:
            await message.answer("❌ Себе переводить нельзя")
            return
        if target.id == bot.id:
            await message.answer("❌ Боту переводить нельзя")
            return
        if amount <= 0:
            await message.answer("❌ Сумма > 0")
            return
        sender = get_user(message.from_user.id, message.from_user.first_name or "Игрок")
        if sender["balance"] < amount:
            await message.answer(f"❌ У тебя <b>{fmt(sender['balance'])}</b> монет", parse_mode="HTML")
            return
        get_user(target.id, target.first_name or "Игрок")
        inc(message.from_user.id, "balance", -amount)
        inc(target.id, "balance", amount)
        new_bal = get_user(message.from_user.id)["balance"]
        await message.answer(
            f"💸 Перевёл <b>{fmt(amount)}</b> → {html.escape(target.first_name)}\n"
            f"💰 Осталось: <b>{fmt(new_bal)}</b>",
            parse_mode="HTML"
        )
        return
    parts = raw.split()
    if len(parts) != 2:
        await message.answer("Использование:\n• <code>перевод Ник Сумма</code>\n• Реплаем: <code>перевод Сумма</code>", parse_mode="HTML")
        return
    nick = parts[0].strip().lstrip("@")
    try:
        amount = int(parts[1])
    except ValueError:
        await message.answer("❌ Сумма должна быть числом")
        return
    if amount <= 0:
        await message.answer("❌ Сумма > 0")
        return
    sender = get_user(message.from_user.id, message.from_user.first_name or "Игрок")
    if sender["balance"] < amount:
        await message.answer(f"❌ У тебя <b>{fmt(sender['balance'])}</b> монет", parse_mode="HTML")
        return
    target_id = find_user_by_nick(nick)
    if target_id is None:
        await message.answer(f"❌ '{html.escape(nick)}' не найден", parse_mode="HTML")
        return
    if target_id == message.from_user.id:
        await message.answer("❌ Себе переводить нельзя")
        return
    inc(message.from_user.id, "balance", -amount)
    inc(target_id, "balance", amount)
    new_bal = get_user(message.from_user.id)["balance"]
    await message.answer(
        f"💸 Перевёл <b>{fmt(amount)}</b> → {html.escape(nick)}\n"
        f"💰 Осталось: <b>{fmt(new_bal)}</b>",
        parse_mode="HTML"
    )

@dp.message(lambda m: m.text and m.text.lower().startswith("казино"))
async def casino_cmd(message: types.Message):
    arg = message.text[6:].strip().lower()
    u = get_user(message.from_user.id, message.from_user.first_name or "Игрок")
    if arg in ("все", "всё"):
        if u["balance"] <= 0:
            await message.answer("❌ У тебя нет монет")
            return
        bet = u["balance"]
    else:
        try:
            bet = int(arg)
        except ValueError:
            await message.answer("Использование:\n• <code>казино Сумма</code>\n• <code>казино все</code>", parse_mode="HTML")
            return
        if bet <= 0:
            await message.answer("❌ Ставка > 0")
            return
        if u["balance"] < bet:
            await message.answer(f"❌ У тебя <b>{fmt(u['balance'])}</b> монет", parse_mode="HTML")
            return
    win = random.random() < 0.45
    if win:
        inc(message.from_user.id, "balance", bet)
        inc(message.from_user.id, "total_earned", bet)
        inc(message.from_user.id, "wins", 1)
        await message.answer(
            f"🎉 <b>ВЫИГРАЛ {fmt(bet)}!</b>\n"
            f"💰 Баланс: <b>{fmt(get_user(message.from_user.id)['balance'])}</b>",
            parse_mode="HTML"
        )
    else:
        inc(message.from_user.id, "balance", -bet)
        inc(message.from_user.id, "losses", 1)
        await message.answer(
            f"😢 Проиграл <b>{fmt(bet)}</b>.\n"
            f"💰 Баланс: <b>{fmt(get_user(message.from_user.id)['balance'])}</b>",
            parse_mode="HTML"
        )

@dp.message(lambda m: m.text and m.text.lower().startswith("рулетка "))
async def roulette_cmd(message: types.Message):
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("рулетка Сумма чёт/нечет")
        return
    try:
        bet = int(parts[1])
    except ValueError:
        await message.answer("❌ Число")
        return
    choice = parts[2].lower()
    if choice not in ("чёт", "чет", "нечет", "нечёт"):
        await message.answer("❌ чёт/нечет")
        return
    u = get_user(message.from_user.id)
    if bet <= 0 or u["balance"] < bet:
        await message.answer("❌ Неверная")
        return
    rolled = random.randint(0, 36)
    is_even = rolled % 2 == 0
    user_wants_even = choice in ("чёт", "чет")
    win = (is_even == user_wants_even) and rolled != 0
    await message.answer(f"🎲 <b>{rolled}</b>", parse_mode="HTML")
    if win:
        inc(message.from_user.id, "balance", bet)
        inc(message.from_user.id, "total_earned", bet)
        inc(message.from_user.id, "wins", 1)
        await message.answer(
            f"🎉 +<b>{fmt(bet)}</b>! Баланс: <b>{fmt(get_user(message.from_user.id)['balance'])}</b>",
            parse_mode="HTML"
        )
    else:
        inc(message.from_user.id, "balance", -bet)
        inc(message.from_user.id, "losses", 1)
        await message.answer(
            f"😢 -<b>{fmt(bet)}</b>. Баланс: <b>{fmt(get_user(message.from_user.id)['balance'])}</b>",
            parse_mode="HTML"
        )

@dp.message(lambda m: m.text and m.text.lower().strip() in ("топ", "топы", "лидеры"))
async def top_cmd(message: types.Message):
    uid = message.from_user.id
    get_user(uid, message.from_user.first_name or "Игрок")
    await message.answer(build_top_rating(uid), reply_markup=top_inline("rating"), parse_mode="HTML")

@dp.callback_query(lambda c: c.data in ("top_rating", "top_money"))
async def top_callback(callback: types.CallbackQuery):
    uid = callback.from_user.id
    get_user(uid, callback.from_user.first_name or "Игрок")
    if callback.data == "top_rating":
        text = build_top_rating(uid)
    else:
        text = build_top_money(uid)
    try:
        await callback.message.edit_text(text, reply_markup=top_inline(), parse_mode="HTML")
    except Exception:
        pass
    try:
        await callback.answer()
    except Exception:
        pass

@dp.message(lambda m: m.text and m.text.lower().strip() in ("баланс", "монеты", "деньги", "кошелёк", "кошелек"))
async def balance_cmd(message: types.Message):
    u = get_user(message.from_user.id)
    await message.answer(
        f'<tg-emoji emoji-id="{PE_BALANCE}">💰</tg-emoji> <b>ТВОЙ БАЛАНС</b>\n'
        f"━━━━━━━━━━━━━━━━\n"
        f'<tg-emoji emoji-id="{PE_BALANCE}">🪙</tg-emoji> <b>{fmt(u["balance"])}</b> монет\n'
        f'<tg-emoji emoji-id="{PE_NEITCOINS}">💎</tg-emoji> <b>{u["neitcoins"]}</b> Нейткоинов',
        parse_mode="HTML"
    )

@dp.message(lambda m: m.text and m.text.lower().strip() in ("рейтинг", "реп", "rating"))
async def rating_cmd(message: types.Message):
    u = get_user(message.from_user.id)
    place = count_users_above_rating(u["rating"]) + 1
    rank = get_rank(u["rating"])
    await message.answer(
        f'<tg-emoji emoji-id="{PE_TOP_PLACE}">⭐</tg-emoji> <b>ТВОЙ РЕЙТИНГ</b>\n'
        f"━━━━━━━━━━━━━━━━\n"
        f'<tg-emoji emoji-id="{PE_TOP_PLACE}">⭐</tg-emoji> Рейтинг: <b>{fmt(u["rating"])}</b>\n'
        f'<tg-emoji emoji-id="{PE_RANK}">🎖</tg-emoji> Ранг: <b>{rank}</b>\n'
        f"🏆 Место: <b>#{place}</b>",
        parse_mode="HTML"
    )

@dp.message(lambda m: m.text and m.text.lower().startswith("ник "))
async def setname_cmd(message: types.Message):
    new_nick = message.text[4:].strip()
    if len(new_nick) < 2 or len(new_nick) > 20:
        await message.answer("❌ 2-20")
        return
    if find_user_by_nick(new_nick):
        await message.answer("❌ Занят")
        return
    get_user(message.from_user.id)
    upd(message.from_user.id, "nickname", new_nick)
    await message.answer(f"✅ Ник: <b>{html.escape(new_nick)}</b>", parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().strip() in ("бонус", "дейли", "награда", "ежедневно"))
async def daily_cmd(message: types.Message):
    u = get_user(message.from_user.id, message.from_user.first_name or "Игрок")
    now = time.time()
    if now - u["last_daily"] < 24 * 60 * 60:
        rem = int(24 * 60 * 60 - (now - u["last_daily"]))
        await message.answer(f"⏳ Через <b>{rem//3600}ч {(rem%3600)//60}мин</b>", parse_mode="HTML")
        return
    streak = u["daily_streak"] + 1 if (u["last_daily"] != 0 and now - u["last_daily"] < 48 * 3600) else 1
    bonus = 50 + (streak - 1) * 25
    inc(message.from_user.id, "balance", bonus)
    inc(message.from_user.id, "total_earned", bonus)
    upd(message.from_user.id, "last_daily", now)
    upd(message.from_user.id, "daily_streak", streak)
    await message.answer(
        f'<tg-emoji emoji-id="{PE_GIFT}">🎁</tg-emoji> +<b>{fmt(bonus)}</b>! (стрик <b>{streak}</b>)\n'
        f'<tg-emoji emoji-id="{PE_BALANCE}">💰</tg-emoji> {fmt(get_user(message.from_user.id)["balance"])}',
        parse_mode="HTML"
    )

@dp.message(lambda m: m.text and m.text.lower().strip() in ("работа", "работать", "заработать"))
async def work_cmd(message: types.Message):
    u = get_user(message.from_user.id, message.from_user.first_name or "Игрок")
    now = time.time()
    if now - u["last_work"] < 60 * 60:
        rem = int(60 * 60 - (now - u["last_work"]))
        await message.answer(f"😴 <b>{rem//60}мин</b>", parse_mode="HTML")
        return
    earnings = random.randint(20, 80)
    inc(message.from_user.id, "balance", earnings)
    inc(message.from_user.id, "total_earned", earnings)
    upd(message.from_user.id, "last_work", now)
    await message.answer(f"💼 {random.choice(['программистом', 'курьером', 'дизайнером', 'стримером', 'тестировщиком'])}, +<b>{fmt(earnings)}</b>!", parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().strip() in ("выдать_всем "))
async def richall_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔")
        return
    try:
        amount = int(message.text[12:].strip())
    except ValueError:
        await message.answer("❌")
        return
    with db_lock:
        cursor.execute("UPDATE users SET balance = balance + ?, total_earned = total_earned + ?", (amount, amount))
        db.commit()
    await message.answer(f"✅ По <b>{fmt(amount)}</b>", parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().startswith("выдать "))
async def give_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔")
        return
    try:
        amount = int(message.text[7:].strip())
    except ValueError:
        await message.answer("❌")
        return
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    get_user(target.id, target.first_name or "Игрок")
    inc(target.id, "balance", amount)
    inc(target.id, "total_earned", amount)
    await message.answer(f"✅ <b>{fmt(amount)}</b> → {html.escape(target.first_name)}", parse_mode="HTML")

@dp.message(lambda m: m.text and m.text.lower().strip() in ("сайт", "профиль на сайте", "мой сайт"))
async def site_cmd(message: types.Message):
    uid = message.from_user.id
    u = get_user(uid, message.from_user.first_name or "Игрок")
    businesses = get_user_businesses(uid)
    pets = get_user_pets(uid)
    base_url = "https://neit-ferriks.vercel.app" 
    params = {"id": uid, "nick": u["nickname"], "balance": u["balance"], "rating": u["rating"], "biz": sum(b["level"] for b in businesses), "pet": ", ".join(p["pet_name"] for p in pets) if pets else "Нет", "neitcoins": u["neitcoins"]}
    query_string = urllib.parse.urlencode(params)
    final_url = f"{base_url}/?{query_string}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📱 Открыть профиль на сайте", url=final_url)]])
    await message.answer(f"🌐 <b>Твой профиль на сайте!</b>\n\nНажми на кнопку ниже, чтобы открыть свою страницу.", reply_markup=kb, parse_mode="HTML")

@dp.message()
async def echo(message: types.Message):
    if not message.text:
        return
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
    if message.chat.type in ("group", "supergroup"):
        return
    await message.answer("🤔 Напиши <code>меню</code>", parse_mode="HTML")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

asyncio.run(main())
