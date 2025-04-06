import json
import os
import openai
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔐 API Key d'OpenAI (agafa la variable d'entorn de Render)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ✅ Dades reals de WhatsApp Business (les que ja tens configurades)
WHATSAPP_TOKEN = "EAAN6GZC00bRIBO5coczj3YuP6e0YnbBeya0lFyZB3RXxajAHGMks5w45sLeCkTsW9fek0jmhMm4xeYTjKT4GM1lhxCzybnNz1zApapUfr2wLxlhpr1uKilPainn8dWp5IZBbqMamJlcJvJBWfeY74ZByG60aXmZC7xeXMOuOL6m3ea7ZAkBCZB3ZAIlSSQFqkFPwJ1yvz6cYcVYWUXd6LKcVoJkNEhYZD"
WHATSAPP_PHONE_NUMBER_ID = "612217341968390"

# ✅ Carrega la base de coneixement extreta del teu e-commerce
with open("coneixement_mundoparquet.json", "r") as f:
    BASE = json.load(f)

def buscar_text_relevant(pregunta):
    """Mini simulador de cerca: selecciona el bloc de text més rellevant segons paraules claus."""
    paraules = pregunta.lower().split()
    resultats = []
    for bloc in BASE:
        coincidències = sum(p in bloc["text"].lower() for p in paraules)
        if coincidències > 0:
            resultats.append((coincidències, bloc["text"]))
    resultats.sort(reverse=True)
    return resultats[0][1] if resultats else ""

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("🔔 Missatge rebut:", data)

    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        from_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        print(f"💬 Missatge de {from_number}: {message}")
    except KeyError:
        print("⚠️ No hi ha missatge de text.")
        return jsonify(success=True)

    # Cerca contingut rellevant del web
    context = buscar_text_relevant(message)
    print("🔍 Context seleccionat:", context)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Ets un expert de MundoParquet. Parles com un venedor català del sud i només respons basant-te en aquest context:\n\n{context}"},
                {"role": "user", "content": message}
            ]
        )
        resposta_chatgpt = response.choices[0].message.content
    except Exception as e:
        print("❌ Error amb OpenAI:", e)
        resposta_chatgpt = "Ho sento, ara mateix no puc respondre. Torna-ho a intentar més tard."

    whatsapp_url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": resposta_chatgpt}
    }

    r = requests.post(whatsapp_url, json=payload, headers=headers)
    print("📤 Enviat a WhatsApp:", r.status_code, r.text)

    return jsonify(success=True)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    verify_token = "parquet2025"
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge")
    return "Error de verificació", 403
