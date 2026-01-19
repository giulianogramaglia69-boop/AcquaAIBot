import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Configurazione tramite variabili d’ambiente

TELEGRAM_TOKEN = os.environ.get(“TELEGRAM_TOKEN”)
GROQ_API_KEY = os.environ.get(“GROQ_API_KEY”)

# Inizializza client Groq

groq_client = Groq(api_key=GROQ_API_KEY)

# Dizionario per memorizzare la cronologia delle conversazioni

conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Gestisce il comando /start”””
user_id = update.effective_user.id
conversations[user_id] = []

```
await update.message.reply_text(
    "👋 Ciao! Sono un chatbot alimentato da Groq.\n"
    "Scrivi qualsiasi messaggio e ti risponderò!\n\n"
    "Comandi disponibili:\n"
    "/start - Inizia una nuova conversazione\n"
    "/reset - Cancella la cronologia della conversazione"
)
```

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Gestisce il comando /reset”””
user_id = update.effective_user.id
conversations[user_id] = []
await update.message.reply_text(“🔄 Conversazione resettata! Iniziamo da capo.”)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Gestisce i messaggi dell’utente”””
user_id = update.effective_user.id
user_message = update.message.text

```
# Inizializza la conversazione se non esiste
if user_id not in conversations:
    conversations[user_id] = []

# Aggiungi il messaggio dell'utente alla cronologia
conversations[user_id].append({
    "role": "user",
    "content": user_message
})

try:
    # Invia un'indicazione di "sta scrivendo..."
    await update.message.chat.send_action("typing")
    
    # Chiamata all'API Groq
    chat_completion = groq_client.chat.completions.create(
        messages=conversations[user_id],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1024,
    )
    
    # Estrai la risposta
    bot_response = chat_completion.choices[0].message.content
    
    # Aggiungi la risposta del bot alla cronologia
    conversations[user_id].append({
        "role": "assistant",
        "content": bot_response
    })
    
    # Limita la cronologia a 20 messaggi
    if len(conversations[user_id]) > 20:
        conversations[user_id] = conversations[user_id][-20:]
    
    # Invia la risposta
    await update.message.reply_text(bot_response)
    
except Exception as e:
    await update.message.reply_text(
        f"❌ Si è verificato un errore: {str(e)}\n"
        "Riprova tra qualche istante."
    )
    print(f"Errore: {e}")
```

def main():
“”“Funzione principale per avviare il bot”””
# Verifica che le variabili d’ambiente siano impostate
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
raise ValueError(“TELEGRAM_TOKEN e GROQ_API_KEY devono essere impostate come variabili d’ambiente”)

```
# Crea l'applicazione
app = Application.builder().token(TELEGRAM_TOKEN).build()

# Aggiungi gli handler
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Avvia il bot
print("🤖 Bot avviato su Render!")
app.run_polling(allowed_updates=Update.ALL_TYPES)
```

if **name** == “**main**”:
main()