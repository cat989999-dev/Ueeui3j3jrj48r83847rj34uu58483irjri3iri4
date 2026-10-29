import asyncio

# ================= PYROGRAM ASYNCIO FIX (FOR NEWER PYTHON VERSIONS) =================
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ====================================================================================

import datetime
import random
import html
import time
import re
from pyrogram import Client, filters, idle
from pyrogram.types import Message, CallbackQuery, ChatJoinRequest, BotCommand
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
import dns.resolver

# ================= PYDROID 3 / ANDROID DNS FIX =================
# ... (बाकी का पूरा कोड इसके नीचे वैसा ही रहेगा) ...

# ================= PYDROID 3 / ANDROID DNS FIX =================
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

# ================= CONFIGURATION =================
BOT_TOKEN = "8873633012:AAHx-IKyeeECMLKatmXFgtSmMJ_xp2_w9pc"
API_ID = 35831190  
API_HASH = "f625657330797a7f149855cbdfcf9dae"
MONGO_URI = "mongodb+srv://Cricket_231:Rohit1616%40@zolmdho.mongodb.net/?appName=Cluster0" 
OWNER_ID = 7691071175 
TRACK_GROUP_ID = -1003946482336  
REQUIRED_USERNAME_TAG = "@redcube"

# ================= HTTP SESSION (For Fast API Calls) =================
HTTP_SESSION: aiohttp.ClientSession | None = None

async def get_session() -> aiohttp.ClientSession:
    global HTTP_SESSION
    if HTTP_SESSION is None or HTTP_SESSION.closed:
        connector = aiohttp.TCPConnector(limit=150, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=20, connect=8)
        HTTP_SESSION = aiohttp.ClientSession(connector=connector, timeout=timeout)
    return HTTP_SESSION

# Raw API Caller like bot_native.py (Prevents Pyrogram Stuck Issues)
async def tg(method: str, retries: int = 2, **params):
    clean = {k: v for k, v in params.items() if v is not None}
    base = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    req_timeout = 12
    for attempt in range(retries + 1):
        try:
            s = await get_session()
            async with s.post(base + method, json=clean, timeout=req_timeout) as r:
                res = await r.json()
            if res.get("ok"): return res["result"]
            retry_after = res.get("parameters", {}).get("retry_after")
            if retry_after and attempt < retries:
                await asyncio.sleep(min(float(retry_after), 5.0))
                continue
            raise RuntimeError(res.get("description", str(res)))
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            if attempt < retries:
                await asyncio.sleep(0.4)
                continue
            raise RuntimeError(f"Network timeout on {method}: {e}")

# ================= PREMIUM EMOJIS DATA =================
PREMIUM_EMOJIS = {
    "✅": "5123248930124989216",
    "❌": "5893197207493939355",
    "⚠️": "5420323339723881652",
    "💰": "5893473283696759404",
    "⛓️": "6021344879689341042",
    "📊": "5895444149699612825",
    "👥": "6021690418398239007",
    "🤖": "5931415565955503486",
    "💡": "6023897907034330805",
    "🎟": "6021617983774791539",
    "👨‍💻": "5444965061749644170",
    "🔐": "6019568309417023812",
    "🎉": "6023579259115674297",
    "⏱": "6034973034257848185",
    "🎁": "6023826881160157558",
    "🏆": "6021644067111180663",
    "📅": "6023880246128810031",
    "🛡": "6019328362479097179",
    "👑": "6021428854889913572",
    "📈": "5938539885907415367",
    "✏️": "5879841310902324730",
    "🏦": "5332455502917949981",
    "📍": "6023989024765516223",
    "🆕": "5886306834410640699",
    "👋": "5247133031235329609",
    "🌐": "6019205852831947754",
    "➡️": "5807462045288766810",
    "🇬🇧": "5395560546865013953",
    "🇷🇺": "5267224089382116952",
    "🇮🇳": "6129782715035163979",
    "💎": "5298988357538328017",
    "🏠": "5258503720928288433"
}

def pe(emoji_char: str) -> str:
    """Format emoji for TEXT messages."""
    eid = PREMIUM_EMOJIS.get(emoji_char)
    if eid: return f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
    return emoji_char

# ================= BUTTON & KEYBOARD GENERATORS =================
def btn(text: str, data: str = None, style: str = None, url: str = None, icon: str = None) -> dict:
    """Format emoji and colors for BUTTONS natively."""
    b = {"text": str(text)} 
    if url: b["url"] = str(url)
    else: b["callback_data"] = str(data) if data else "noop"
    if style: b["style"] = style
    if icon and icon in PREMIUM_EMOJIS: b["icon_custom_emoji_id"] = PREMIUM_EMOJIS[icon]
    return b

def kb(*rows) -> dict:
    board = []
    for row in rows:
        r = []
        for item in row:
            if isinstance(item, dict): r.append(item)
            elif len(item) >= 4: r.append(btn(item[0], item[1], style=item[2], icon=item[3]))
            elif len(item) == 3: r.append(btn(item[0], item[1], style=item[2]))
            elif len(item) == 2: r.append(btn(item[0], item[1]))
            elif len(item) == 1: r.append(btn(item[0], item[0]))
        if r: board.append(r)
    return {"inline_keyboard": board}

# Fast Sending Methods
async def send_msg(chat_id: int, text: str, markup=None, parse_mode="HTML", reply_to: int = None, disable_web_page_preview=True):
    try:
        return await tg("sendMessage", chat_id=chat_id, text=text, reply_markup=markup, parse_mode=parse_mode, reply_to_message_id=reply_to, disable_web_page_preview=disable_web_page_preview)
    except Exception as e:
        print("Send Error:", e)

