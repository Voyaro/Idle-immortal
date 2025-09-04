from flask import Flask
from threading import Thread
import time
import requests

app = Flask('')

@app.route('/')
def home():
    return "Discord Bot is Alive! 🚀"

def run():
    app.run(host='0.0.0.0', port=8080)

def ping_self():
    """Auto-ping sendiri setiap 5 menit"""
    while True:
        try:
            requests.get("https://your-repl-name.your-username.repl.co", timeout=10)
            print("✅ Successfully pinged self")
        except:
            print("❌ Failed to ping self")
        time.sleep(300)  # 5 menit

def keep_alive():
    """Jalankan Flask server dan auto-ping"""
    # Jalankan Flask server
    flask_thread = Thread(target=run)
    flask_thread.daemon = True
    flask_thread.start()

    # Jalankan auto-ping (opsional)
    ping_thread = Thread(target=ping_self)
    ping_thread.daemon = True
    ping_thread.start()

    print("🛡️  Keep-alive system activated!")