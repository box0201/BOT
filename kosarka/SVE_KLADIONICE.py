import asyncio
from maxbet_k import maxbet
from betole_k import betole
from merkurxtip_k import merkur
from oktagonbet_k import oktagon
from mozzart_k import mozzart
from soccer_k import soccer
import nest_asyncio
nest_asyncio.apply()

async def main():
    await asyncio.gather(
      maxbet(), 
      mozzart(),
      betole(),
    )
    await asyncio.gather(
      soccer(),
      merkur(),
      oktagon(),

      )
    
if __name__ == "__main__":
    asyncio.run(main())
