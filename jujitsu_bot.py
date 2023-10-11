import sys
import requests
import time
import math

# token stoker dedans !! ne jamais faire apparaitre son token dans le code
token = sys.argv[1]  # pour cela click droit sur le fichier (bot.py) -> modify run configuration -> insérer le token dans la case prévue pour

#importation de tous les librairie utile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

def appeler_opendata(path):
    url = f'http://transport.opendata.ch/v1{path}'
    reponse = requests.get(url)
    return reponse.json()
def rechercher_arret(parametres):
    data = appeler_opendata(parametres)
    arret = data['stations']
    map = "https://www.google.com/maps?q="
    message_texte = f"Voici les résultats\n"

    for arret in arret:
        if arret['id']:
            message_texte = f"{message_texte} \n /s{arret['id']}"
            message_texte = f"{message_texte} {arret['name']}"
            message_texte = f"{message_texte} {arret['icon']}"

    return message_texte

def rechercher_prochai_depart(id):
    message_depart = "Voici les porchains départs : \n"
    data = appeler_opendata(f'/stationboard?id={id}')
    stationboard = data['stationboard']

    maintenant = time.time()
    for depart in stationboard:
        message_depart+= f"\n{depart['number']} -> {depart['to']}"

        timestamp = depart['stop']['departureTimestamp']
        diff = timestamp - maintenant
        temps_minute = math.floor(diff/60)

        if temps_minute < 0:
            message_depart+= ' Déjà parti ...'
        elif temps_minute <2:
            message_depart+= 'Cours il ne faut pas le rater !!'
        else:
            message_depart+= f'dans {temps_minute} minutes'

    return message_depart

#création de la fonction qui li /strat
async def start(update: Update, contexte: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Salut {update.effective_user.first_name}')

#création de la fonction qui li une chaine de caratère ou un texte
async def recreche_texte(update: Update, contexte: ContextTypes.DEFAULT_TYPE) -> None:
    arrets = rechercher_arret(f'/locations?query={update.message.text}')
    print(arrets)
    await update.message.reply_text(arrets)

async def recreche_gps(update: Update, contexte: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    arrets = rechercher_arret(f'/locations?x={user_location.latitude}&y={user_location.longitude}')
    await update.message.reply_text(arrets)

async def afficher_arret(update: Update, contexte: ContextTypes.DEFAULT_TYPE) -> None:
    identifiant = update.message.text[2:]
    date = rechercher_prochai_depart(identifiant)
    await update.message.reply_text(date)

#Application builder pour notre token
app = ApplicationBuilder().token(token).build()

#detection du /start et lancement de la focnction start
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.COMMAND, afficher_arret))
#recherche grace à la localisation gps via le .LOCATION
app.add_handler(MessageHandler(filters.LOCATION, recreche_gps))
#detection du texte et lancement de la fonction recherche_texte
app.add_handler(MessageHandler(filters.TEXT, recreche_texte))

app.run_polling()