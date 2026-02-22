from flask import Flask, render_template, request
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------
# PROMPT TEMPLATES
# ---------------------------------------------------------

RECIPIENT_STYLES_EN = {
    "hair": "a casual but respectful message suitable for a hairdresser or barber.",
    "beauty": "a warm and friendly tone suitable for a lash or nail technician.",
    "massage": "a calm, polite message appropriate for a massage therapist or physiotherapist.",
    "therapy": "a very respectful, emotionally-aware message suitable for a mental health professional.",
    "doctor": "a formal, concise message suitable for a doctor or clinic appointment.",
    "general": "a neutral, everyday appointment cancellation message."
}

RECIPIENT_STYLES_FI = {
    "hair": "rentoon mutta kunnioittavaan sävyyn sopiva viesti kampaajalle tai parturille.",
    "beauty": "lämpimään ja ystävälliseen sävyyn sopiva viesti ripsi- tai kynsiteknikolle.",
    "massage": "rauhallinen ja asiallinen viesti hierojalle tai fysioterapeutille.",
    "therapy": "erittäin kunnioittava ja empaattinen viesti terapeutille.",
    "doctor": "virallinen ja ytimekäs viesti lääkärille tai terveysasemalle.",
    "general": "neutraali viesti, joka sopii yleisiin ajanvarauksiin."
}

TONE_EN = {
    "simple": "Keep the wording brief, direct, and uncomplicated.",
    "polite": "Use a warm, polite tone without sounding overly emotional.",
    "formal": "Use a professional, formal tone suitable for official communication."
}

TONE_FI = {
    "simple": "Pidä viesti lyhyenä, suorana ja yksinkertaisena.",
    "polite": "Käytä lämmintä ja kohteliasta sävyä ilman liiallista tunteellisuutta.",
    "formal": "Käytä virallista, asiallista ja ammattimaista sävyä."
}

# ---------------------------------------------------------
# GENERATION FUNCTION
# ---------------------------------------------------------

def generate_cancellation(language, recipient, tone, details):
    """Creates a cancellation message using gpt-4o-mini."""

    if language == "en":
        recipient_style = RECIPIENT_STYLES_EN.get(recipient, "")
        tone_style = TONE_EN.get(tone, "")
        prompt = f"""
Write an appointment cancellation message in English.

The message should be:
- {recipient_style}
- {tone_style}

Additional details to include (if provided):
{details if details else 'No additional details.'}

Do NOT add anything extra. Just return the final message.
"""
    else:
        recipient_style = RECIPIENT_STYLES_FI.get(recipient, "")
        tone_style = TONE_FI.get(tone, "")
        prompt = f"""
Kirjoita ajanvarauksen peruutusviesti suomeksi.

Viestin tulee olla:
- {recipient_style}
- {tone_style}

Lisätiedot, jos annettu:
{details if details else 'Ei lisätietoja.'}

Älä lisää muuta. Palauta vain valmis viesti.
"""

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=180
    )

    return response.choices[0].message["content"]


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    language = request.form.get("language")
    recipient = request.form.get("recipient")
    tone = request.form.get("tone")
    details = request.form.get("details", "")

    try:
        message = generate_cancellation(language, recipient, tone, details)
    except Exception as e:
        message = "Error generating message. Please try again."

    return render_template("result.html", message=message)


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)