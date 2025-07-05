
import pandas as pd
from rapidfuzz import fuzz
from concurrent.futures import ProcessPoolExecutor
import time
from itertools import combinations
from collections import defaultdict
from SVE_KLADIONICE import main 
import asyncio
import logging
import re
from multiprocessing import Manager
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import asyncio
import subprocess
from Telegram import send, delete_messages
from datetime import datetime, timedelta
from del_csv_k import func, delete
start = time.time()
import nest_asyncio
nest_asyncio.apply()

delete()
asyncio.run(main())
unapred = 240
uslov_procenat = 0
podudarnost = 75
delta = 0
file_names = func()


head = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', '1X', 'X2',
        'I W1', 'I W2', 'II W1', 'II W2',
        'I 1', 'I X', 'I 2', 'I 1X', 'I X2',
        'II 1', 'II X', 'II 2','II 1X', 'II X2',
        'W1', 'W2',
        '1/4 1', '1/4 X', '1/4 2','1/4 1X', '1/4 X2',
        '1/4 W1', '1/4 W2',
        '2/4 1', '2/4 X', '2/4 2', '2/4 1X', '2/4 X2',
        '3/4 1', '3/4 X', '3/4 2', '3/4 1X', '3/4 X2',
        '4/4 1', '4/4 X', '4/4 2', '4/4 1X', '4/4 X2',
        '2/4 W1', '2/4 W2', '3/4 W1', '3/4 W2', '4/4 W1', '4/4 W2',
         'P1', 'P2',]

yellow = "\033[93m"
blue = '\033[94m'
reset = "\033[0m"
GREEN = "\033[92m"
RESET = "\033[0m"
##################################################################################################
logging.basicConfig(level=logging.INFO, format='%(message)s')
def colored_log(message, color=RESET):
    logging.info(f"{color}{message}{RESET}")
    print((f"{color}{message}{RESET}"))
#################################################################################################
kladionice = []
for i in file_names:
    kladionice.append(pd.read_csv(i, usecols=head))
df = pd.concat(kladionice, ignore_index=True)

df['vreme'] = pd.to_datetime(df['vreme'])
df.sort_values(by='vreme', inplace=True)
df['vreme'] = df['vreme'] + timedelta(hours=1)
now = datetime.now()
time_threshold = now + timedelta(hours=unapred)
df = df[(df['vreme'] >= now) & (df['vreme'] <= time_threshold)]

def normalize_name(name: str) -> str:
    return name.strip().lower()

df['domaci_normalizovan'] = df['domaci'].apply(normalize_name)
df['gosti_normalizovan'] = df['gosti'].apply(normalize_name)

lista_datum = df['vreme'].dt.floor('min').unique()
tolerancija = pd.Timedelta(minutes=delta)

colored_log(f"Ukupan broj redova: {len(df)}", GREEN)
def process_date(datum_za_filtriranje):
    new_df = df[(df['vreme'].between(datum_za_filtriranje - tolerancija, datum_za_filtriranje + tolerancija))]
    results = []
    for row1, row2 in combinations(new_df.itertuples(index=False), 2):
        if row1.domaci_normalizovan == row2.domaci_normalizovan and row1.gosti_normalizovan == row2.gosti_normalizovan:
            results.append({"vreme": row1.vreme, "domaci": row1.domaci_normalizovan,
                            "gosti": row1.gosti_normalizovan, "ids": [row1.ID, row2.ID]})
        elif fuzz.ratio(f'{row1.domaci_normalizovan}-{row1.gosti_normalizovan}',
                        f'{row2.domaci_normalizovan}-{row2.gosti_normalizovan}') >= podudarnost:
            results.append({"vreme": row1.vreme, "domaci": row1.domaci_normalizovan,
                            "gosti": row1.gosti_normalizovan, "ids": [row1.ID, row2.ID]})

    return results
