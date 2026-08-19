from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

# Токен бота берем из переменной окружения (безопасно!)
BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not BOT_TOKEN:
    print("⚠️ ОШИБКА: TELEGRAM_TOKEN не найден в переменных окружения!")
    exit(1)

# Ваш Chat ID (вставьте сюда свой!)
CHAT_ID = "8502815418"  # ← ЗДЕСЬ ВСТАВЬТЕ ВАШ CHAT ID (цифры)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

@app.route('/')
def index():
    return "✅ Speed Radar Server is running! Send POST to /upload"

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Проверяем, есть ли файл в запросе
        if 'photo' not in request.files:
            return jsonify({"error": "No photo uploaded"}), 400
        
        photo = request.files['photo']
        
        # Читаем скорость из формы (если передана)
        speed = request.form.get('speed', 'неизвестно')
        
        # Получаем текущее время
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Формируем подпись к фото
        caption = f"🚗 Проезд зафиксирован\n"
        caption += f"📅 Время: {timestamp}\n"
        caption += f"📊 Скорость: {speed} км/ч"
        
        # Проверяем превышение (если скорость - число)
        try:
            speed_num = float(speed)
            if speed_num > 20:
                caption += "\n⚠️ ПРЕВЫШЕНИЕ! (>20 км/ч)"
            else:
                caption += "\n✅ Скорость в норме"
        except:
            pass  # Если скорость не число, просто пропускаем

        # Отправляем фото в Telegram
        files = {
            'photo': (photo.filename, photo.stream, photo.mimetype)
        }
        data = {
            'chat_id': CHAT_ID,
            'caption': caption
        }
        
        response = requests.post(TELEGRAM_API_URL, files=files, data=data)
        
        if response.status_code == 200:
            return jsonify({"status": "ok", "message": "Photo sent to Telegram"}), 200
        else:
            return jsonify({"error": "Telegram API error", "details": response.text}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)