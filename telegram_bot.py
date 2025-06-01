import telebot
import requests
import re

BOT_TOKEN = "7672029423:AAH3WE6rZLjIxb0gGYR9XxqumqItsjvId2U"
SAFEBROWSING_API_KEY = "AIzaSyCY8hs7mBav6Ua_2b2EqqyudpArNFAiPNs"

bot = telebot.TeleBot(BOT_TOKEN)

# Welcome message for /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "👋 Welcome to TechHrpler Bot!\n"
        "Send me any website link, and I'll tell you if it's safe or dangerous.\n\n"
        "🔒 Privacy Policy: https: https://docs.google.com/document/d/1KYmjtxZWSDiyam8_cjO8G98xJuM29sIn2z0_yYgePcM/edit?usp=sharing\n"
        "📧 Contact: @TechHrlper_bot"
    )

# Extract the first URL from the message
def extract_url(text):
    match = re.search(r'https?://[^\s]+', text)
    return match.group() if match else None

# Keywords for suspicious links if Google API gives safe result
unsafe_keywords = [
    "casino", "bet", "gambling", "phishing", "scam", "hack", 
    "bitcoin", "investment", "lottery", "win", "bonus"
]

@bot.message_handler(content_types=['text'])
def check_url(message):
    url = extract_url(message.text)
    
    if not url:
        bot.reply_to(message, "❌ Please send a valid message containing a URL.")
        return

    url_lower = url.lower()
    matched_keywords = [kw for kw in unsafe_keywords if kw in url_lower]

    try:
        response = requests.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={SAFEBROWSING_API_KEY}",
            json={
                "client": {
                    "clientId": "telegram-bot",
                    "clientVersion": "1.0"
                },
                "threatInfo": {
                    "threatTypes": [
                        "MALWARE", "SOCIAL_ENGINEERING", 
                        "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"
                    ],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}]
                }
            }
        )

        data = response.json()

        if data.get("matches"):
            bot.reply_to(message, "⚠️ Caution: Google Safe Browsing has identified this site as unsafe")
        else:
            if matched_keywords:
                bot.reply_to(
                    message,
                    f"⚠️ Alert: This website has been flagged as suspicious based on keyword analysis: {', '.join(matched_keywords)}"
                )
            else:
                bot.reply_to(message, "✅ No threats detected. This website appears safe based on Google's security check")

    except Exception as e:
        print("Error:", e)
        bot.reply_to(message, "⚠️ Error while checking the URL. Please try again later.")

print("🤖 Bot is running...")
bot.polling()
