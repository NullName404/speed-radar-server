from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = "8502815418"  # Замените на ваш

@app.route('/')
def index():
    return "✅ Speed Radar Server is running!"

@app.route('/upload', methods=['POST'])
def upload():
    try:
        photo = request.files['photo']
        speed = request.form.get('speed', 'неизвестно')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        caption = f"🚗 Проезд\n📅 {timestamp}\n📊 Скорость: {speed} км/ч"
        
        files = {'photo': (photo.filename, photo.read(), photo.mimetype)}
        data = {'chat_id': CHAT_ID, 'caption': caption}
        
        response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", files=files, data=data)
        
        if response.status_code == 200:
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"error": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
