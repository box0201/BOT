import asyncio
from telegram import Bot
from liste import TOKEN, chat_id

bot = Bot(token=TOKEN)
async def typing(chat_id):
    try:
        while True:
            await bot.send_chat_action(chat_id=chat_id, action='typing')
            await asyncio.sleep(10) 
    except asyncio.CancelledError:
      pass
  

if __name__ == "__main__":
    asyncio.run(typing(chat_id))