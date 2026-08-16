import os
import json
import time
import requests
from datetime import datetime
from flask import Flask, request
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "8471373583"))
GROUP_ID = os.environ.get("GROUP_ID", "-1001234567890")
PORT = int(os.environ.get("PORT", 10000))

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not set!")
    exit(1)

print("✅ Bot token loaded!")

bot = TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# ============================================================
# FILES & DATA
# ============================================================
USERS_FILE = "users.json"
BLACKLIST_FILE = "blacklist.json"
ADMIN_IDS = [OWNER_ID]

# ============================================================
# DATA FUNCTIONS
# ============================================================
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return []

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(blacklist, f, indent=2)

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_blacklisted(user_id):
    return str(user_id) in load_blacklist()

def register_user(user_id, username=None, first_name=None):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "id": user_id,
            "username": username,
            "name": first_name or "Unknown",
            "joined": datetime.now().isoformat(),
            "banned": False
        }
        save_users(users)
    return users[str(user_id)]

# ============================================================
# STYLISH TEXT
# ============================================================
def stylish_text(text: str) -> str:
    stylish_chars = {
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ',
        'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ',
        'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ',
        'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 'ꜱ', 'T': 'ᴛ',
        'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ',
        'Z': 'ᴢ', 'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ',
        'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ',
        'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ',
        't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ'
    }
    result = ""
    for char in text:
        result += stylish_chars.get(char, char)
    return result

def make_green_button(text, callback=None, url=None):
    final_text = stylish_text(text)
    try:
        if callback:
            return InlineKeyboardButton(text=final_text, style="success", callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final_text, style="success", url=url)
        else:
            return InlineKeyboardButton(text=final_text, style="success")
    except:
        if callback:
            return InlineKeyboardButton(text=final_text, callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final_text, url=url)
        else:
            return InlineKeyboardButton(text=final_text)

# ============================================================
# START COMMAND
# ============================================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    user = register_user(user_id, username, first_name)
    
    if user.get("banned", False):
        bot.send_message(message.chat.id, "❌ You are banned!")
        return
    
    text = f"""
⭐ ═══《 📤 FORWARD BOT 》═══ ⭐

⭐ 👤 User: {first_name}
⭐ 🆔 ID: {user_id}
⭐ 👾 @{username or 'N/A'}

⭐ ═══════════════════════ ⭐

⭐ Send me any message (text/photo/video/document)
⭐ I will forward it to the group!

⭐ ═══════════════════════ ⭐

⭐ 👨‍💻 Developer: @iflexzyan
"""
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(KeyboardButton(stylish_text("📤 SEND TO GROUP")))
    markup.row(KeyboardButton(stylish_text("📊 STATUS")), KeyboardButton(stylish_text("ℹ️ ABOUT")))
    
    if is_admin(user_id):
        markup.row(KeyboardButton(stylish_text("⚙️ ADMIN PANEL")))
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

# ============================================================
# SEND TO GROUP BUTTON
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("📤 SEND TO GROUP") in m.text)
def send_to_group_btn(message):
    bot.send_message(message.chat.id, "📤 Send me the message you want to forward to the group!\n(Text, Photo, Video, Document, Audio, etc.)")

# ============================================================
# FORWARD ALL MESSAGES TO GROUP
# ============================================================
@bot.message_handler(func=lambda m: True, content_types=[
    'text', 'photo', 'video', 'document', 'audio', 'voice', 
    'animation', 'sticker', 'video_note', 'location', 'venue', 
    'contact', 'poll', 'dice'
])
def forward_to_group(message):
    try:
        user_id = message.from_user.id
        user = register_user(user_id, message.from_user.username, message.from_user.first_name)
        
        if user.get("banned", False):
            bot.send_message(message.chat.id, "❌ You are banned from forwarding!")
            return
        
        # ===== FORWARD TO GROUP =====
        try:
            forwarded = bot.forward_message(GROUP_ID, message.chat.id, message.message_id)
            
            # ===== SEND CONFIRMATION TO USER =====
            if message.text:
                preview = message.text[:50] + "..." if len(message.text) > 50 else message.text
                bot.send_message(
                    message.chat.id, 
                    f"✅ Message forwarded to group!\n\n📝 Preview: {preview}"
                )
            else:
                bot.send_message(
                    message.chat.id, 
                    f"✅ {message.content_type.title()} forwarded to group!"
                )
            
            # ===== NOTIFY ADMIN =====
            if is_admin(user_id):
                pass
            else:
                try:
                    bot.send_message(
                        OWNER_ID,
                        f"📤 New Forward\n👤 {message.from_user.first_name} (@{message.from_user.username or 'N/A'})\n🆔 {user_id}\n📋 Type: {message.content_type}"
                    )
                except:
                    pass
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Failed to forward: {str(e)}")
            
    except Exception as e:
        print(f"Forward error: {e}")