def process_date_1(datum_za_filtriranje, tolerancija, podudarnost):
    filtrirani_df = df[df['vreme'].between(datum_za_filtriranje - tolerancija, 
                                           datum_za_filtriranje + tolerancija)]
    redovi = filtrirani_df.to_dict(orient='records')
    
    results = []
    for row1, row2 in combinations(redovi, 2):
        if (row1['domaci_normalizovan'] == row2['domaci_normalizovan'] and
            row1['gosti_normalizovan'] == row2['gosti_normalizovan']):
            results.append({
                "vreme": row1['vreme'],
                "domaci": row1['domaci_normalizovan'],
                "gosti": row1['gosti_normalizovan'],
                "ids": [row1['ID'], row2['ID']]
            })
        elif fuzz.ratio(f"{row1['domaci_normalizovan']}-{row1['gosti_normalizovan']}",
                        f"{row2['domaci_normalizovan']}-{row2['gosti_normalizovan']}") >= podudarnost:
            results.append({
                "vreme": row1['vreme'],
                "domaci": row1['domaci_normalizovan'],
                "gosti": row1['gosti_normalizovan'],
                "ids": [row1['ID'], row2['ID']]
            })

    return results

#with ProcessPoolExecutor() as executor:
#    results = list(executor.map(process_date, lista_datum))


results = []
for i in lista_datum:
  results.append(process_date_1(i, tolerancija, podudarnost))
dfs = pd.DataFrame([item for sublist in results for item in sublist])

lista = [row['ids'] for _, row in dfs.iterrows()]
def spoji_iste_liste(liste):
    grupisane = defaultdict(set)
    for lista in liste:
        grupisane[lista[0]].update(lista)

    return [list(spojena) for spojena in grupisane.values()]

rezultat = spoji_iste_liste(lista)
colored_log(len(rezultat), GREEN)

j = 0
for i in rezultat:
    if len(i) > len(kladionice):
        print(i)

    j += 1
#print(j)

class DisjointSet:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])  # Path compression
        return self.parent[item]

    def union(self, set1, set2):
        root1 = self.find(set1)
        root2 = self.find(set2)

        if root1 != root2:
            # Union by rank
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1

    def add(self, item):
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0
def spojiti_liste(liste):
    ds = DisjointSet()
    for i, lst in enumerate(liste):
        for element in lst:
            ds.add(element)
            ds.union(lst[0], element)
    rezultati = {}
    for lst in liste:
        root = ds.find(lst[0])
        if root not in rezultati:
            rezultati[root] = []
        rezultati[root].extend(lst)
    return [list(set(group)) for group in rezultati.values()]

rezultat = spojiti_liste(rezultat)
print(len(rezultat))

nb_space = "\u00A0"

messages = []

def arbitraza(kvote, string, i):
    kolone = string.split('/')
    broj = len(i)
    obrnut_kvote = [1.0 / kvota for kvota in kvote]
    suma_inverzija = sum(obrnut_kvote)
    if suma_inverzija < 1:
        domaci = i['domaci'].iloc[0]
        gosti = i['gosti'].iloc[0]
        vreme = i['vreme'].iloc[0]
        id_list = []
        for j in kolone:
            for index, row in i.iterrows():
                if row[f'{j}'] == kvote[kolone.index(j)]:
                    id_list.append(re.sub(r'\d+', '', row['ID']))

        procenat_arbitraze = (1 / suma_inverzija - 1) * 100
        procenat = round(procenat_arbitraze, 2)
        if procenat < uslov_procenat:
            return None
        kvote_str = " ".join(f"{kvota:.2f}" for kvota in kvote)

        print(f"(K) {domaci} vs {gosti} {yellow}{procenat}{reset}% - {string}: [{GREEN}{kvote_str}{reset}] {blue}{id_list}{reset} {vreme} {broj}")

        message = f"""
        <b>(K) {domaci} vs {gosti}</b> {nb_space * 5}<i>{procenat}%</i> 
        
        {nb_space * 6}<b>{string}</b>
        
        {nb_space * 2}[<code>{kvote_str}</code>]
        
        {nb_space * 2}<b><i>{id_list}</i></b>{nb_space * 10}<i>{broj}</i> 
        
         {nb_space * 2}<i>{vreme}</i>
        """
        messages.append(message)
        selected_columns = ['ID', 'vreme', 'domaci', 'gosti'] + kolone

        #print(tabulate(i[selected_columns], headers='keys', tablefmt='grid'))

