import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests
metre = " Mètres"
token = sys.argv[1]

def rechercher_arrets(parametre):
    data = appeler_openData(parametre)
    arrets = data['stations']
    messageText = "Voici le résultat"
    for arret in arrets:
        if arret['id']:
            messageText = f"{messageText} \n{arret['id']}"
            messageText = f"{messageText} {arret['name']}"
            messageText = f"{messageText} {arret['icon']}"
            messageText = f"{messageText} {arret['distance'], metre}" 
    return messageText

def appeler_openData(path):
    url = f"https://transport.opendata.ch/v1{path}"
    reponse = requests.get(url)
    return reponse.json()


async def Start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def recherche_texte(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texteAchercher = update.message.text
    arrets = rechercher_arrets(f'/locations?query={texteAchercher}')
    await update.message.reply_text(arrets)


#permet en envoyant sa location d'avoir les coordonnées GPS
async def recherche_gps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    arrets = rechercher_arrets(f'/locations?x={user_location.latitude}&y={user_location.longitude}')
    await update.message.reply_text(arrets)

async def afficher_arret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    indentifiant = update.message.text[2:]
    await update.message.reply_text("Afficher arret" + indentifiant)

app = ApplicationBuilder().token(token).build()

app.add_handler(CommandHandler("start", Start))
app.add_handler(MessageHandler(filters.COMMAND, afficher_arret))
app.add_handler(MessageHandler(filters.TEXT, recherche_texte))
app.add_handler(MessageHandler(filters.LOCATION, recherche_gps))

app.run_polling()