async def edit_msg(chat_id: int, message_id: int, text: str, markup=None, parse_mode="HTML", disable_web_page_preview=True):
    try:
        return await tg("editMessageText", chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    except Exception:
        return await send_msg(chat_id, text, markup=markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)


# ================= INITIALIZATION =================
app = Client("my_advanced_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

client = AsyncIOMotorClient(MONGO_URI, maxPoolSize=50)
db = client['AdvancedBotDB']
users_db = db['users']
admins_db = db['admins']
config_db = db['config']
activity_db = db['activity']
auth_groups_db = db['authorized_groups'] 

user_states = {}
active_tickets = {}   
pending_tickets = {}  
user_langs = {}  

# FAST CACHING SYSTEM (Prevents Bot Delay/Stuck)
ldb_cache = {"daily": {"data": None, "time": 0}, "weekly": {"data": None, "time": 0}, "monthly": {"data": None, "time": 0}}
ADMIN_CACHE = {"data": [], "time": 0}
CONFIG_CACHE = {"data": None, "time": 0}

# ================= LANGUAGE DICTIONARY =================
TR = {
    "en": {
        "welcome_head": f"Welcome <b>{{name}}</b>! {pe('👋')}\n\n",
        "welcome": f"{pe('✅')} <b>Welcome to the Tracker Bot!</b>\n\nTo verify your account:\n1. Add <code>{{tag}}</code> to your Telegram Name.\n2. Add this link to your Bio: {{link}}\n\nUse the buttons below to navigate.",
        "lang_set": f"{pe('✅')} Language set to English.",
        "verify_ok": f"{pe('✅')} <b>Verification Successful!</b> Your name and bio are now being tracked.",
        "verify_fail": f"{pe('❌')} <b>Verification Failed:</b>\nPlease ensure your name contains <code>{{tag}}</code> and your bio has the tracking link.",
        "help": f"{pe('✏️')} <b>Available Commands:</b>\n/start - Open Menu\n/lang - Change Language\n/verify - Verify profile\n/affiliate - Get referral link\n/leaderboard - View Activity\n/support - Contact support\n/close - Close active ticket",
        "affiliate_link": f"{pe('⛓️')} <b>Your Personal Affiliate Link:</b>\n{{link}}\n\nShare this to invite users. We automatically track valid invites.",
        "affiliate_stats": f"{pe('📊')} <b>Affiliate Stats:</b>\n{pe('👥')} Real Invites: {{real}}\n{pe('🤖')} Fake/Filtered: {{fake}}\n\n{pe('💡')} You get ${{reward}} for every {{req}} valid members.",
        "sup_ask": f"{pe('✏️')} Please describe your issue in a single message. (Reason for support):",
        "sup_sent": f"{pe('✅')} Your request has been sent to the admins. Ticket Number: <b>{{tkt}}</b>\nPlease wait for an admin to accept it.",
        "sup_pending": f"{pe('⚠️')} You already have a pending or active support ticket. Please wait until it is resolved.",
        "tkt_joined": f"{pe('👨‍💻')} <b>An admin has joined the chat!</b>\nYou can now talk directly to them.",
        "tkt_closed": f"{pe('🔐')} <b>Your ticket has been closed.</b>",
        "tkt_rejected": f"{pe('❌')} <b>Your ticket ({{tkt}}) has been rejected by an admin.</b>",
        "draw_none": "No draw results available yet.",
        "draw_res": f"{pe('🎉')} <b>DAILY DRAW RESULTS</b> {pe('🎉')}\n\n{pe('⏱')} <b>Time:</b> {{time}}\n{pe('👥')} <b>Total Participants:</b> {{total}}\n{pe('🎁')} <b>Prize:</b> ${{amt}} each\n\n{pe('🏆')} <b>Winners:</b>\n{{winners}}",
        "wd_addr": f"{pe('📍')} Please send your {pe('💎')} TON withdrawal address:\n\n<b>Example:</b> <code>UQ...</code>",
        "wd_rej": f"{pe('❌')} <b>Withdrawal Rejected!</b>\nAmount: ${{amount}}\nReason: {{reason}}\nFunds refunded."
    },
    "ru": {
        "welcome_head": f"Добро пожаловать <b>{{name}}</b>! {pe('👋')}\n\n",
        "welcome": f"{pe('✅')} <b>Добро пожаловать в Tracker Bot!</b>\n\nДля верификации аккаунта:\n1. Добавьте <code>{{tag}}</code> в ваше имя.\n2. Добавьте эту ссылку в Bio: {{link}}\n\nИспользуйте кнопки ниже.",
        "lang_set": f"{pe('✅')} Язык изменен на Русский.",
        "verify_ok": f"{pe('✅')} <b>Верификация пройдена!</b> Ваше имя и Bio отслеживаются.",
        "verify_fail": f"{pe('❌')} <b>Ошибка верификации:</b>\nУбедитесь, что ваше имя содержит <code>{{tag}}</code>, а в Bio есть ссылка.",
        "help": f"{pe('✏️')} <b>Команды:</b>\n/start - Меню\n/lang - Сменить язык\n/verify - Верификация\n/affiliate - Реферальная ссылка\n/leaderboard - Таблица лидеров\n/support - Поддержка\n/close - Закрыть тикет",
        "affiliate_link": f"{pe('⛓️')} <b>Ваша реферальная ссылка:</b>\n{{link}}\n\nПоделитесь ею для приглашения. Мы автоматически учитываем валидных пользователей.",
        "affiliate_stats": f"{pe('📊')} <b>Статистика:</b>\n{pe('👥')} Реальные: {{real}}\n{pe('🤖')} Фейки: {{fake}}\n\n{pe('💡')} Вы получаете ${{reward}} за каждых {{req}} пользователей.",
        "sup_ask": f"{pe('✏️')} Пожалуйста, опишите вашу проблему в одном сообщении (Причина обращения):",
        "sup_sent": f"{pe('✅')} Ваш запрос отправлен. Номер тикета: <b>{{tkt}}</b>\nПожалуйста, подождите ответа.",
        "sup_pending": f"{pe('⚠️')} У вас уже есть активный тикет. Дождитесь его закрытия.",
        "tkt_joined": f"{pe('👨‍💻')} <b>Администратор подключился!</b>\nТеперь вы можете общаться с ним.",
        "tkt_closed": f"{pe('🔐')} <b>Ваш тикет закрыт.</b>",
        "tkt_rejected": f"{pe('❌')} <b>Ваш тикет ({{tkt}}) был отклонен администратором.</b>",
        "draw_none": "Результаты розыгрыша пока недоступны.",
        "draw_res": f"{pe('🎉')} <b>РЕЗУЛЬТАТЫ РОЗЫГРЫША</b> {pe('🎉')}\n\n{pe('⏱')} <b>Время:</b> {{time}}\n{pe('👥')} <b>Участников:</b> {{total}}\n{pe('🎁')} <b>Приз:</b> ${{amt}} каждому\n\n{pe('🏆')} <b>Победители:</b>\n{{winners}}",
        "wd_addr": f"{pe('📍')} Пожалуйста, отправьте ваш адрес {pe('💎')} TON:\n\n<b>Пример:</b> <code>UQ...</code>",
        "wd_rej": f"{pe('❌')} <b>Вывод отклонен!</b>\nСумма: ${{amount}}\nПричина: {{reason}}\nСредства возвращены."
    },
    "hi": {
        "welcome_head": f"स्वागत है <b>{{name}}</b>! {pe('👋')}\n\n",
        "welcome": f"{pe('✅')} <b>ट्रैकर बॉट में आपका स्वागत है!</b>\n\nअपने अकाउंट को वेरीफाई करने के लिए:\n1. अपने टेलीग्राम नाम में <code>{{tag}}</code> जोड़ें।\n2. अपने Bio में यह लिंक जोड़ें: {{link}}\n\nनेविगेट करने के लिए नीचे दिए गए बटन्स का उपयोग करें।",
        "lang_set": f"{pe('✅')} भाषा हिंदी में सेट हो गई है।",
        "verify_ok": f"{pe('✅')} <b>सत्यापन सफल!</b> आपका नाम और बायो अब ट्रैक किया जा रहा है।",
        "verify_fail": f"{pe('❌')} <b>सत्यापन विफल:</b>\nकृपया सुनिश्चित करें कि आपके नाम में <code>{{tag}}</code> है और आपके बायो में ट्रैकिंग लिंक है।",
        "help": f"{pe('✏️')} <b>उपलब्ध कमांड्स:</b>\n/start - मेन्यू खोलें\n/lang - भाषा बदलें\n/verify - प्रोफाइल वेरीफाई करें\n/affiliate - रेफरल लिंक प्राप्त करें\n/leaderboard - लीडरबोर्ड देखें\n/support - सहायता प्राप्त करें\n/close - सक्रिय टिकट बंद करें",
        "affiliate_link": f"{pe('⛓️')} <b>आपका पर्सनल एफिलिएट लिंक:</b>\n{{link}}\n\nयूजर्स को इनवाइट करने के लिए इसे शेयर करें।",
        "affiliate_stats": f"{pe('📊')} <b>एफिलिएट आँकड़े:</b>\n{pe('👥')} असली इनवाइट: {{real}}\n{pe('🤖')} फेक/फ़िल्टर: {{fake}}\n\n{pe('💡')} हर {{req}} मेंबर्स पर आपको ${{reward}} मिलेंगे।",
        "sup_ask": f"{pe('✏️')} कृपया अपनी समस्या एक मैसेज में लिखें (सहायता का कारण):",
        "sup_sent": f"{pe('✅')} आपका अनुरोध एडमिन को भेज दिया गया है। टिकट नंबर: <b>{{tkt}}</b>\nकृपया प्रतीक्षा करें।",
        "sup_pending": f"{pe('⚠️')} आपके पास पहले से ही एक सक्रिय टिकट है। कृपया इसके समाधान की प्रतीक्षा करें।",
        "tkt_joined": f"{pe('👨‍💻')} <b>एक एडमिन चैट में शामिल हो गया है!</b>\nअब आप सीधे उनसे बात कर सकते हैं।",
        "tkt_closed": f"{pe('🔐')} <b>आपका टिकट बंद कर दिया गया है।</b>",
        "tkt_rejected": f"{pe('❌')} <b>आपका टिकट ({{tkt}}) एडमिन द्वारा अस्वीकार कर दिया गया है।</b>",
        "draw_none": "अभी तक कोई ड्रा रिज़ल्ट उपलब्ध नहीं है।",
        "draw_res": f"{pe('🎉')} <b>डेली ड्रा रिज़ल्ट</b> {pe('🎉')}\n\n{pe('⏱')} <b>समय:</b> {{time}}\n{pe('👥')} <b>कुल प्रतिभागी:</b> {{total}}\n{pe('🎁')} <b>इनाम:</b> ${{amt}} प्रत्येक\n\n{pe('🏆')} <b>विजेता:</b>\n{{winners}}",
        "wd_addr": f"{pe('📍')} कृपया अपना {pe('💎')} TON निकासी पता भेजें:\n\n<b>उदाहरण:</b> <code>UQ...</code>",
        "wd_rej": f"{pe('❌')} <b>निकासी अस्वीकृत!</b>\nरकम: ${{amount}}\nकारण: {{reason}}\nफंड्स वापस कर दिए गए हैं।"
    }
}

# ================= HELPER FUNCTIONS =================
async def is_admin(user_id):
    if user_id == OWNER_ID: return True
    now = time.time()
    if now - ADMIN_CACHE["time"] > 300: # 5 Min cache to prevent DB overload and delays
        admins = await admins_db.find().to_list(100)
        ADMIN_CACHE["data"] = [a["user_id"] for a in admins]
        ADMIN_CACHE["time"] = now
    return user_id in ADMIN_CACHE["data"]

async def is_group_authorized(chat_id: int) -> bool:
    if chat_id > 0: return True 
    if chat_id == TRACK_GROUP_ID: return True
    return bool(await auth_groups_db.find_one({"chat_id": chat_id}))

async def get_lang(user_id):
    if user_id in user_langs: return user_langs[user_id]
    user = await users_db.find_one({"user_id": user_id})
    l = user.get("lang", "en") if user else "en"
    user_langs[user_id] = l
    return l

async def get_config():
    now = time.time()
    if CONFIG_CACHE["data"] and now - CONFIG_CACHE["time"] < 60: # 1 Min cache
        return CONFIG_CACHE["data"]
        
    conf = await config_db.find_one({"_id": "settings"})
    if not conf:
        conf = {
            "affiliate_reward": 3.0, 
            "affiliate_req": 100,
            "draw_winners_count": 10,
            "draw_amount": 2.0,
            "draw_enabled": True
        }
        await config_db.insert_one({"_id": "settings", **conf})
        
    CONFIG_CACHE["data"] = conf
    CONFIG_CACHE["time"] = now
    return conf

async def get_or_create_user(user_id, user_obj=None):
    user = await users_db.find_one({"user_id": user_id})
    name = "User"
    if user_obj:
        name = user_obj.first_name or "User"
        if user_obj.last_name: name += f" {user_obj.last_name}"
        
    if not user:
        user = {
            "user_id": user_id, "balance": 0.0, "bio_link": None, 
            "verified": False, "affiliates": [], "fake_affiliates": [], 
            "lang": "en", "won_draw": False, "name": name
        }
        await users_db.insert_one(user)
    elif user_obj and (user.get("name") != name or user.get("name") == "User"):
        await users_db.update_one({"user_id": user_id}, {"$set": {"name": name}})
        user["name"] = name
    return user

async def fetch_real_name(user_id, db_name):
    if db_name and db_name != "User":
        return db_name
    try:
        u = await app.get_users(user_id)
        name = u.first_name or "User"
        if u.last_name: name += f" {u.last_name}"
        await users_db.update_one({"user_id": user_id}, {"$set": {"name": name}})
        return name
    except:
        return "User"

def get_main_menu(lang: str):
    return kb(
        [("Verify", "menu_verify", "primary", "✅"), ("Affiliate", "menu_affiliate", "success", "⛓️")],
        [("Leaderboard", "menu_leaderboard", "primary", "🏆"), ("Draw", "menu_draw", "primary", "🎉")],
        [("Support", "menu_support", "danger", "🎟"), ("Language", "menu_lang", "primary", "🌐")]
    )

async def generate_leaderboard_text(period, page):
    today = datetime.date.today()
    if period == "daily":
        match_date = {"$gte": str(today)}
        title = "DAILY ACTIVITY RANKING"
    elif period == "weekly":
        match_date = {"$gte": str(today - datetime.timedelta(days=7))}
        title = "WEEKLY ACTIVITY RANKING"
    else: 
        match_date = {"$gte": str(today - datetime.timedelta(days=30))}
        title = "MONTHLY ACTIVITY RANKING"

    now = datetime.datetime.now().timestamp()
    cache_entry = ldb_cache.get(period)
    
    if cache_entry["data"] and (now - cache_entry["time"] < 60) and page == 0:
        pass 
    
    pipeline = [
        {"$match": {"date": match_date}},
        {"$group": {"_id": "$user_id", "total": {"$sum": "$message_count"}}},
        {"$sort": {"total": -1}},
        {"$skip": page * 10},
        {"$limit": 10},
        {"$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "user_id",
            "as": "user_info"
        }}
    ]
    
    results = await activity_db.aggregate(pipeline).to_list(length=10)
    unique_users_list = await activity_db.distinct("user_id", {"date": match_date})
    total_users_period = len(unique_users_list)
    max_pages = max(0, (total_users_period - 1) // 10)
    
    text = f"{pe('🏆')} <b>{title}</b> (Page {page+1}/{max_pages+1})\n\n"
    if not results:
        text += "<i>No activity recorded yet.</i>"
    else:
        for i, res in enumerate(results, start=(page*10)+1):
            user_info = res.get('user_info', [])
            db_name = user_info[0].get("name") if user_info else None
            name = await fetch_real_name(res['_id'], db_name)
            safe_name = html.escape(name)
            text += f"<b>{i}.</b> <a href='tg://user?id={res['_id']}'>{safe_name}</a> - {res['total']} msgs\n"
            
    if page == 0:
        ldb_cache[period] = {"data": (text, max_pages), "time": now}
        
    return text, max_pages

# ================= BACKGROUND VERIFICATION DETECTOR =================
async def background_verification_check():
    while True:
        try:
            verified_users = await users_db.find({"verified": True}).to_list(length=None)
            for u in verified_users:
                try:
                    chat_info = await app.get_chat(u["user_id"])
                    full_name = f"{chat_info.first_name or ''} {chat_info.last_name or ''}".lower()
                    name_ok = REQUIRED_USERNAME_TAG.lower() in full_name
                    bio_ok = u.get("bio_link") in (chat_info.bio or "")
                    
                    if not (name_ok and bio_ok):
                        await users_db.update_one({"user_id": u["user_id"]}, {"$set": {"verified": False}})
                        lang = await get_lang(u["user_id"])
                        msg = f"{pe('⚠️')} <b>Warning:</b> You have removed the required name tag or bio link! Your verification is revoked and you are disqualified from upcoming draws. Please add them back and send /verify."
                        if lang == "ru":
                            msg = f"{pe('⚠️')} <b>Внимание:</b> Вы удалили тег из имени или ссылку из Bio! Ваша верификация аннулирована. Пожалуйста, верните их и отправьте /verify."
                        elif lang == "hi":
                            msg = f"{pe('⚠️')} <b>चेतावनी:</b> आपने नाम से टैग या बायो से लिंक हटा दिया है! आपका सत्यापन रद्द कर दिया गया है। कृपया उन्हें वापस जोड़ें और /verify भेजें।"
                        try: await send_msg(u["user_id"], msg)
                        except: pass
                except: pass
                await asyncio.sleep(2) 
        except: pass
        await asyncio.sleep(120)

# ================= USER COMMANDS =================
@app.on_message(filters.command("lang") & filters.private)
async def lang_cmd(client: Client, message: Message):
    btns = kb(
        [("English", "lang_en", "primary", "🇬🇧"), ("Русский", "lang_ru", "danger", "🇷🇺")],
        [("हिंदी (Hindi)", "lang_hi", "success", "🇮🇳")]
    )
    await send_msg(message.chat.id, "Select your language / Выберите язык / भाषा चुनें:", markup=btns)

@app.on_message(filters.command("access"))
async def access_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    try:
        target_chat = int(message.command[1]) if len(message.command) > 1 else message.chat.id
        if target_chat > 0:
            return await send_msg(message.chat.id, f"{pe('⚠️')} Use this command inside a group, or provide a Group ID (-100xxxx).")
            
        await auth_groups_db.update_one({"chat_id": target_chat}, {"$set": {"chat_id": target_chat}}, upsert=True)
        await send_msg(message.chat.id, f"{pe('✅')} Group <code>{target_chat}</code> authorized successfully! Activity tracking and leaderboards will now work here.")
    except Exception as e:
        await send_msg(message.chat.id, "Usage: /access [group_id] or use in group.")

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user)
    lang = await get_lang(message.from_user.id)
    
    if not user.get("bio_link"):
        try:
            invite = await app.create_chat_invite_link(TRACK_GROUP_ID, name=f"Bio_{message.from_user.id}", creates_join_request=True)
            await users_db.update_one({"user_id": message.from_user.id}, {"$set": {"bio_link": invite.invite_link}})
            user["bio_link"] = invite.invite_link
        except:
            return await send_msg(message.chat.id, f"{pe('❌')} Group invite link error. Bot must be admin in Track Group.")

    welcome_head = TR[lang]["welcome_head"].format(name=html.escape(user['name']))
    await send_msg(message.chat.id, welcome_head, disable_web_page_preview=True)
    
    welcome_body = TR[lang]["welcome"].format(tag=REQUIRED_USERNAME_TAG, link=user['bio_link'])
    await send_msg(message.chat.id, welcome_body, markup=get_main_menu(lang), disable_web_page_preview=True)
    
    if await is_admin(message.from_user.id):
        await send_msg(message.chat.id, f"{pe('🛡')} <b>Admin Access Recognized!</b> Send /adminhelp to see your commands.")

@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    lang = await get_lang(message.from_user.id)
    await send_msg(message.chat.id, TR[lang]["help"])

@app.on_message(filters.command("verify") & filters.private)
async def verify_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = await get_or_create_user(user_id, message.from_user)
    lang = await get_lang(user_id)
    
    chat_info = await app.get_chat(user_id)
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".lower()
    
    name_ok = REQUIRED_USERNAME_TAG.lower() in full_name
    bio_ok = user_data.get("bio_link") in (chat_info.bio or "")

    if name_ok and bio_ok:
        await users_db.update_one({"user_id": user_id}, {"$set": {"verified": True}})
        await send_msg(message.chat.id, TR[lang]["verify_ok"])
    else:
        await send_msg(message.chat.id, TR[lang]["verify_fail"].format(tag=REQUIRED_USERNAME_TAG))

@app.on_message(filters.command("affiliate") & filters.private)
async def affiliate_cmd(client: Client, message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user)
    lang = await get_lang(message.from_user.id)
    try:
        invite = await app.create_chat_invite_link(TRACK_GROUP_ID, name=f"Affiliate_{message.from_user.id}", creates_join_request=True)
        markup = kb(
            [("Affiliate Status", "menu_aff_stats", "primary", "📊")],
            [("Back", "menu_main", "danger", "❌")]
        )
        await send_msg(message.chat.id, TR[lang]["affiliate_link"].format(link=invite.invite_link), markup=markup)
    except:
        await send_msg(message.chat.id, f"{pe('❌')} Error creating link. Ensure bot is admin in the tracking group.")

@app.on_message(filters.command("draw") & filters.private)
async def show_draw_cmd(client: Client, message: Message):
    lang = await get_lang(message.from_user.id)
    conf = await get_config()
    
    if not conf.get("draw_enabled", True):
        return await send_msg(message.chat.id, f"{pe('⚠️')} <b>Draw now disabled, soon coming.</b>")

    draw_data = await config_db.find_one({"_id": "latest_draw"})
    
    if not draw_data or not draw_data.get("winners"):
        return await send_msg(message.chat.id, TR[lang]["draw_none"])
        
    winners_text = ""
    for i, wid in enumerate(draw_data["winners"], 1):
        u_doc = await users_db.find_one({"user_id": wid})
        db_name = u_doc.get("name") if u_doc else None
        name = await fetch_real_name(wid, db_name)
        winners_text += f"{i}. {html.escape(name)}\n"
        
    text = TR[lang]["draw_res"].format(
        time=draw_data["time"], total=draw_data["total"], 
        amt=draw_data.get("amount", 2.0), winners=winners_text
    )
    await send_msg(message.chat.id, text, disable_web_page_preview=True)

@app.on_message(filters.command(["daily", "weekly", "monthly", "leaderboard"]))
async def leaderboard_cmd(client: Client, message: Message):
    if message.chat.id < 0 and not await is_group_authorized(message.chat.id):
        return
        
    cmd = message.command[0].lower()
    period = cmd if cmd in ["daily", "weekly", "monthly"] else "weekly"
    
    text, max_pages = await generate_leaderboard_text(period, 0)
    
    btns = kb(
        [("Daily", "ldb_daily_0", "primary", "📅"), ("Weekly", "ldb_weekly_0", "success", "📅"), ("Monthly", "ldb_monthly_0", "primary", "📅")],
        [("Back", f"ldb_{period}_0" if message.chat.id > 0 else "noop", "danger", "❌"), ("Next", f"ldb_{period}_1", "primary", "➡️")]
    )
    await send_msg(message.chat.id, text, markup=btns, disable_web_page_preview=True)

@app.on_message(filters.command("support") & filters.private)
async def support_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    
    if user_id in active_tickets or user_id in pending_tickets:
        return await send_msg(message.chat.id, TR[lang]["sup_pending"])
        
    user_states[user_id] = {"state": "wait_for_support"}
    await send_msg(message.chat.id, TR[lang]["sup_ask"])

@app.on_message(filters.command("withdraw") & filters.private)
async def withdraw_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    conf = await get_config()
    
    if not conf.get("withdrawal_enabled", True): 
        return await send_msg(message.chat.id, f"{pe('⚠️')} Withdrawals are disabled.")
        
    user = await get_or_create_user(user_id, message.from_user)
    if user["balance"] <= 0: return await send_msg(message.chat.id, f"{pe('❌')} Your wallet balance is $0.")
        
    user_states[user_id] = {"state": "wait_for_method", "amount": user["balance"]}
    
    markup = kb(
        [("TON", "wd_method_ton", "primary", "💎")], 
        [("Cancel", "menu_main", "danger", "❌")]
    )
    await send_msg(message.chat.id, f"{pe('💰')} <b>Balance:</b> ${user['balance']}\n\nPlease select the withdrawal method:", markup=markup)

# ================= NAYA COMMAND HANDLER =================
@app.on_message(filters.command("close") & filters.private)
async def close_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check karna ki kya user kisi active ticket mein hai
    if user_id not in active_tickets: 
        return await send_msg(message.chat.id, "No active ticket.")
        
    target_id = active_tickets[user_id]
    
    # Active ticket se dono users (admin aur user) ko nikalna
    del active_tickets[user_id]
    if target_id in active_tickets: 
        del active_tickets[target_id]
        
    await send_msg(message.chat.id, f"{pe('✅')} Ticket closed.")
    
    # Dusre user (ya admin) ko bhi batana ki ticket close ho gaya hai
    try: 
        t_lang = await get_lang(target_id)
        await send_msg(target_id, TR[t_lang]["tkt_closed"])
    except Exception as e: 
        print(f"Error sending close message: {e}")
        
# ================= BACKGROUND TRACKERS =================
@app.on_chat_join_request(filters.chat(TRACK_GROUP_ID))
async def handle_join_request(client: Client, request: ChatJoinRequest):
    user_id = request.from_user.id
    await client.approve_chat_join_request(TRACK_GROUP_ID, user_id)
    
    if request.invite_link and request.invite_link.name and request.invite_link.name.startswith("Affiliate_"):
        inviter_id = int(request.invite_link.name.split("_")[1])
        inviter_data = await get_or_create_user(inviter_id)
        
        is_fake = request.from_user.is_bot or request.from_user.is_fake
        if is_fake:
            await users_db.update_one({"user_id": inviter_id}, {"$addToSet": {"fake_affiliates": user_id}})
        else:
            if user_id not in inviter_data.get("affiliates", []):
                await users_db.update_one({"user_id": inviter_id}, {"$addToSet": {"affiliates": user_id}})
                
                new_count = len(inviter_data.get("affiliates", [])) + 1
                conf = await get_config()
                if new_count % conf["affiliate_req"] == 0:
                    reward = conf["affiliate_reward"]
                    await users_db.update_one({"user_id": inviter_id}, {"$inc": {"balance": reward}})
                    lang = await get_lang(inviter_id)
                    msg = f"{pe('🎉')} <b>Congratulations!</b> You reached {conf['affiliate_req']} members. ${reward} added!"
                    if lang == "ru": msg = f"{pe('🎉')} <b>Поздравляем!</b> Вы пригласили {conf['affiliate_req']} участников. Вам начислено ${reward}!"
                    if lang == "hi": msg = f"{pe('🎉')} <b>बधाई हो!</b> आपने {conf['affiliate_req']} मेंबर्स जोड़ लिए हैं। आपके वॉलेट में ${reward} जुड़ गए हैं!"
                    try: await send_msg(inviter_id, msg)
                    except: pass

@app.on_message(filters.group, group=1)
async def group_activity_tracker(client: Client, message: Message):
    if not message.from_user: return
    if not await is_group_authorized(message.chat.id): return

    user_id = message.from_user.id
    full_name = message.from_user.first_name or "User"
    if message.from_user.last_name:
        full_name += f" {message.from_user.last_name}"
    
    today = str(datetime.date.today())
    await users_db.update_one({"user_id": user_id}, {"$set": {"name": full_name}}, upsert=True)
    await activity_db.update_one(
        {"user_id": user_id, "group_id": message.chat.id, "date": today},
        {"$inc": {"message_count": 1}}, upsert=True
    )

# ================= ADMIN COMMANDS =================
@app.on_message(filters.command("adminhelp") & filters.private)
async def adminhelp_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    text = (
        f"{pe('🛡')} <b>ADMIN COMMANDS MENU</b>\n\n"
        "🔸 `/redraw` - Draw daily winners (Activity weighted)\n"
        "🔸 `/toggledraw` - Enable/Disable Draw feature\n"
        "🔸 `/drawsettings [count] [amount]` - Set daily winners and prize amount\n"
        "🔸 `/addadmin [user_id]` - Add new admin\n"
        "🔸 `/removeadmin [user_id]` - Remove admin\n"
        "🔸 `/adminlist` - View all admins\n"
        "🔸 `/setprice [members] [amount]` - Update affiliate referral price\n"
        "🔸 `/togglewithdraw` - Turn withdrawals ON/OFF\n"
        "🔸 `/broadcast` - Reply to any msg to send to all users\n"
        "🔸 `/check [username/id]` - Check specific user's activity\n"
        "🔸 `/access` (in a group) - Authorize group for Leaderboard commands\n"
    )
    await send_msg(message.chat.id, text)

@app.on_message(filters.command("toggledraw"))
async def toggledraw_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    conf = await get_config()
    new_state = not conf.get("draw_enabled", True)
    await config_db.update_one({"_id": "settings"}, {"$set": {"draw_enabled": new_state}}, upsert=True)
    
    global CONFIG_CACHE
    CONFIG_CACHE["time"] = 0 
    
    await send_msg(message.chat.id, f"{pe('✅')} Draw is now <b>{'ENABLED' if new_state else 'DISABLED'}</b>.")

@app.on_message(filters.command("drawsettings"))
async def drawsettings_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        count = int(parts[1])
        amount = float(parts[2])
        await config_db.update_one({"_id": "settings"}, {"$set": {"draw_winners_count": count, "draw_amount": amount}}, upsert=True)
        await send_msg(message.chat.id, f"{pe('✅')} <b>Draw Settings Updated!</b>\nWinners per draw: {count}\nAmount per winner: ${amount}")
    except:
        await send_msg(message.chat.id, "Usage: /drawsettings [number_of_winners] [amount_per_winner]\nExample: `/drawsettings 10 2.5`")

@app.on_message(filters.command("redraw"))
async def redraw_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    
    conf = await get_config()
    win_count = conf.get("draw_winners_count", 10)
    win_amt = conf.get("draw_amount", 2.0)
    
    users = await users_db.find({"verified": True, "won_draw": {"$ne": True}}).to_list(length=None)
    
    if len(users) < win_count:
        await users_db.update_many({"verified": True}, {"$set": {"won_draw": False}})
        users = await users_db.find({"verified": True, "won_draw": {"$ne": True}}).to_list(length=None)
        
    if not users: return await send_msg(message.chat.id, f"{pe('❌')} No verified users available to draw.")

    today = str(datetime.date.today() - datetime.timedelta(days=7))
    activity = await activity_db.aggregate([
        {"$match": {"date": {"$gte": today}}},
        {"$group": {"_id": "$user_id", "total": {"$sum": "$message_count"}}}
    ]).to_list(length=None)
    
    act_dict = {a["_id"]: a["total"] for a in activity}
    
    population = []
    weights = []
    for u in users:
        population.append(u)
        w = 1 + act_dict.get(u["user_id"], 0)
        weights.append(w)
        
    valid_winners = []
    
    while len(valid_winners) < win_count and population:
        winner = random.choices(population, weights=weights, k=1)[0]
        idx = population.index(winner)
        population.pop(idx)
        weights.pop(idx)
        
        try:
            chat_info = await app.get_chat(winner['user_id'])
            full_name = f"{chat_info.first_name or ''} {chat_info.last_name or ''}".lower()
            name_ok = REQUIRED_USERNAME_TAG.lower() in full_name
            bio_ok = winner.get("bio_link") in (chat_info.bio or "")
            
            if name_ok and bio_ok:
                valid_winners.append(winner)
            else:
                await users_db.update_one({"user_id": winner['user_id']}, {"$set": {"verified": False}})
                lang = await get_lang(winner['user_id'])
                msg = f"{pe('⚠️')} <b>Draw Disqualified!</b> You removed the required name tag or bio link. Please /verify again."
                if lang == "ru":
                    msg = f"{pe('⚠️')} <b>Дисквалификация!</b> Вы удалили тег из имени или ссылку из Bio. Пожалуйста, отправьте /verify снова."
                elif lang == "hi":
                    msg = f"{pe('⚠️')} <b>ड्रॉ से अयोग्य!</b> आपने नाम से टैग या बायो से लिंक हटा दिया है। कृपया फिर से /verify करें।"
                try: await send_msg(winner['user_id'], msg)
                except: pass
        except:
            pass
            
    if not valid_winners:
        return await send_msg(message.chat.id, f"{pe('❌')} No strictly verified users found (all removed their tags/bio!).")

    winner_ids = [w['user_id'] for w in valid_winners]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_verified = await users_db.count_documents({"verified": True})
    
    for wid in winner_ids:
        await users_db.update_one({"user_id": wid}, {"$set": {"won_draw": True}, "$inc": {"balance": float(win_amt)}})
        lang = await get_lang(wid)
        msg = f"{pe('🎉')} <b>Congratulations!</b> You won ${win_amt} in today's draw based on your activity!" 
        if lang == "ru": msg = f"{pe('🎉')} <b>Поздравляем!</b> Вы выиграли ${win_amt} в розыгрыше за вашу активность!"
        if lang == "hi": msg = f"{pe('🎉')} <b>बधाई हो!</b> आपने अपनी सक्रियता (activity) के आधार पर आज के ड्रा में ${win_amt} जीते हैं!"
        try: await send_msg(wid, msg)
        except: pass

    await config_db.update_one(
        {"_id": "latest_draw"},
        {"$set": {"time": now, "total": total_verified, "winners": winner_ids, "amount": win_amt}}, upsert=True
    )
    await send_msg(message.chat.id, f"{pe('✅')} <b>Draw Completed!</b>\n{len(valid_winners)} strictly active winners selected and credited ${win_amt}.\nPublic list updated.")

@app.on_message(filters.command("addadmin"))
async def addadmin_cmd(client: Client, message: Message):
    if message.from_user.id != OWNER_ID: return
    try:
        target = int(message.text.split()[1])
        await admins_db.update_one({"user_id": target}, {"$set": {"user_id": target}}, upsert=True)
        await send_msg(message.chat.id, f"{pe('✅')} User <code>{target}</code> is now an Admin.")
    except: await send_msg(message.chat.id, "Usage: /addadmin [user_id]")

@app.on_message(filters.command("removeadmin"))
async def removeadmin_cmd(client: Client, message: Message):
    if message.from_user.id != OWNER_ID: return
    try:
        target = int(message.text.split()[1])
        await admins_db.delete_one({"user_id": target})
        await send_msg(message.chat.id, f"{pe('✅')} Admin <code>{target}</code> removed.")
    except: await send_msg(message.chat.id, "Usage: /removeadmin [user_id]")

@app.on_message(filters.command("adminlist"))
async def adminlist_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    admins = await admins_db.find().to_list(length=100)
    text = f"{pe('👑')} <b>Owner:</b> <code>{OWNER_ID}</code>\n\n{pe('🛡')} <b>Admins:</b>\n"
    for a in admins: text += f"- <code>{a['user_id']}</code>\n"
    await send_msg(message.chat.id, text)

@app.on_message(filters.command("setprice"))
async def setprice_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        m_req = int(parts[1])
        rew = float(parts[2])
        await config_db.update_one({"_id": "settings"}, {"$set": {"affiliate_req": m_req, "affiliate_reward": rew}}, upsert=True)
        await send_msg(message.chat.id, f"{pe('✅')} Price updated: ${rew} per {m_req} members.")
    except: await send_msg(message.chat.id, "Usage: /setprice [members] [reward amount]")

@app.on_message(filters.command("togglewithdraw"))
async def togglewd_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    conf = await get_config()
    new_state = not conf.get("withdrawal_enabled", True)
    await config_db.update_one({"_id": "settings"}, {"$set": {"withdrawal_enabled": new_state}}, upsert=True)
    
    global CONFIG_CACHE
    CONFIG_CACHE["time"] = 0 
    
    await send_msg(message.chat.id, f"{pe('✏️')} Withdrawals are now <b>{'ENABLED' if new_state else 'DISABLED'}</b>.")

@app.on_message(filters.command("broadcast"))
async def broadcast_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    if not message.reply_to_message: return await send_msg(message.chat.id, "Reply to a message to broadcast.")
    users = await users_db.find().to_list(length=None)
    sent = 0
    for u in users:
        try:
            await message.reply_to_message.copy(u["user_id"])
            sent += 1
            await asyncio.sleep(0.05) 
        except: pass
    await send_msg(message.chat.id, f"{pe('✅')} Broadcast complete. Sent to {sent} users.")

@app.on_message(filters.command(["check", "checkactivity"]))
async def checkactivity_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    try:
        target_input = message.text.split()[1]
        
        try:
            user_info = await app.get_users(target_input)
            target_id = user_info.id
        except:
            target_id = int(target_input)
            user_info = await app.get_users(target_id)
            
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)
        month_ago = today - datetime.timedelta(days=30)
        records = await activity_db.find({"user_id": target_id}).to_list(length=None)
        
        d_count = sum(r["message_count"] for r in records if r["date"] == str(today))
        w_count = sum(r["message_count"] for r in records if datetime.date.fromisoformat(r["date"]) >= week_ago)
        m_count = sum(r["message_count"] for r in records if datetime.date.fromisoformat(r["date"]) >= month_ago)
        
        safe_name = html.escape(user_info.first_name or "User")
        await send_msg(message.chat.id, f"{pe('📈')} <b>Activity Report for <a href='tg://user?id={target_id}'>{safe_name}</a> (<code>{target_id}</code>)</b>:\n\n{pe('📅')} <b>Today:</b> {d_count} msgs\n{pe('📅')} <b>This Week:</b> {w_count} msgs\n{pe('📅')} <b>This Month:</b> {m_count} msgs")
    except Exception as e: 
        await send_msg(message.chat.id, f"{pe('⚠️')} Usage: /check [username/id]\nError: {e}")


