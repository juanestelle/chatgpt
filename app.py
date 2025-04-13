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

# System prompt per defecte
DEFAULT_SYSTEM_PROMPT = (
    "Ets un expert en terres laminats, parquets, vinílics, portes plegables, accessoris i instal·lació. "
    "Parles com un assessor proper, atent i pràctic. "
    "Dóna respostes clares, útils i amb llenguatge natural. "
    "Comença en castellà si no pots detectar l'idioma. "
    "Si no tens prou informació, recomana contactar amb l'equip humà."
)

# Llegir system prompt des d'un fitxer si existeix
if os.path.exists("system_prompt.txt"):
    with open("system_prompt.txt", "r") as f:
        SYSTEM_PROMPT = f.read().strip()
else:
    SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT

# Manteniment de sessions (historial opcional per millorar el context)
conversations = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("🔔 Missatge rebut:", json.dumps(data, indent=2))

    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        from_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    except KeyError:
        return jsonify(success=True)

    # Fixar idioma per defecte (castellà)
    idioma_prompt = "Responde en castellano."
    full_prompt = f"{SYSTEM_PROMPT}\n\n{idioma_prompt}"

    # Gestionar context per número (opcional)
    history = conversations.get(from_number, [])
    history.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": full_prompt}] + history
        )
        resposta = response.choices[0].message.content
        history.append({"role": "assistant", "content": resposta})
        conversations[from_number] = history[-10:]  # Limitar context a últims 10 missatges

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
    print("🔍 PAYLOAD:", json.dumps(payload, indent=2))
    print("🔍 HEADERS:", headers)
    print("📤 Enviat a WhatsApp:", r.status_code, r.text)

    return jsonify(success=True)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = "parquet2025"
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge")
    return "Error de verificació", 403
