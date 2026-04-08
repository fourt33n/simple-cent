from flask import Flask, render_template, request
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load OpenAI 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------
# PROMPT TEMPLATE FOR ROUTES
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

RECIPIENT_APOLOGY_EN = {
    "partner": "warm but still composed, acknowledging your role clearly.",
    "coworker": "polite, cooperative, and focused on maintaining good teamwork.",
    "boss": "professional, accountable, and respectful of hierarchy.",
    "associate": "businesslike, courteous, and clear",
    "client": "professional, reassuring, and showing responsibility.",
    "general": "clear, respectful, and mature"
}

RECIPIENT_APOLOGY_FI = {
    "partner": "lämmin mutta selkeä, oma vastuu tuodaan esiin ilman liioittelua.",
    "coworker": "kohtelias, yhteistyöhön keskittyvä ja selkeä.",
    "boss": "ammattimainen, asiallinen ja vastuullisuutta korostava.",
    "associate": "liikemaailmaan sopiva, kohtelias ja selkeä",
    "client": "ammattimainen, rauhoittava ja vastuuta ottava",
    "general": "selkeä, kunnioittava ja asiallinen"
}

TONE_APOLOGY_FI = {
    "soft": "pehmeä ja lämmin, mutta ei tunteellinen",
    "neutral": "kohtelias ja neutraali sävyltään",
    "formal": "asiallinen, viralline ja ammattimainen"
}

TONE_APOLOGY_EN = {
    "soft": "soft and warm, gentle but not overly emotional.",
    "neutral": "polite, clear, and neutral in emotional tone",
    "formal": "formal, respectful, and professional"
}

#_________________________________________________________
# PASSWORD CHECKER
#_________________________________________________________

def check_access(provided, correct):
    return provided and provided.strip() == correct.strip()

# ---------------------------------------------------------
# GENERATION FUNCTION
# ---------------------------------------------------------

def generate_cancellation(language, recipient, tone, details, recipient_name, your_name):
    """Creates a cancellation message using gpt-4o-mini."""

    if language == "en":
        recipient_style = RECIPIENT_STYLES_EN.get(recipient, "")
        tone_style = TONE_EN.get(tone, "")
        recipient_line = f"Recipient's name: {recipient_name}" if recipient_name else "No specific recipient name."
        sender_line = f"Sender's name: {your_name}" if your_name else "No sender name included."
        prompt = f"""
Write an appointment cancellation message in English.

The message should be:
- {recipient_style}
- {tone_style}

Additional details to include (if provided):
{details if details else 'No additional details.'}

{recipient_line}
{sender_line}

Do NOT add anything extra. Use names only if provided. Just return the final message.
"""
    else:
        recipient_style = RECIPIENT_STYLES_FI.get(recipient, "")
        tone_style = TONE_FI.get(tone, "")
        recipient_line = f"Vastaanottajan nimi: {recipient_name}" if recipient_name else "Ei vastaanottajan nimeä."
        sender_line = f"Lähettäjän nimi: {your_name}" if your_name else "Ei lähettäjän nimeä."
        prompt = f"""
Kirjoita ajanvarauksen peruutusviesti suomeksi.

Viestin tulee olla:
- {recipient_style}
- {tone_style}

Lisätiedot, jos annettu:
{details if details else 'Ei lisätietoja.'}

{recipient_line}
{sender_line}

Älä lisää muuta. Palauta vain valmis viesti.
"""

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():
    print("HOME ROUTE HIT")
    correct_password = os.getenv("CANCEL_PASSWORD")
    if request.method == "POST":
        key = request.form.get("key")
        if check_access(key, correct_password):
            return render_template("cancel.html")
        return render_template("access.html", error=True, action="/")
    return render_template("access.html", action="/")

@app.route("/reschedule", methods=["GET", "POST"])
def reschedule():
    correct_password = os.getenv("RESCHEDULE_PASSWORD")
    if request.method == "POST":
        key = request.form.get("key")
        if check_access(key, correct_password):
            return render_template("reschedule.html")
        return render_template("access.html", error=True, action="/reschedule")
    return render_template("access.html", action="/reschedule")

@app.route("/decline", methods=["GET", "POST"])
def decline():
    correct_password = os.getenv("DECLINE_PASSWORD")
    if request.method == "POST":
        key = request.form.get("key")
        if check_access(key, correct_password):
            return render_template("decline.html")
        return render_template("access.html", error=True, action="/decline")
    return render_template("access.html", action="/decline")

