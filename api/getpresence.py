import os
import requests
from flask import Flask, request, jsonify

# Инициализация Flask приложения
app = Flask(__name__)

# URL официального Roblox API
ROBLOX_PRESENCE_API = "https://presence.roblox.com/v1/presence/users"

@app.route('/getpresence', methods=['POST'])
def get_user_presence_flask():
    
    # 1. Обработка входящего JSON-запроса
    try:
        data = request.json 
    except Exception:
        return jsonify({"error": "Invalid or missing JSON in request body"}), 400

    # 2. Проверка наличия 'userId'
    if not data or 'userId' not in data:
        return jsonify({"error": "Missing 'userId' key in JSON body"}), 400

    try:
        user_id = int(data.get('userId'))
    except ValueError:
        return jsonify({"error": "User ID must be a valid number"}), 400

    roblox_payload = {"userIds": [user_id]}
    
    # 3. Отправляем POST-запрос на официальный API Roblox
    try:
        # Убираем проверку SSL (verify=False) только для устранения возможных ошибок Vercel/requests, 
        # хотя обычно это не рекомендуется! Добавляем таймаут.
        roblox_response = requests.post(
            ROBLOX_PRESENCE_API, 
            json=roblox_payload,
            timeout=10, 
            verify=True # Возвращаем True, если проблема не в SSL.
        )
        roblox_response.raise_for_status() 
        roblox_data = roblox_response.json()

    except requests.exceptions.RequestException as e:
        print(f"Roblox API Request Failed: {e}")
        return jsonify({"error": f"Failed to reach Roblox API: {type(e).__name__}: {str(e)}"}), 502

    # 4. Обрабатываем ответ
    place_id = 0
    game_id = None
    
    presences = roblox_data.get('userPresences', [])
    
    if presences:
        user_data = presences[0]
        if user_data.get('userPresenceType') == 2: 
            place_id = user_data.get('placeId', 0)
            game_id = user_data.get('gameId', None)

    # 5. Возвращаем ответ
    return jsonify({
        "TargetPlaceId": place_id,
        "TargetGameId": game_id
    })

def handler(event, context):
    return app(event, context)
