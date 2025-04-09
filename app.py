import os
import json
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Configuració
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
WHATSAPP_TOKEN = os.environ.get("EAAN6GZC00bRIBO9NhqhcRVy0cMnLwxZAMZAmJL5ZAbFkZCkH1NHWZC2ZALdanK5EnffY4BtgfYh8di9AkAqTQ73VNoXtcfTdrm1bQDPMfwPibkUEJZAxdkLbCmcU9QnnkL8iCsYM3958HvyyenGZBBLQUZBz0u9coZCETasbCMwLLHzcebaBa7lvUjqnZAFgFhBWNoPUxr54SZBZB15lc8ck684yLEOqP7ZAuBX")
WHATSAPP_PHONE_NUMBER_ID = "612217341968390"
ASSISTANT_ID = "asst_5TFwLGxmWMBBqYD3tTbm0APi"

# Magatzem de fils
threads = {}

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
        # Reutilitzem fils per mantenir context
        if from_number not in threads:
            thread = client.beta.threads.create()
            threads[from_number] = thread.id
        else:
            thread_id = threads[from_number]

        client.beta.threads.messages.create(
            thread_id=threads[from_number],
            role="user",
            content=message
        )

        run = client.beta.threads.runs.create(
            thread_id=threads[from_number],
            assistant_id=ASSISTANT_ID
        )

        # Esperar que acabi (polling bàsic)
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=threads[from_number],
                run_id=run.id
            )
            if run_status.status == "completed":
                break

        messages = client.beta.threads.messages.list(thread_id=threads[from_number])
        resposta = messages.data[0].content[0].text.value

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