# ============================================================
# ADMIN PANEL
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("⚙️ ADMIN PANEL") in m.text)
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Unauthorized!")
        return
    
    users = load_users()
    blacklist = load_blacklist()
    
    text = f"""
⭐ ═══《 ⚙️ ADMIN PANEL 》═══ ⭐

⭐ 👥 Users: {len(users)}
⭐ 🚫 Blacklisted: {len(blacklist)}
⭐ 📤 Group ID: `{GROUP_ID}`

⭐ ═══════════════════════ ⭐

Commands:
/blacklist <id> - Blacklist user
/unblacklist <id> - Unblacklist user
/ban <id> - Ban user
/unban <id> - Unban user
/users - List all users
/group - Set group ID
/stats - Bot stats

⭐ ═══════════════════════ ⭐
"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ============================================================
# ADMIN COMMANDS
# ============================================================
@bot.message_handler(commands=['blacklist'])
def blacklist_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ /blacklist <id>")
        return
    try:
        user_id = parts[1]
        blacklist = load_blacklist()
        if user_id not in blacklist:
            blacklist.append(user_id)
            save_blacklist(blacklist)
            bot.send_message(message.chat.id, f"✅ User {user_id} blacklisted!")
        else:
            bot.send_message(message.chat.id, f"⚠️ User {user_id} already blacklisted!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID!")

@bot.message_handler(commands=['unblacklist'])
def unblacklist_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ /unblacklist <id>")
        return
    try:
        user_id = parts[1]
        blacklist = load_blacklist()
        if user_id in blacklist:
            blacklist.remove(user_id)
            save_blacklist(blacklist)
            bot.send_message(message.chat.id, f"✅ User {user_id} unblacklisted!")
        else:
            bot.send_message(message.chat.id, f"⚠️ User {user_id} not in blacklist!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID!")

@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ /ban <id>")
        return
    try:
        user_id = parts[1]
        users = load_users()
        if user_id in users:
            users[user_id]["banned"] = True
            save_users(users)
            bot.send_message(message.chat.id, f"✅ User {user_id} banned!")
        else:
            bot.send_message(message.chat.id, f"⚠️ User {user_id} not found!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID!")

@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ /unban <id>")
        return
    try:
        user_id = parts[1]
        users = load_users()
        if user_id in users:
            users[user_id]["banned"] = False
            save_users(users)
            bot.send_message(message.chat.id, f"✅ User {user_id} unbanned!")
        else:
            bot.send_message(message.chat.id, f"⚠️ User {user_id} not found!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID!")

@bot.message_handler(commands=['users'])
def users_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    if not users:
        bot.send_message(message.chat.id, "❌ No users!")
        return
    text = "⭐ ═══《 👥 USERS 》═══ ⭐\n\n"
    for uid, data in users.items():
        banned = "🚫" if data.get("banned", False) else "✅"
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {banned}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    for i in range(0, len(text), 3800):
        bot.send_message(message.chat.id, text[i:i+3800])

# ============================================================
# GROUP COMMAND - FIXED (global GROUP_ID sab se pehle)
# ============================================================
@bot.message_handler(commands=['group'])
def group_cmd(message):
    global GROUP_ID  # <-- SAB SE PEHLE
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, f"📤 Current Group ID: `{GROUP_ID}`\n\n/group <new_group_id>")
        return
    new_group = parts[1]
    GROUP_ID = new_group
    bot.send_message(message.chat.id, f"✅ Group ID set to: `{new_group}`")

# ============================================================
# STATS COMMAND
# ============================================================
@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    blacklist = load_blacklist()
    text = f"""
⭐ ═══《 📊 BOT STATS 》═══ ⭐

⭐ 👥 Users: {len(users)}
⭐ 🚫 Blacklisted: {len(blacklist)}
⭐ 📤 Group ID: `{GROUP_ID}`
⭐ 👑 Admins: {len(ADMIN_IDS)}

⭐ ═══════════════════════ ⭐
"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ============================================================
# STATUS BUTTON
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("📊 STATUS") in m.text)
def status_cmd(message):
    user_id = message.from_user.id
    user = register_user(user_id, message.from_user.username, message.from_user.first_name)
    
    text = f"""
⭐ ═══《 📊 YOUR STATUS 》═══ ⭐

⭐ 👤 Name: {user.get('name', 'Unknown')}
⭐ 🆔 ID: {user_id}
⭐ 👾 @{user.get('username', 'N/A')}
⭐ 📅 Joined: {user.get('joined', 'N/A')[:16]}

⭐ ═══════════════════════ ⭐
"""
    bot.send_message(message.chat.id, text)

# ============================================================
# ABOUT BUTTON
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("ℹ️ ABOUT") in m.text)
def about_cmd(message):
    text = """
⭐ ═══《 ℹ️ ABOUT 》═══ ⭐

⭐ 📤 FORWARD BOT
⭐ Send messages → Forward to group

⭐ 👨‍💻 Developer: @iflexzyan

⭐ ═══════════════════════ ⭐
"""
    bot.send_message(message.chat.id, text)

# ============================================================
# FLASK WEBHOOK
# ============================================================
@app.route('/', methods=['GET'])
def index():
    return "✅ FORWARD BOT is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    return '', 403

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("✅ FORWARD BOT STARTED!")
    print(f"✅ Owner: {OWNER_ID}")
    print(f"✅ Group ID: {GROUP_ID}")
    
    try:
        bot.remove_webhook()
        print("✅ Webhook removed!")
    except Exception as e:
        print(f"⚠️ {e}")
    
    try:
        hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        if hostname:
            webhook_url = f"https://{hostname}/{BOT_TOKEN}"
            bot.set_webhook(url=webhook_url)
            print(f"✅ Webhook set: {webhook_url}")
        else:
            print("⚠️ No hostname, using polling")
            bot.infinity_polling()
            exit()
    except Exception as e:
        print(f"⚠️ {e}, falling back to polling")
        bot.infinity_polling()
        exit()
    
    app.run(host='0.0.0.0', port=PORT)