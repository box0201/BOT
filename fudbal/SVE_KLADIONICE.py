import asyncio
from topbet import topbet
from maxbet import maxbet
from betole import betole
from merkurxtip import merkur
from oktagonbet import oktagon
from mozzart import mozzart
from soccer import soccer
from brazil import brazil
from balkanbet import balkan
from mystake import mystake
from volcano import volcano
from pinnbet import pinnbet
from superbet import superbet
from win365 import win365
import nest_asyncio
nest_asyncio.apply()

kladionica_funkcije = {
    "mozzart": mozzart,
    "maxbet": maxbet,
    "merkur": merkur,
    "soccer": soccer,
    "oktagon": oktagon,
    "balkan": balkan,
    "mystake": mystake,
    "superbet": superbet,
    "topbet": topbet,
    "pinnbet": pinnbet,
    "betole": betole,
    "volcano": volcano,
    "365.rs": win365  
}

async def main():
    with open('/content/drive/MyDrive/BOT/fudbal/kladionice.txt', 'r') as f:
        izabrane = [line.strip() for line in f]
    deo1 = [x for x in ['maxbet', 'topbet', 'merkur', 'volcano'] if x in izabrane]
    deo2 = [x for x in ['soccer', 'oktagon', 'balkan', 'superbet'] if x in izabrane]
    deo3 = [x for x in ['betole', 'pinnbet', 'mystake', '365.rs'] if x in izabrane]
    deo4 = [x for x in ['mozzart', ] if x in izabrane]
    
    svi_delovi = [deo1, deo2, deo3, deo4]
    for grupa in svi_delovi:
        if grupa:
            tasks = [kladionica_funkcije[naziv]() for naziv in grupa]
            await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())