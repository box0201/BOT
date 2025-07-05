from telegram.ext import Application, ConversationHandler, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import re
from liste import TOKEN, chat_id
from telegram import BotCommand
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, BotCommand
import nest_asyncio
nest_asyncio.apply()

logging.basicConfig(level=logging.CRITICAL)
broj_kvote_dict = {}
bot = Bot(token=TOKEN)

kladionice = [
    "mozzart", "maxbet", "mekrur", "soccer", "oktagon",
    "balkan", "mystake", "superbet", "topbet", 'pinnbet',
    'betole', 'volcano', '365.rs'
]
user_selected = {}  # user_id -> set(kladionica)


def build_keyboard(selected_set):
    buttons = []
    row = []

    for i, name in enumerate(kladionice):
        label = f"{'✅' if name in selected_set else '☑️'} {name}"
        row.append(InlineKeyboardButton(label, callback_data=f"toggle:{name}"))

        # Dodaj red kada ima 2 dugmeta
        if len(row) == 2:
            buttons.append(row)
            row = []

    # Ako ostane još jedno dugme u redu
    if row:
        buttons.append(row)

    # Dodaj "Sačuvaj" dugme ispod svega
    buttons.append([InlineKeyboardButton("✅ Sačuvaj", callback_data="save")])

    return InlineKeyboardMarkup(buttons)
async def kladionica_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    selected = user_selected.get(user_id, set())
    markup = build_keyboard(selected)
    await update.message.reply_text("Izaberi kladionice:", reply_markup=markup)

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    data = query.data

    if user_id not in user_selected:
        user_selected[user_id] = set()

    if data.startswith("toggle:"):
        name = data.split(":")[1]
        if name in user_selected[user_id]:
            user_selected[user_id].remove(name)
        else:
            user_selected[user_id].add(name)
        await query.edit_message_reply_markup(reply_markup=build_keyboard(user_selected[user_id]))

    elif data == "save":
        izabrane = user_selected[user_id]
        with open("/content/drive/MyDrive/BOT/fudbal/kladionice.txt", "w") as f:
            for name in izabrane:
                f.write(name + "\n")
        tekst = "✅ Izabrane kladionice:\n" + "\n".join(f"• {k}" for k in izabrane)
        await query.edit_message_text(tekst)

async def send_image_via_telegram(image_buffer):
    await bot.send_photo(chat_id=chat_id, photo=image_buffer)

async def send(messages, tiho):
    """Šalje poruke putem Telegram bota."""
    for message in messages:    
        try:
            message = await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML", disable_notification=tiho)
            message_id = message.message_id
            if tiho:
              return message_id
        except Exception as e:
            logging.error(f"Greška prilikom slanja poruke: {e}")

async def delete_messages(message_ids):
    """Asinhrona funkcija za brisanje poruka."""
    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            logging.info(f"Poruka sa ID-jem {message_id} uspešno obrisana.")
        except Exception as e:
            logging.error(f"Greška prilikom brisanja poruke sa ID-jem {message_id}: {e}")


async def delete_all_messages():
    async for message in bot.get_chat_history(chat_id=chat_id, limit=10000):
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            print(f"Obrisana poruka: {message.message_id}")
        except Exception as e:
            print(f"Ne mogu da obrišem poruku {message.message_id}: {e}")