def func(i):
    filtrirani_redovi = df[df['ID'].isin(i)]
    dff = filtrirani_redovi.groupby(['vreme'], as_index=True).max()
    i = filtrirani_redovi
    #######################################################################################################
    arbitraza([dff.iloc[0]['1X'], dff.iloc[0]['2']], '1X/2', i)
    arbitraza([dff.iloc[0]['X2'], dff.iloc[0]['1']], 'X2/1', i)
    arbitraza([dff.iloc[0]['I 1X'], dff.iloc[0]['I 2']], 'I 1X/I 2', i)
    arbitraza([dff.iloc[0]['I X2'], dff.iloc[0]['I 1']], 'I X2/I 1', i)
    arbitraza([dff.iloc[0]['II 1X'], dff.iloc[0]['II 2']], 'II 1X/II 2', i)
    arbitraza([dff.iloc[0]['II X2'], dff.iloc[0]['II 1']], 'II X2/II 1', i)
    arbitraza([dff.iloc[0]['W1'], dff.iloc[0]['W2']], 'W1/W2', i)
    arbitraza([dff.iloc[0]['I W1'], dff.iloc[0]['I W2']], 'I W1/I W2', i)
    arbitraza([dff.iloc[0]['II W1'], dff.iloc[0]['II W2']], 'II W1/II W2', i)
    arbitraza([dff.iloc[0]['1/4 1X'], dff.iloc[0]['1/4 2']], '1/4 1X/1/4 2', i)
    arbitraza([dff.iloc[0]['1/4 X2'], dff.iloc[0]['1/4 1']], '1/4 X2/1/4 1', i)
    arbitraza([dff.iloc[0]['2/4 1X'], dff.iloc[0]['2/4 2']], '2/4 1X/2/4 2', i)
    arbitraza([dff.iloc[0]['2/4 X2'], dff.iloc[0]['2/4 1']], '2/4 X2/2/4 1', i)
    arbitraza([dff.iloc[0]['3/4 1X'], dff.iloc[0]['3/4 2']], '3/4 1X/3/4 2', i)
    arbitraza([dff.iloc[0]['3/4 X2'], dff.iloc[0]['3/4 1']], '3/4 X2/3/4 1', i)
    arbitraza([dff.iloc[0]['4/4 1X'], dff.iloc[0]['4/4 2']], '4/4 1X/4/4 2', i)
    arbitraza([dff.iloc[0]['4/4 X2'], dff.iloc[0]['4/4 1']], '4/4 X2/4/4 1', i)
    arbitraza([dff.iloc[0]['1/4 W1'], dff.iloc[0]['1/4 W2']], '1/4 W1/ 1/4 W2', i)
    arbitraza([dff.iloc[0]['2/4 W1'], dff.iloc[0]['2/4 W2']], '2/4 W1/ 2/4 W2', i)
    arbitraza([dff.iloc[0]['3/4 W1'], dff.iloc[0]['3/4 W2']], '3/4 W1/ 3/4 W2', i)
    arbitraza([dff.iloc[0]['4/4 W1'], dff.iloc[0]['4/4 W2']], '4/4 W1/ 4/4 W2', i)
    arbitraza([dff.iloc[0]['P1'], dff.iloc[0]['P2']], 'P1/P2', i)

#####################################################################################

#with Manager() as manager:
#    messages = manager.list()
#    with ProcessPoolExecutor() as executor:
#        rezultati = list(executor.map(func, rezultat))
#    messages = list(messages)
for i in rezultat:
  func(i)

asyncio.run(send(messages, False))
#asyncio.run(delete_messages([message_id]))
end = time.time()
print(f"\nUkupno vreme trajanja: {yellow}{end - start:.2f}{reset} sekundi\n")