# ================= MAIN MENU & INLINE ROUTER =================
@app.on_callback_query(filters.regex("^menu_main$"))
async def cb_menu_main(client: Client, call: CallbackQuery):
    await call.answer()
    user = await get_or_create_user(call.from_user.id, call.from_user)
    lang = await get_lang(call.from_user.id)
    
    welcome_body = TR[lang]["welcome"].format(tag=REQUIRED_USERNAME_TAG, link=user['bio_link'])
    await edit_msg(call.message.chat.id, call.message.id, welcome_body, markup=get_main_menu(lang))

@app.on_callback_query(filters.regex("^menu_verify$"))
async def cb_menu_verify(client: Client, call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    user_data = await get_or_create_user(user_id, call.from_user)
    lang = await get_lang(user_id)
    
    chat_info = await app.get_chat(user_id)
    full_name = f"{call.from_user.first_name or ''} {call.from_user.last_name or ''}".lower()
    name_ok = REQUIRED_USERNAME_TAG.lower() in full_name
    bio_ok = user_data.get("bio_link") in (chat_info.bio or "")

    markup = kb([("Back", "menu_main", "danger", "❌")])
    if name_ok and bio_ok:
        await users_db.update_one({"user_id": user_id}, {"$set": {"verified": True}})
        await edit_msg(call.message.chat.id, call.message.id, TR[lang]["verify_ok"], markup=markup)
    else:
        await edit_msg(call.message.chat.id, call.message.id, TR[lang]["verify_fail"].format(tag=REQUIRED_USERNAME_TAG), markup=markup)

@app.on_callback_query(filters.regex("^menu_affiliate$"))
async def cb_menu_affiliate(client: Client, call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    user = await get_or_create_user(user_id, call.from_user)
    lang = await get_lang(user_id)
    
    invite_link = user.get("affiliate_link")
    if not invite_link:
        try:
            invite = await app.create_chat_invite_link(TRACK_GROUP_ID, name=f"Affiliate_{user_id}", creates_join_request=True)
            invite_link = invite.invite_link
            await users_db.update_one({"user_id": user_id}, {"$set": {"affiliate_link": invite_link}})
        except:
            return await send_msg(call.message.chat.id, "Error creating link. Bot must be admin.")
            
    markup = kb(
        [("Affiliate Status", "menu_aff_stats", "primary", "📊")],
        [("Back", "menu_main", "danger", "❌")]
    )
    await edit_msg(call.message.chat.id, call.message.id, TR[lang]["affiliate_link"].format(link=invite_link), markup=markup, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("^menu_aff_stats$"))
async def cb_menu_aff_stats(client: Client, call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    user = await get_or_create_user(user_id, call.from_user)
    lang = await get_lang(user_id)
    conf = await get_config()
    
    markup = kb([("Back", "menu_affiliate", "danger", "❌")])
    await edit_msg(call.message.chat.id, call.message.id, TR[lang]["affiliate_stats"].format(
        real=len(user.get("affiliates", [])), fake=len(user.get("fake_affiliates", [])), 
        reward=conf['affiliate_reward'], req=conf['affiliate_req']
    ), markup=markup)

@app.on_callback_query(filters.regex("^menu_support$"))
async def cb_menu_support(client: Client, call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    lang = await get_lang(user_id)
    
    if user_id in active_tickets or user_id in pending_tickets:
        return await send_msg(call.message.chat.id, "You already have an active/pending ticket.")
        
    user_states[user_id] = {"state": "wait_for_support"}
    markup = kb([("Cancel / Back", "menu_main", "danger", "❌")])
    await edit_msg(call.message.chat.id, call.message.id, TR[lang]["sup_ask"], markup=markup)

@app.on_callback_query(filters.regex("^menu_draw$"))
async def cb_menu_draw(client: Client, call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    lang = await get_lang(user_id)
    conf = await get_config()
    
    markup = kb([("Back", "menu_main", "danger", "❌")])
    
    if not conf.get("draw_enabled", True):
        return await edit_msg(call.message.chat.id, call.message.id, f"{pe('⚠️')} <b>Draw now disabled, soon coming.</b>", markup=markup)

    draw_data = await config_db.find_one({"_id": "latest_draw"})
    
    if not draw_data or not draw_data.get("winners"):
        return await edit_msg(call.message.chat.id, call.message.id, TR[lang]["draw_none"], markup=markup)
        
    winners_text = ""
    for i, wid in enumerate(draw_data["winners"], 1):
        u_doc = await users_db.find_one({"user_id": wid})
        db_name = u_doc.get("name") if u_doc else None
        name = await fetch_real_name(wid, db_name)
        winners_text += f"{i}. {html.escape(name)}\n"
        
    text = TR[lang]["draw_res"].format(
        time=draw_data["time"], total=draw_data["total"], 
        amt=draw_data.get("amount", 2.0), winners=winners_text
    )
    await edit_msg(call.message.chat.id, call.message.id, text, markup=markup, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("^menu_lang$"))
async def cb_menu_lang(client: Client, call: CallbackQuery):
    await call.answer()
    btns = kb(
        [("English", "lang_en", "primary", "🇬🇧"), ("Русский", "lang_ru", "danger", "🇷🇺")],
        [("हिंदी (Hindi)", "lang_hi", "success", "🇮🇳")],
        [("Back", "menu_main", "danger", "❌")]
    )
    await edit_msg(call.message.chat.id, call.message.id, "Select your language / Выберите язык / भाषा चुनें:", markup=btns)

# ================= YAHAN PAR NAYA LANGUAGE CHANGE HANDLER ADD KIYA GAYA HAI =================
@app.on_callback_query(filters.regex("^lang_(en|ru|hi)$"))
async def cb_set_lang(client: Client, call: CallbackQuery):
    await call.answer()
    new_lang = call.data.split("_")[1]
    user_id = call.from_user.id
    
    # DB me nayi language update kardo
    await users_db.update_one({"user_id": user_id}, {"$set": {"lang": new_lang}})
    user_langs[user_id] = new_lang
    
    # User object fetch karo
    user = await get_or_create_user(user_id, call.from_user)
    
    # Text ready karo (Language set message + Welcome message)
    text = TR[new_lang]["lang_set"] + "\n\n" + TR[new_lang]["welcome"].format(tag=REQUIRED_USERNAME_TAG, link=user.get('bio_link', ''))
    
    # Main menu dikha do nayi language ke sath
    await edit_msg(call.message.chat.id, call.message.id, text, markup=get_main_menu(new_lang))
# ===========================================================================================

@app.on_callback_query(filters.regex("^menu_leaderboard$"))
async def cb_menu_leaderboard(client: Client, call: CallbackQuery):
    await call.answer()
    text, max_pages = await generate_leaderboard_text("weekly", 0)
    btns = kb(
        [("Daily", "ldb_daily_0", "primary", "📅"), ("Weekly", "ldb_weekly_0", "success", "📅"), ("Monthly", "ldb_monthly_0", "primary", "📅")],
        [("Back", "menu_main" if call.message.chat.id > 0 else "noop", "danger", "❌"), ("Next", "ldb_weekly_1", "primary", "➡️")]
    )
    await edit_msg(call.message.chat.id, call.message.id, text, markup=btns, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("^menu_withdraw$"))
async def cb_menu_withdraw(client: Client, call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    lang = await get_lang(user_id)
    conf = await get_config()
    
    if not conf.get("withdrawal_enabled", True): 
        markup = kb([("Back", "menu_main", "danger", "❌")])
        return await edit_msg(call.message.chat.id, call.message.id, f"{pe('⚠️')} Withdrawals are disabled.", markup=markup)
        
    user = await get_or_create_user(user_id, call.from_user)
    if user["balance"] <= 0: 
        markup = kb([("Back", "menu_main", "danger", "❌")])
        return await edit_msg(call.message.chat.id, call.message.id, f"{pe('❌')} Your wallet balance is $0.", markup=markup)
        
    user_states[user_id] = {"state": "wait_for_method", "amount": user["balance"]}
    markup = kb(
        [("TON", "wd_method_ton", "primary", "💎")], 
        [("Cancel / Back", "menu_main", "danger", "❌")]
    )
    await edit_msg(call.message.chat.id, call.message.id, f"{pe('💰')} <b>Balance:</b> ${user['balance']}\n\nPlease select the withdrawal method:", markup=markup)

@app.on_callback_query(filters.regex("^wd_method_ton$"))
async def cb_wd_method_ton(client: Client, call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    lang = await get_lang(user_id)
    state_info = user_states.get(user_id, {})
    
    if state_info.get("state") != "wait_for_method":
        return await send_msg(call.message.chat.id, "Session expired. Please request withdrawal again.")
        
    user_states[user_id]["state"] = "wait_for_address"
    user_states[user_id]["method"] = "TON"
    markup = kb([("Cancel", "menu_main", "danger", "❌")])
    await edit_msg(call.message.chat.id, call.message.id, TR[lang]["wd_addr"], markup=markup)


@app.on_message(filters.private & filters.text & ~filters.regex(r"^/"))
async def message_handler(client: Client, message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    state = user_states.get(user_id, {}).get("state")
    
    name = message.from_user.first_name or "User"
    if message.from_user.last_name: name += f" {message.from_user.last_name}"
    safe_name = html.escape(name)
    
    # 1. Support Request 
    if state == "wait_for_support":
        reason = message.text
        del user_states[user_id]
        
        ticket_id = f"#TKT{random.randint(10000, 99999)}"
        pending_tickets[user_id] = ticket_id  
        
        # PURE TEXT BUTTONS - NO EMOJIS FOR ADMIN ACTIONS
        btns = kb(
            [("Accept", f"tktacc_{user_id}", "success"), ("Reject", f"tktrej_{user_id}", "danger")]
        )
        admin_text = f"{pe('🎟')} <b>New Support Ticket ({ticket_id})</b>\n{pe('👥')} User: <a href='tg://user?id={user_id}'>{safe_name}</a> (<code>{user_id}</code>)\n{pe('✏️')} <b>Reason:</b> {html.escape(reason)}"
        
        admins = await admins_db.find().to_list(100)
        for aid in set([OWNER_ID] + [a["user_id"] for a in admins]):
            try: await send_msg(aid, admin_text, markup=btns)
            except: pass
            
        markup = kb([("Back to Menu", "menu_main", "primary", "🏠")])
        return await send_msg(message.chat.id, TR[lang]["sup_sent"].format(tkt=ticket_id), markup=markup)

    # 2. Withdrawal Address Wait
    if state == "wait_for_address":
        address_info = message.text
        amount = user_states[user_id]["amount"]
        method = user_states[user_id].get("method", "TON")
        
        await users_db.update_one({"user_id": user_id}, {"$inc": {"balance": -amount}})
        del user_states[user_id]
        
        # PURE TEXT BUTTONS - NO EMOJIS FOR ADMIN ACTIONS
        btns = kb(
            [("Accept", f"wdone_{user_id}_{amount}", "success"), ("Reject", f"wrej_{user_id}_{amount}", "danger")]
        )
        
        admin_text = f"{pe('🆕')} <b>Withdrawal Request ({method})</b>\n{pe('👨‍💻')} User: <a href='tg://user?id={user_id}'>{safe_name}</a> (<code>{user_id}</code>)\n{pe('💰')} Amount: ${amount}\n{pe('📍')} Address: <code>{html.escape(address_info)}</code>"
        
        admins = await admins_db.find().to_list(100)
        for aid in set([OWNER_ID] + [a["user_id"] for a in admins]):
            try: await send_msg(aid, admin_text, markup=btns)
            except: pass
            
        markup = kb([("Back to Menu", "menu_main", "primary", "🏠")])
        return await send_msg(message.chat.id, f"{pe('✅')} Your {method} withdrawal request has been sent to admins.", markup=markup)

    # 3. Withdrawal Transaction Link (Admin Input)
    if state == "wait_for_txlink":
        if not await is_admin(user_id): return
        target_id = user_states[user_id]["target_id"]
        amount = user_states[user_id]["amount"]
        tx_link = message.text
        
        del user_states[user_id]
        
        t_lang = await get_lang(target_id)
        try: await send_msg(target_id, f"{pe('✅')} <b>Your withdrawal of ${amount} has been successfully processed!</b>\n\n{pe('⛓️')} <b>Transaction Link:</b> {html.escape(tx_link)}", disable_web_page_preview=True)
        except: pass
        
        return await send_msg(message.chat.id, f"{pe('✅')} Withdrawal marked as Paid and transaction link sent to user.")

    # 4. Withdrawal Reject Reason (Admin Input)
    if state == "wait_for_reason":
        if not await is_admin(user_id): return
        target_id = user_states[user_id]["target_id"]
        amount = user_states[user_id]["amount"]
        reason = message.text
        
        await users_db.update_one({"user_id": target_id}, {"$inc": {"balance": float(amount)}})
        del user_states[user_id]
        
        t_lang = await get_lang(target_id)
        try: await send_msg(target_id, TR[t_lang]["wd_rej"].format(amount=amount, reason=html.escape(reason)))
        except: pass
        return await send_msg(message.chat.id, f"{pe('✅')} Rejection reason sent and funds refunded to user.")

    # 5. Active Ticket Messaging
    if user_id in active_tickets:
        target_id = active_tickets[user_id]
        is_sender_admin = await is_admin(user_id)
        try: 
            if is_sender_admin:
                await message.copy(target_id)
            else:
                await message.forward(target_id)
        except: pass

# ================= CALLBACK QUERIES =================
@app.on_callback_query(filters.regex("^ldb_"))
async def ldb_callback(client: Client, call: CallbackQuery):
    await call.answer()
    _, period, page_str = call.data.split("_")
    req_page = int(page_str)
    
    _, max_pages = await generate_leaderboard_text(period, 0)
    
    if req_page < 0 or req_page > max_pages:
        return await send_msg(call.message.chat.id, "No more pages available! / Дальше страниц нет!")
        
    text, _ = await generate_leaderboard_text(period, req_page)
    
    btns = kb(
        [("Daily", "ldb_daily_0", "primary", "📅"), ("Weekly", "ldb_weekly_0", "success", "📅"), ("Monthly", "ldb_monthly_0", "primary", "📅")],
        [("Back", f"ldb_{period}_{req_page-1}" if req_page > 0 else ("menu_main" if call.message.chat.id > 0 else "noop"), "danger", "❌"), ("Next", f"ldb_{period}_{req_page+1}", "primary", "➡️")]
    )
    
    try: await edit_msg(call.message.chat.id, call.message.id, text, markup=btns)
    except: pass

@app.on_callback_query(filters.regex("^tktacc_"))
async def ticket_accept(client: Client, call: CallbackQuery):
    await call.answer()
    if not await is_admin(call.from_user.id): return
    target_id = int(call.data.split("_")[1])
    
    if target_id not in pending_tickets:
        return await send_msg(call.message.chat.id, "This ticket is no longer pending or has been closed.")
        
    pending_tickets.pop(target_id) 
    active_tickets[target_id] = call.from_user.id
    active_tickets[call.from_user.id] = target_id
    
    text = call.message.text or call.message.caption or ""
    safe_text = html.escape(text)
    
    admin_name = html.escape(call.from_user.first_name or "Admin")
    safe_text += f"\n\n{pe('✅')} <b>Accepted by <a href='tg://user?id={call.from_user.id}'>{admin_name}</a></b>"
    
    await edit_msg(call.message.chat.id, call.message.id, safe_text, markup=None)
    
    t_lang = await get_lang(target_id)
    await send_msg(target_id, TR[t_lang]["tkt_joined"])
    await send_msg(call.from_user.id, f"{pe('✅')} Session Started with <code>{target_id}</code>.\nUse /close to end.")

@app.on_callback_query(filters.regex("^tktrej_"))
async def ticket_reject(client: Client, call: CallbackQuery):
    await call.answer()
    if not await is_admin(call.from_user.id): return
    target_id = int(call.data.split("_")[1])
    
    text = call.message.text or call.message.caption or ""
    safe_text = html.escape(text)
    
    match = re.search(r"#TKT\d+", text)
    ticket_id = match.group(0) if match else "#TKT_UNKNOWN"
    
    if target_id in pending_tickets:
        del pending_tickets[target_id]
    
    admin_name = html.escape(call.from_user.first_name or "Admin")
    safe_text += f"\n\n{pe('❌')} <b>Rejected by <a href='tg://user?id={call.from_user.id}'>{admin_name}</a></b>"
    
    await edit_msg(call.message.chat.id, call.message.id, safe_text, markup=None)
    
    t_lang = await get_lang(target_id)
    try: await send_msg(target_id, TR[t_lang]["tkt_rejected"].format(tkt=ticket_id))
    except: pass

@app.on_callback_query(filters.regex("^wdone_"))
async def wd_done(client: Client, call: CallbackQuery):
    await call.answer()
    if not await is_admin(call.from_user.id): return
    
    _, target_id, amount = call.data.split("_")
    
    # Send admin into wait state for Tx Link
    user_states[call.from_user.id] = {"state": "wait_for_txlink", "target_id": int(target_id), "amount": amount}
    
    text = call.message.text or call.message.caption or ""
    safe_text = html.escape(text)
    safe_text += f"\n\n{pe('✏️')} <b>Processing...</b>"
    
    await edit_msg(call.message.chat.id, call.message.id, safe_text, markup=None)
    
    await send_msg(call.message.chat.id, f"{pe('✏️')} <b>Please type the Transaction Link for this withdrawal:</b>")

@app.on_callback_query(filters.regex("^wrej_"))
async def wd_reject(client: Client, call: CallbackQuery):
    await call.answer()
    if not await is_admin(call.from_user.id): return
    
    _, target_id, amount = call.data.split("_")
    user_states[call.from_user.id] = {"state": "wait_for_reason", "target_id": int(target_id), "amount": amount}
    
    text = call.message.text or call.message.caption or ""
    safe_text = html.escape(text)
    safe_text += f"\n\n{pe('✏️')} <b>Processing Rejection...</b>"
    
    await edit_msg(call.message.chat.id, call.message.id, safe_text, markup=None)
    
    await send_msg(call.message.chat.id, f"{pe('✏️')} <b>Please type the reason for rejection:</b>")

@app.on_callback_query(filters.regex("^close$"))
async def cb_close(client: Client, call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id not in active_tickets: 
        return await send_msg(call.message.chat.id, "No active ticket.")
        
    target_id = active_tickets[user_id]
    del active_tickets[user_id]
    if target_id in active_tickets: del active_tickets[target_id]
        
    await send_msg(call.message.chat.id, f"{pe('✅')} Ticket closed.")
    try: 
        t_lang = await get_lang(target_id)
        await app.send_message(target_id, TR[t_lang]["tkt_closed"])
    except: pass

# ================= DUMMY WEB SERVER (FOR RENDER) =================
async def web_server():
    async def handle(request):
        return web.Response(text="Bot is Alive and Running on Render! ✅")
    
    web_app = web.Application()
    web_app.router.add_get('/', handle)
    runner = web.AppRunner(web_app)
    await runner.setup()
    
    # Render environment se dynamically port lega, warna default 8080 use karega
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Fake Web Server Started on port {port} 🌐")

# ================= STARTUP =================
async def main():
    await app.start()
    
    # 1. Fake Web server ko background me start karna
    asyncio.create_task(web_server())
    
    # 2. Verification check start karna
    asyncio.create_task(background_verification_check())
    
    await app.set_bot_commands([
        BotCommand("start", "Start Menu"), BotCommand("lang", "Change Language"),
        BotCommand("help", "Commands list"), BotCommand("verify", "Verify account"),
        BotCommand("affiliate", "Referral link"),
        BotCommand("leaderboard", "Activity Leaderboard"), BotCommand("draw", "Latest draw results"), 
        BotCommand("support", "Contact support"), BotCommand("close", "Close ticket")
    ])
    print("Bot is successfully running! ✅ Blazing Fast Response & Pure Buttons Active.")
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())