def arbitrazni_kalkulator_3(kvote, ulog, tolerancija=1000):
    kvota_1, kvota_2, kvota_3 = kvote

    najmanja_razlika = float('inf')
    najbolje_uloge = None

    for i in range(ulog - tolerancija, ulog, 100):
        ulog_1 = (i / kvota_1) / ((1 / kvota_1) + (1 / kvota_2) + (1 / kvota_3))
        ulog_2 = (i / kvota_2) / ((1 / kvota_1) + (1 / kvota_2) + (1 / kvota_3))
        ulog_3 = i - ulog_1 - ulog_2

        ulog_1 = round(ulog_1 / 100) * 100
        ulog_2 = round(ulog_2 / 100) * 100
        ulog_3 = round(ulog_3 / 100) * 100

        profit_1 = ulog_1 * kvota_1 - i
        profit_2 = ulog_2 * kvota_2 - i
        profit_3 = ulog_3 * kvota_3 - i

        razlika = abs(profit_1 - profit_2) + abs(profit_1 - profit_3) + abs(profit_2 - profit_3)

        if razlika < najmanja_razlika:
            najmanja_razlika = razlika
            najbolje_uloge = (ulog_1, ulog_2, ulog_3)

    i = sum(najbolje_uloge)
    profit_1 = najbolje_uloge[0] * kvota_1 - i
    profit_2 = najbolje_uloge[1] * kvota_2 - i
    profit_3 = najbolje_uloge[2] * kvota_3 - i
    profit = (profit_1 + profit_2 + profit_3) / 3

    return najbolje_uloge, round(profit, 2), round((profit / sum(najbolje_uloge)) * 100, 2)

def arbitrazni_kalkulator_spec(kvote, ulog, tolerancija=1000):
    kvota_1, kvota_2 = kvote
    najveća_razlika = float('-inf')
    najbolje_uloge = None
    for i in range(ulog - tolerancija, ulog, 100):  # Krećemo od uloga sa tolerancijom
        ulog_1 = (i / kvota_1) / ((1 / kvota_1) + (1 / kvota_2))  # Računamo ulog za prvu kvotu
        ulog_2 = i - ulog_1  # Drugi ulog je ostatak
        ulog_1 = round(ulog_1 / 100) * 100  # Zaokružujemo ulog na stotinu
        ulog_2 = round(ulog_2 / 100) * 100  # Zaokružujemo ulog na stotinu
        profit_1 = ulog_1 * kvota_1 - i  # Profit za prvu kvotu
        profit_2 = ulog_2 * kvota_2 - i  # Profit za drugu kvotu
        # Ako bilo koji profit ide ispod 0, preskačemo
        if profit_1 < 0 or profit_2 < 0:
            continue
        # Uslov: veći profit mora biti povezan s manjom kvotom
        if (profit_1 > profit_2 and kvota_1 > kvota_2) or (profit_2 > profit_1 and kvota_2 > kvota_1):
            continue
        razlika = abs(profit_1 - profit_2)  # Računamo razliku
        if razlika > najveća_razlika:  # Tražimo najveću razliku
            najveća_razlika = razlika
            najbolje_uloge = (ulog_1, ulog_2)
    if najbolje_uloge:
        i = sum(najbolje_uloge)
        profit_1 = najbolje_uloge[0] * kvota_1 - i
        profit_2 = najbolje_uloge[1] * kvota_2 - i

        profit = max(profit_2, profit_1)
        return najbolje_uloge, round(profit, 2), round((profit / sum(najbolje_uloge)) * 100, 2)

    return 0, 0, 0

def arbitrazni_kalkulator(kvote, ulog, tolerancija=1000):
    kvota_1, kvota_2 = kvote

    najmanja_razlika = float('inf') 
    najbolje_uloge = None 

    for i in range(ulog - tolerancija, ulog, 100):
        ulog_1 = (i / kvota_1) / ((1 / kvota_1) + (1 / kvota_2))
        ulog_2 = i - ulog_1
        ulog_1 = round(ulog_1 / 100) * 100  
        ulog_2 = round(ulog_2 / 100) * 100  
        profit_1 = ulog_1 * kvota_1 - i
        profit_2 = ulog_2 * kvota_2 - i
        razlika = abs(profit_1 - profit_2)
        if razlika < najmanja_razlika:
            najmanja_razlika = razlika
            najbolje_uloge = (ulog_1, ulog_2)
            
    i = sum(najbolje_uloge)
    profit_1 = najbolje_uloge[0] * kvota_1 - i
    profit_2 = najbolje_uloge[1] * kvota_2 - i
    profit = (profit_1 + profit_2) / 2 
    return najbolje_uloge, round(profit, 2), round((profit/sum(najbolje_uloge))*100, 2)

