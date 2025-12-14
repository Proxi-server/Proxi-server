import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
ROBLOX_PRESENCE_API = "https://presence.roblox.com/v1/presence/users"

@app.route('/getpresence', methods=['POST'])
def get_user_presence_flask():
    try:
        data = request.json
        user_id = data.get('userId')
        if not user_id:
            return jsonify({"error": "Missing userId in request body"}), 400
    except Exception as e:
        return jsonify({"error": f"Invalid JSON or request: {str(e)}"}), 400

    roblox_payload = {"userIds": [user_id]}

    try:
        roblox_response = requests.post(ROBLOX_PRESENCE_API, json=roblox_payload)
        roblox_response.raise_for_status() 
        roblox_data = roblox_response.json()

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to reach Roblox API: {str(e)}"}), 500

    place_id = 0
    game_id = None

    presences = roblox_data.get('userPresences', [])

    if presences:
        user_data = presences[0]
        if user_data.get('userPresenceType') == 2:
            place_id = user_data.get('placeId', 0)
            game_id = user_data.get('gameId', None)

    return jsonify({
        "TargetPlaceId": place_id,
        "TargetGameId": game_id
    })

def handler(event, context):
    return app(event, context)
