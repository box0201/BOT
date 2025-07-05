from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import re
import subprocess
from telegram import Bot
from liste_k import TOKEN, chat_id
import logging
import asyncio
import nest_asyncio
nest_asyncio.apply()

logging.basicConfig(level=logging.CRITICAL)
broj_kvote_dict = {}
bot = Bot(token=TOKEN) 


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

def main():
    from liste import TOKEN
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("check_data", check_saved_data))
    application.add_handler(MessageHandler(filters.TEXT, process_command))  
    application.run_polling()

if __name__ == "__main__":
    main()

