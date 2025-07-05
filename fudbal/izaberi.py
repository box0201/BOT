from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio, nest_asyncio
nest_asyncio.apply()

KLADIONICE = [
    "mozzart", "maxbet", "soccer", "oktagon", "betole", "balkan",
    "superbet", "topbet", "merkur", "volcano", "mystake", "pinnbet"
]

# Skladišti korisničke izbore
user_selections = {}

def build_keyboard(user_id):
    selected = user_selections.get(user_id, set())
    keyboard = []
    row = []
    for idx, name in enumerate(KLADIONICE, start=1):
        button_text = f"{'✅' if name in selected else '☑️'} {name}"
        row.append(InlineKeyboardButton(button_text, callback_data=name))
        if idx % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("💾 Sačuvaj", callback_data="sacuvaj")])
    return InlineKeyboardMarkup(keyboard)


async def kladionica_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_selections[user_id] = set()
    await update.message.reply_text(
        "Izaberi kladionice:",
        reply_markup=build_keyboard(user_id)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "sacuvaj":
        selected = user_selections.get(user_id, set())
        with open(f"kladionice.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(selected))
        await query.edit_message_text(f"Kladionice sačuvane:\n" + "\n".join(selected) if selected else "Niste izabrali nijednu kladionicu.")
        exit()
        return

    # Toggle izbor
    selected = user_selections.setdefault(user_id, set())
    if data in selected:
        selected.remove(data)
    else:
        selected.add(data)

    await query.edit_message_reply_markup(reply_markup=build_keyboard(user_id))

async def main():
    from liste import TOKEN
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("izaberi", kladionica_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

