import os
import json
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Configuració
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = "612217341968390"

# System prompt editable — aquí defines el comportament del bot
SYSTEM_PROMPT = (
    "Ets un expert en terres laminats, parquets, vinílics, portes plegables, accessoris i instal·lació. "
    "Parles com un assessor proper, atent i pràctic. "
    "Dóna respostes clares, útils i amb llenguatge natural. "
    "Comença en castellà si no pots detectar l'idioma. "
    "Si no tens prou informació, recomana contactar amb l'equip humà."
)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("\U0001F514 Missatge rebut:", json.dumps(data, indent=2))

    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        from_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    except KeyError:
        return jsonify(success=True)

    try:
        # Crida directa a GPT amb system prompt editable
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        )
        resposta = response.choices[0].message.content

    except Exception as e:
        print("❌ Error amb OpenAI:", e)
        resposta = "Ho sento! Ara mateix no puc respondre. Torna-ho a provar en uns minuts."

    whatsapp_url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": resposta}
    }

    r = requests.post(whatsapp_url, json=payload, headers=headers)
    print("\U0001F50D PAYLOAD:", json.dumps(payload, indent=2))
    print("\U0001F50D HEADERS:", headers)
    print("\U0001F4E4 Enviat a WhatsApp:", r.status_code, r.text)

    return jsonify(success=True)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = "parquet2025"
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge")
    return "Error de verificació", 403
