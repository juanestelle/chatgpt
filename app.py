@app.route('/prova_openai')
def prova_openai():
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ets un assistent de prova."},
                {"role": "user", "content": "Hola, això és una prova."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"


from flask import Flask, request, jsonify
import requests
from openai import OpenAI

app = Flask(__name__)

WHATSAPP_TOKEN = "EAAN6GZC00bRIBO5coczj3YuP6e0YnbBeya0lFyZB3RXxajAHGMks5w45sLeCkTsW9fek0jmhMm4xeYTjKT4GM1lhxCzybnNz1zApapUfr2wLxlhpr1uKilPainn8dWp5IZBbqMamJlcJvJBWfeY74ZByG60aXmZC7xeXMOuOL6m3ea7ZAkBCZB3ZAIlSSQFqkFPwJ1yvz6cYcVYWUXd6LKcVoJkNEhYZD"
WHATSAPP_PHONE_NUMBER_ID = "612217341968390"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ets un expert amable en parquets i terres laminats, i parles amb català del sud. Sempre ofereixes consells molt pràctics i detallats."},
            {"role": "user", "content": message}
        ]
    )

    resposta_chatgpt = response.choices[0].message.content

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
    verify_token = "parquet2025"
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge")
    return "Error de verificació", 403

if __name__ == "__main__":
    app.run(port=5000)