async def process_command(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if text.startswith('/set'):
        params = text.split(' ')
        # Provera da li postoje dovoljni parametri
        if len(params) != 3:
            await update.message.reply_text("Jebem ti mater u pizdu nepismenu !!! ")
            return    
        try:
            with open("/content/drive/MyDrive/BOT/fudbal/set.txt", "w") as f:
                f.write(params[1] + '\n')
                f.write(params[2])
            mid = update.message.message_id  # U slučaju da vam ovo treba
            await update.message.reply_text("Parametri su uspešno sačuvani!")
        except Exception as e:
            await update.message.reply_text(f"Došlo je do greške: {e}")
        return None
    if text == '/stop':
      with open("/content/drive/MyDrive/BOT/stop.txt", "w") as f:
        f.write("Stop signal")
        mid = update.message.message_id
        #await delete_messages([mid])
        return None
  #######################################################################################################
    if text.startswith('//'):
          match = re.match(r"//(\d+)", text)  
          broj = int(match.group(1))  
          if update.message.reply_to_message:
            originalna_poruka = update.message.reply_to_message.text
            pattern = r"\[([0-9\.]+(?: [0-9\.]+)*)\]"  
            kvote_str_match = re.search(pattern, originalna_poruka)
            if kvote_str_match:
                kvote_str = kvote_str_match.group(1)
                kvote_lista = [float(kvota) for kvota in kvote_str.split()]
                broj_kvote_dict[broj] = kvote_lista
                ulog, profit, procenat = arbitrazni_kalkulator_spec(kvote_lista, broj)
                await update.message.reply_text(f"{kvote_lista} {ulog} {profit} {procenat}%")
                profit_1 = round(kvote_lista[0]*ulog[0], 2)
                profit_2 = round(kvote_lista[1]*ulog[1], 2)
                await update.message.reply_text(f"{profit_1}  {profit_2}")
                return None
##################################################################################################################
    match = re.match(r"/(\d+)", text)  
    if match:
        broj = int(match.group(1))  
        if update.message.reply_to_message:
            originalna_poruka = update.message.reply_to_message.text
            pattern = r"\[([0-9\.]+(?: [0-9\.]+)*)\]"  
            kvote_str_match = re.search(pattern, originalna_poruka)
            if kvote_str_match:
                kvote_str = kvote_str_match.group(1)
                kvote_lista = [float(kvota) for kvota in kvote_str.split()]
                broj_kvote_dict[broj] = kvote_lista
                if len(kvote_lista) == 3:
                    ulog, profit, procenat = arbitrazni_kalkulator_3(kvote_lista, broj)
                    await update.message.reply_text(f"{kvote_lista} {ulog} {profit} {procenat}%")
                    profit_1 = round(kvote_lista[0] * ulog[0], 2)
                    profit_2 = round(kvote_lista[1] * ulog[1], 2)
                    profit_3 = round(kvote_lista[2] * ulog[2], 2)
                    await update.message.reply_text(f"{profit_1}   {profit_2}   {profit_3}")

                ulog, profit, procenat = arbitrazni_kalkulator(kvote_lista, broj)
                await update.message.reply_text(f"{kvote_lista} {ulog} {profit} {procenat}%")
                profit_1 = round(kvote_lista[0]*ulog[0], 2)
                profit_2 = round( kvote_lista[1]*ulog[1], 2)
                await update.message.reply_text(f"{profit_1}   {profit_2}")

            else:
                message = await update.message.reply_text(f"Broj {broj} je sačuvan, ali kvote nisu pronađene u poruci!")
                message_id = message.message_id
                await delete_messages([message_id, update.message.message_id])  
        else:
            message = await update.message.reply_text(f"Broj {broj} je sačuvan, ali niste odgovorili na nijednu poruku!")
            message_id = message.message_id
            await delete_messages([message_id, update.message.message_id]) 
    else:
        message = await update.message.reply_text("Uneta komanda nije validna! Koristite format /<broj>.")
        message_id = message.message_id
        await asyncio.sleep(1)
        await delete_messages([message_id, update.message.message_id]) 

async def check_saved_data(update: Update, context: CallbackContext):
    broj = int(context.args[0]) if context.args else None
    if broj is not None and broj in broj_kvote_dict:
        kvote_lista = broj_kvote_dict[broj]
        await update.message.reply_text(f"Za broj {broj} sačuvane kvote su: {kvote_lista}")
    else:
        await update.message.reply_text(f"Podaci za broj {broj} nisu pronađeni!")
    return None

async def kvota_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        original_text = update.message.reply_to_message.text
        prvi_red = original_text.splitlines()[0].replace('(F)', '')  # Uzimamo prvi red
        tekst = re.sub(r'\s*\d+(\.\d+)?%', '', prvi_red)
        tekst = tekst.split('vs')

        await update.message.reply_text(f"Tekst poruke na koju si odgovorio:\n\n{tekst}")
    else:
        await update.message.reply_text("ODGOVORI NA PORUKU OCA TI JEBEM !!!")

CEKA_KVOTE, CEKA_ULOG = range(2)


async def arb_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Unesi kvote (razdvojene razmakom):")
    return CEKA_KVOTE

async def primi_kvote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kvote = [float(kvota) for kvota in update.message.text.strip().split()]
        if len(kvote) not in [2, 3]:
            raise ValueError("Dozvoljene su samo 2 ili 3 kvote.")
        context.user_data["kvote"] = kvote
        await update.message.reply_text("💰 Unesi ulog:")
        return CEKA_ULOG
    except Exception as e:
        await update.message.reply_text(f"⚠️ Greška: {e}")
        return CEKA_KVOTE
async def primi_ulog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ulog = int(update.message.text)
        kvote = context.user_data["kvote"]

        if len(kvote) == 2:
            ulozi, profit, procenat = arbitrazni_kalkulator(kvote, ulog)
        else:
            ulozi, profit, procenat = arbitrazni_kalkulator_3(kvote, ulog)

        odgovor = (
            f"📊 Kvote: {kvote}\n"
            f"🎯 Ulozi: {ulozi}\n"
            f"💵 Profit: {profit} RSD\n"
            f"📈 Procenat: {procenat}%"
        )
        await update.message.reply_text(odgovor)
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"⚠️ Neispravan ulog: {e}")
        return CEKA_ULOG
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Prekinuto.")
    return ConversationHandler.END

async def postavi_komande(application):
    komande = [
        BotCommand("izaberi", "Klandze"),
        BotCommand("arb", "kalkulator"),
        BotCommand("kvote", "Prikazuje kvote"),
        # Dodaj po potrebi
    ]
    await application.bot.set_my_commands(komande)

def main():
    from liste import TOKEN
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("check_data", check_saved_data))
    application.add_handler(CommandHandler("izaberi", kladionica_handler))  # dodaj i ovaj handler
    application.add_handler(CommandHandler("kvote", kvota_handler))  # dodaj i ovaj handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("arb", arb_start)],
        states={
            CEKA_KVOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, primi_kvote)],
            CEKA_ULOG: [MessageHandler(filters.TEXT & ~filters.COMMAND, primi_ulog)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)  
    application.add_handler(MessageHandler(filters.TEXT, process_command))
    application.add_handler(CallbackQueryHandler(button_handler))  # ⬅️ OVAJ deo fali
    asyncio.get_event_loop().run_until_complete(postavi_komande(application))
    application.run_polling()

if __name__ == "__main__":
    main()