@app.route("/apology", methods=["GET", "POST"])
def apology():
    print("APOLOGY HIT")
    correct_password = os.getenv("APOLOGY_PASSWORD")
    if request.method == "POST":
        key = request.form.get("key")
        if check_access(key, correct_password):
            return render_template("apology.html") 
        return render_template("access.html", error=True, action="/apology")
    return render_template("access.html", action="/apology")


@app.route("/generate", methods=["POST"])
def generate():
    language = request.form.get("language")
    print("LANG RECIEVED:", language)
    recipient = request.form.get("recipient")
    recipient_name = request.form.get("recipient_name", "")
    your_name = request.form.get("your_name", "")
    tone = request.form.get("tone")
    details = request.form.get("details", "")

    try:
        message = generate_cancellation(language, recipient, tone, details, recipient_name, your_name)
    except Exception as e:
        message = "Error generating message. Please try again."

    return render_template("result.html", message=message, title="Your Cancellation", return_to="/")


# _________________________________________________________
# RESCHED
#__________________________________________________________

@app.route("/reschedule_generate", methods=["POST"])
def reschedule_generate():
    language = request.form.get("language")
    recipient = request.form.get("recipient")
    recipient_name = request.form.get("recipient_name")
    your_name = request.form.get("your_name")
    tone = request.form.get("tone")
    details = request.form.get("details")

    try:
        message = generate_reschedule(language, recipient, recipient_name, your_name, tone, details)
    except Exception:
        message = "Error generating message. Please try again."
    
    return render_template("result.html", message=message, title="Your Reschedule", return_to="/reschedule")

def generate_reschedule(language, recipient, recipient_name, your_name, tone, details):
    if language == "en":
        recipient_line = f"Recipient's name: {recipient_name}" if recipient_name else "No specific recipient name."
        sender_line = f"Sender's name: {your_name}" if your_name else "No sender name included."
        prompt = f"""
Write a clear and polite message requesting to reschedule an appointment.

Requirements:
- Appointment type (category): {recipient}
- Tone: {tone}
- {recipient_line}
- {sender_line}
- Keep it concise (3-5 sentences max)
- Clearly state that you cannot make the original time *but you still want the appointment*
- Politely ask for a new suitable time
- Include optional details ONLY if the user added any
- Do NOT cancel the appointment - only reschedule it

IMPORTANT RULES ABOUT NAMES:
- If a recipient name is provided, insert it directly into the message.
- If a sender name is provided, insert it directly into the message.
- Do NOT write placeholders like [Recipient's Name] or [Your Name].
- Do NOT rewrite the name, modify it, or replace it.
- Use the name exactly as the user typed it.
- If no names are provided, write the message normally without any placeholders.

Extra details provider by user:
{details if details else "No additional details."}

Return ONLY the final message.
"""
    else:
        recipient_line = f"Vastaanottajan nimi: {recipient_name}" if recipient_name else "Ei vastaanottajan nimeä."
        sender_line = f"Lähettäjän nimi: {your_name}" if your_name else "Ei lähettäjän nimeä."
        prompt = f"""
Kirjoita selkeä ja kohtelias viesti, jossa pyydetään ajan siirtämistä.

Vaatimukset:
- Vastaanottajan tyyppi: {recipient}
- {recipient_line}
- {sender_line}
- Sävy: {tone}
- Pidä viesti tiiviinä (3-5 lausetta)
- Kerro, ettet pääse sovittuna aikana, mutta haluat edelleen pitää ajan
- Pyydä uutta sopivaa aikaa
- Sisällytä lisätiedot vain, jos käyttäjä kirjoitti niitä
- Älä peru aikaa - vain siirrä sitä

TÄRKEÄT SÄÄNNÖT NIMIEN KÄYTÖSTÄ:
- Jos vastaanottajan nimi on annettu, lisää se suoraan viestiin.
- Jos lähettäjän nimi on annettu, lisää se suoraan viestiin.
- ÄLÄ käytä paikkamerkkejä kuten [Nimi] tai [Vastaanottajan nimi].
- Älä muuta tai keksi nimiä, käytä niitä juuri sellaisina kuin ne on kirjoitettu.
- Jos nimiä ei ole annettu, älä lisää tervehdyspaikkamerkkejä.

Käyttäjän antamat lisätiedot:
{details if details else "Ei lisätietoja."}

Palauta VAIN valmis viesti.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=180
    )
    return response.choices[0].message.content
# __________________________________________________________
# DECLINE
#___________________________________________________________

@app.route("/decline_generate", methods=["POST"])
def decline_generate():
    language = request.form.get("language")
    recipient = request.form.get("recipient")
    tone = request.form.get("tone")
    details = request.form.get("details")

    try:
        message = generate_decline(language, recipient, tone, details)
    except Exception as e:
        message = "Error generating message. Please try again."
    return render_template("result.html", message=message, title="Your Decline", return_to="/decline")


def generate_decline(language, recipient, tone, details):
    if language == "en":
        prompt = f"""
