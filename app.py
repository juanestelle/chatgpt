import os
import json
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Inicialització OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Configuració de WhatsApp
WHATSAPP_TOKEN = "POSA_AQUÍ_EL_TEU_TOKEN"
WHATSAPP_PHONE_NUMBER_ID = "612217341968390"

# ID del GPT personalitzat de MundoParquet
GPT_ID = "g-rSjrrRI65-mundoparquet"

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
        resposta_gpt = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": message}
            ],
            tools=[],
            tool_choice="auto",
            temperature=0.7,
            max_tokens=800,
            stream=False,
            user=from_number,
            extra_headers={"OpenAI-Beta": "assistants=v1"},
            path=f"/v1/gpts/{GPT_ID}/completions"
        )

        resposta = resposta_gpt.choices[0].message.content
    except Exception as e:
        print("❌ Error amb OpenAI:", e)
        resposta = "Ho sento, ara mateix no puc respondre. Torna-ho a intentar més tard."

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
    print("\U0001F4E4 Enviat a WhatsApp:", r.status_code, r.text)

    return jsonify(success=True)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = "parquet2025"
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge")
    return "Error de verificació", 403
