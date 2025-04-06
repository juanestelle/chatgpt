import json
import os
import openai
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔐 Clau d'OpenAI (des de Render)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ✅ Configuració WhatsApp
WHATSAPP_TOKEN = "EAAN6GZC00bRIBO5coczj3YuP6e0YnbBeya0lFyZB3RXxajAHGMks5w45sLeCkTsW9fek0jmhMm4xeYTjKT4GM1lhxCzybnNz1zApapUfr2wLxlhpr1uKilPainn8dWp5IZBbqMamJlcJvJBWfeY74ZByG60aXmZC7xeXMOuOL6m3ea7ZAkBCZB3ZAIlSSQFqkFPwJ1yvz6cYcVYWUXd6LKcVoJkNEhYZD"
WHATSAPP_PHONE_NUMBER_ID = "612217341968390"

# ✅ Carrega la base de coneixement
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
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Digues si aquest text està escrit en català, castellà, o si no ho pots saber. Només digues un d'aquests: 'català', 'castellà', o 'desconegut'."},
                {"role": "user", "content": text}
            ]
        )
        idioma = resp.choices[0].message.content.strip().lower()
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

    if idioma not in ["català", "castellà"]:
        resposta = "Per poder ajudar-te millor, em pots dir si prefereixes continuar en català o castellà?"
    else:
        context = buscar_text_relevant(message)
        instruccio = {
            "català": f"Ets un expert de MundoParquet. Respon de manera clara i amable en català (neutre). Usa només aquest context:\n\n{context}",
            "castellà": f"Eres un experto de MundoParquet. Responde de forma clara y amable en castellano. Usa solo este contexto:\n\n{context}"
        }

        try:
            resposta_gpt_
