from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
import easyocr
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not BOT_TOKEN:
    print("⚠️ ОШИБКА: TELEGRAM_TOKEN не найден в переменных окружения!")
    exit(1)

CHAT_ID = "8502815418"  # ← ЗДЕСЬ ВАШ CHAT ID

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
# =============================================

# Инициализируем EasyOCR (русский + английский)
reader = easyocr.Reader(['ru', 'en'], gpu=False)  # gpu=False для бесплатного Render

def recognize_plate(image_bytes):
    """Распознает номер машины на фото"""
    try:
        # Конвертируем байты в изображение для EasyOCR
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        # Распознаем текст
        results = reader.readtext(image_np, paragraph=False)
        
        # Ищем текст, похожий на номер (буквы + цифры)
        plate = None
        for (bbox, text, confidence) in results:
            # Простой фильтр: номер обычно содержит буквы и цифры
            if any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
                # Убираем пробелы и приводим к верхнему регистру
                cleaned = ''.join(text.split()).upper()
                # Пример: если длина от 6 до 9 символов и есть буквы/цифры
                if 6 <= len(cleaned) <= 9:
                    plate = cleaned
                    break
        return plate
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

@app.route('/')
def index():
    return "✅ Speed Radar Server is running! Send POST to /upload"

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'photo' not in request.files:
            return jsonify({"error": "No photo uploaded"}), 400
        
        photo = request.files['photo']
        image_bytes = photo.read()  # Читаем фото в байты для OCR
        
        speed = request.form.get('speed', 'неизвестно')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ===== РАСПОЗНАВАНИЕ НОМЕРА =====
        plate_number = recognize_plate(image_bytes)
        # =================================
        
        # Формируем сообщение
        caption = f"🚗 Проезд зафиксирован\n"
        caption += f"📅 Время: {timestamp}\n"
        caption += f"📊 Скорость: {speed} км/ч\n"
        
        if plate_number:
            caption += f"🔢 Номер: {plate_number}\n"
        else:
            caption += f"🔢 Номер: не распознан\n"
        
        # Проверяем превышение
        try:
            speed_num = float(speed)
            if speed_num > 20:
                caption += "\n⚠️ ПРЕВЫШЕНИЕ! (>20 км/ч)"
            else:
                caption += "\n✅ Скорость в норме"
        except:
            pass
        
        # Отправляем фото в Telegram
        files = {
            'photo': (photo.filename, image_bytes, photo.mimetype)
        }
        data = {
            'chat_id': CHAT_ID,
            'caption': caption
        }
        
        response = requests.post(TELEGRAM_API_URL, files=files, data=data)
        
        if response.status_code == 200:
            return jsonify({"status": "ok", "plate": plate_number}), 200
        else:
            return jsonify({"error": "Telegram API error", "details": response.text}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
