import json
import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

WHATSAPP_TOKEN = "AQUÍ_EL_TEU_NOU_TOKEN"
WHATSAPP_PHONE_NUMBER_ID = "612217341968390"

with open("coneixement_mundoparquet.json", "r") as f:
    BASE = json.load(f)

def buscar_text_relevant(pregunta):
    paraules = pregunta.lower().split()
    resultats = []
    for bloc in BASE:
        coincidències = sum(p in bloc["text"].lower() for p in paraules)
        if coincidències > 0:
            resultats.append((coincidències, bloc["text"]))
    resultats.sort(reverse=True)
    return resultats[0][1] if resultats else ""

def detectar_idioma(text):
    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Digues si el següent text és en català, castellà o desconegut. Només respon amb una sola paraula: català, castellà o desconegut."},
                {"role": "user", "content": text}
            ]
        )
        idioma = resposta.choices[0].message.content.strip().lower()

        if any(p in text.lower() for p in ["castellà", "castellano", "en castellà", "en castellano"]):
            idioma = "castellà"
        elif any(p in text.lower() for p in ["català", "catalan", "en català"]):
            idioma = "català"

        print(f"🧭 Idioma detectat: {idioma}")
        return idioma
    except Exception as e:
        print("❌ Error detectant idioma:", e)
        return "desconegut"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("🔔 Missatge rebut:", data)

    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        from_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        print(f"💬 Missatge de {from_number}: {message}")
    except KeyError:
        return jsonify(success=True)

    idioma = detectar_idioma(message)

    if idioma == "desconegut" and len(message.split()) < 5:
        resposta = "Per poder ajudar-te millor, em pots dir si prefereixes continuar en català o castellà?"
    else:
        if idioma == "desconegut":
            idioma = "castellà"  # 🟡 Per defecte: castellà

        context = buscar_text_relevant(message)
        instruccio = {
            "català": f"Ets un expert de MundoParquet. Respon de manera clara i amable en català (neutre). Usa només aquest context:\n\n{context}",
            "castellà": f"Eres un experto de MundoParquet. Responde de forma clara y amable en castellano. Usa solo este contexto:\n\n{context}"
        }

        try:
            resposta_gpt = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": instruccio[idioma]},
                    {"role": "user", "content": message}
                ]
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
    print("📤 Enviat a WhatsApp:", r.status_code, r.text)

    return jsonify(success=True)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    verify_token = "parquet2025"
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge")
    return "Error de verificació", 403