Write a polite decline message in English.

Context:
- Decline type: {recipient}
- Tone: {tone}
- Extra details: {details if details else "No extra details provided."}

Rules:
- Be clear but respectful.
- No passive-aggressive tone.
- Keep it concise.
- Do NOT add placeholders like [Name].

Return ONLY the final message.
"""
    else:
        prompt= f"""
Kirjoita kohtelias kieltäytymisviesti suomeksi.

Konteksti:
- Kieltäytymisen tyyppi: {recipient}
- Sävy: {tone}
- Lisätiedot: {details if details else "Ei lisätietoja."}

Säännöt:
- Ole selkeä mutta ystävällinen.
- Ei passiivis-aggressiivisuutta.
- Viesti oltava ytimekäs.
- Älä lisää paikkamerkkejä kuten [Nimi].

Palauta VAIN valmis viesti.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=180
    )
    return response.choices[0].message.content
    

#__________________________________________________________
# APOLOGY
#__________________________________________________________

def apology_ending(tone): ## THIS IS THE ENG VERSION
    if tone == "soft":
        return "I appreciate your understanding."
    elif tone == "neutral":
        return "Thank you for your understanding."
    elif tone == "formal":
        return "Please let me know if any clarification is needed."
    return "Thank you for your understanding."

def apology_ending_fi(tone):
    if tone == "soft":
        return "Arvostan ymmärrystäsi."
    elif tone == "neutral":
        return "Kiitos ymmärryksestäsi."
    elif tone == "formal":
        return "Ilmoitathan, jos jokin vaatii tarkennusta."
    return "Kiitos ymmärryksestäsi."


@app.route("/apology_generate", methods=["POST"])
def apology_generate():
    language = request.form.get("language")
    recipient = request.form.get("recipient")
    tone = request.form.get("tone")
    details = request.form.get("details")

    try:
        message = generate_apology(language, recipient, tone, details)
    except Exception as e:
        message = "Error generating message. Please try again."
    return render_template("result.html", message=message, title="Your Apology", return_to="/apology")


def generate_apology(language, recipient, tone, details):
    """Creates and apology message using gpt-4o-mini."""

    if language == "en":
        end_line = apology_ending(tone)
    else:
        end_line = apology_ending_fi(tone)

    if language == "en":
        recipient_style = RECIPIENT_APOLOGY_EN.get(recipient, "")
        tone_style = TONE_APOLOGY_EN.get(tone, "")

        prompt = f"""
Write an apology message in English.

CONTEXT:
- Who the apology is for: {recipient_style}
- Tone: {tone_style}
- Extra details: {details if details else "None provided."}

STRICT RULES:
- NO email format.
- NO subject lines.
- NO greetings like "Dear" or "To whom it may concern."
- NO placeholders like [Name].
- NO signatures with titles or companies.
- 3-5 sentences maximum.
- If extra details are provided, include them naturally.
- End with this line: {end_line}

Do NOT add anything extra. Return ONLY final message.
"""
    else:
        recipient_style = RECIPIENT_APOLOGY_FI.get(recipient, "")
        tone_style = TONE_APOLOGY_FI.get(tone, "")

        prompt = f"""
Kirjoita lyhyt anteeksipyyntö suomeksi.

KONTEKSTI:
- Kenelle anteeksipyyntö on: {recipient_style}
- Sävy: {tone_style}
- Lisätiedot: {details if details else "Ei lisätietoja."}

TARKAT SÄÄNNÖT:
- EI sähköpostimuotoa.
- EI otsikoita.
- EI tervehdyksiä kuten "Hyvä herra" tai "Arvoisa".
- EI paikanmerkkejä kuten [Nimi]
- EI allekirjoituksia, titteleitä tai yrityksiä.
- 3-5 virkettä.
- Luonnollinen ja viestityylinen
- Jos lisätietoja on annettu, sisällytä ne luonnollisesti.
- Päätä tähän lauseeseen: {end_line}


Palauta VAIN valmis viesti.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=180
    )
    return response.choices[0].message.content
# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

