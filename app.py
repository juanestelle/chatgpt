from flask import Flask, request, jsonify
import requests
import openai

app = Flask(__name__)

WHATSAPP_TOKEN = "el_teu_token_meta"
WHATSAPP_PHONE_NUMBER_ID = "el_teu_phone_number_ID"
openai.api_key = "la_teva_clau_openai"

@app.route('/', methods=['GET'])
def home():
    return "Webhook funcionant correctament!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        from_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    except KeyError:
        return jsonify(success=True)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ets un assistent amable i útil."},
            {"role": "user", "content": message}
        ]
    )

    resposta_chatgpt = response['choices'][0]['message']['content']

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

    requests.post(whatsapp_url, json=payload, headers=headers)

    return jsonify(success=True)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    verify_token = "el_teu_token_de_verificacio"
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge")
    return "Error de verificació", 403

if __name__ == "__main__":
    app.run(port=5000)
