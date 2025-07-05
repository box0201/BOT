import pandas as pd
from rapidfuzz import fuzz
from concurrent.futures import ProcessPoolExecutor
import time
from itertools import combinations
from collections import defaultdict
from SVE_KLADIONICE import main
import logging
import re
from multiprocessing import Manager
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import asyncio
import subprocess
from Telegram import send, delete_messages
from datetime import datetime, timedelta
from del_csv import func, delete
from del_sajt import delete as del_kvote
from tabulate import tabulate
import asyncio




start = time.time()
delete()
asyncio.run(main())
podudarnost = 80
delta = 5
file_names = func()

path = '/content/drive/MyDrive/BOT/fudbal/set.txt'
with open(path, "r") as f:
    lines = f.readlines()
    unapred = float(lines[0].strip())
    uslov_procenat = float(lines[1].strip())

head = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', 'GG', 'NG', 'GG3+', 'ne GG3+',
        'ug 0-1', 'ug 2+', 'ug 0-2', 'ug 3+', 'ug 0-3', 'ug 4+', 'ug 0-4', 'ug 5+', '1&3+', 'ne1&3+',
        '1-1', 'ne 1-1', 'W1', 'W2',
        'D I 0-1', 'D I 2+', 'G I 0-1', 'G I 2+', 'D II 0-1', 'D II 2+', 'G II 0-1', 'G II 2+',
        'I GG', 'I NG', 'II GG', 'II NG',
        '1X', '12', 'X2',
        'I 1', 'I X', 'I 2', 'I 1X', 'I 12', 'I X2', 'II 1', 'II X', 'II 2', 'II 1X', 'II 12', 'II X2',
        'I 0', 'I 0-1', 'I 0-2', 'I 1+', 'I 2+', 'I 3+', 'II 0', 'II 0-1', 'II 0-2', 'II 1+', 'II 2+', 'II 3+',
        '1X-1X', '1X-12', '1X-X2', '12-1X', '12-12', '12-X2', 'X2-1X', 'X2-12', 'X2-X2',
        '1-1X', '1-12', '1-X2', 'X-1X', 'X-12', 'X-X2', '2-1X', '2-12',
        '2-X2', '1X-1', '1X-X', '1X-2', '12-1', '12-X', '12-2', 'X2-1', 'X2-X', 'X2-2',
        ]

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

print(file_names)
#################################################################################################
num = len(file_names)
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


# with ProcessPoolExecutor() as executor:
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


# print(j)

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
event_broj = 0
    
def arbitraza(kvote, string, i):
    global event_broj
    kolone = string.split('|')
    broj = len(i)
    obrnut_kvote = []
    for kvota in kvote:
      if kvota == 0:
        return None
    for kvota in kvote:
      obrnut_kvote.append(1.0 / kvota)
    suma_inverzija = sum(obrnut_kvote)
    if suma_inverzija < 1:
        domaci = i['domaci'].iloc[0]
        gosti = i['gosti'].iloc[0]
        vreme = i['vreme'].iloc[0] + timedelta(hours=1)
        id_list = []
        for j in kolone:
            for index, row in i.iterrows():
                if row[f'{j}'] == kvote[kolone.index(j)]:
                    id_list.append(re.sub(r'\d+', '', row['ID']))

        procenat_arbitraze = (1 / suma_inverzija - 1) * 100
        procenat = round(procenat_arbitraze, 2)
        if procenat < uslov_procenat:
            return None

        selected_columns = ['ID', 'vreme', 'domaci', 'gosti'] + kolone
        df = i[selected_columns]
        global event_broj
        kvote_str = " ".join(f"{kvota:.2f}" for kvota in kvote)
        df.to_csv(f'/content/kvote-backend/csv/utakmica_{event_broj}_{procenat}.csv', index=False)
        event_broj += 1
        print(f"{domaci} vs {gosti} {yellow}{procenat}{reset}% - {string}: [{GREEN}{kvote_str}{reset}] {blue}{id_list}{reset} {vreme} {broj}")

        message = f"""

        <b>(F) {domaci} vs {gosti}</b> {nb_space * 5}<i>{procenat}%</i> 

        {nb_space * 6}<b>{string}</b>

        {nb_space * 2}[<code>{kvote_str}</code>]

        {nb_space * 2}<b><i>{id_list}</i></b>{nb_space * 10}<i>{broj, num}</i> 

         {nb_space * 2}<i>{vreme}</i>
        """
        messages.append(message)

del_kvote()

def func(i):
    filtrirani_redovi = df[df['ID'].isin(i)]
    dff = filtrirani_redovi.groupby(['vreme'], as_index=True).max()
    i = filtrirani_redovi
    #######################################################################################################
    arbitraza([dff.iloc[0]['GG'], dff.iloc[0]['NG']], 'GG|NG', i)
    arbitraza([dff.iloc[0]['GG3+'], dff.iloc[0]['ne GG3+']], 'GG3+|ne GG3+', i)
    arbitraza([dff.iloc[0]['ug 0-1'], dff.iloc[0]['ug 2+']], 'ug 0-1|ug 2+', i)
    arbitraza([dff.iloc[0]['ug 0-2'], dff.iloc[0]['ug 3+']], 'ug 0-2|ug 3+', i)
    arbitraza([dff.iloc[0]['ug 0-3'], dff.iloc[0]['ug 4+']], 'ug 0-3|ug 4+', i)
    arbitraza([dff.iloc[0]['ug 0-4'], dff.iloc[0]['ug 5+']], 'ug 0-4|ug 5+', i)
    arbitraza([dff.iloc[0]['1&3+'], dff.iloc[0]['ne1&3+']], '1&3+|ne1&3+', i)
    arbitraza([dff.iloc[0]['1-1'], dff.iloc[0]['ne 1-1']], '1-1|ne 1-1', i)
    arbitraza([dff.iloc[0]['D I 0-1'], dff.iloc[0]['D I 2+']], 'D I 0-1|D I 2+', i)
    arbitraza([dff.iloc[0]['G I 0-1'], dff.iloc[0]['G I 2+']], 'G I 0-1|G I 2+', i)
    arbitraza([dff.iloc[0]['D II 0-1'], dff.iloc[0]['D II 2+']], 'D II 0-1|D II 2+', i)
    arbitraza([dff.iloc[0]['G II 0-1'], dff.iloc[0]['G II 2+']], 'G II 0-1|G II 2+', i)
    arbitraza([dff.iloc[0]['I GG'], dff.iloc[0]['I NG']], 'I GG|I NG', i)
    arbitraza([dff.iloc[0]['II GG'], dff.iloc[0]['II NG']], 'II GG|II NG', i)
    arbitraza([dff.iloc[0]['1X'], dff.iloc[0]['2']], '1X|2', i)
    arbitraza([dff.iloc[0]['12'], dff.iloc[0]['X']], '12|X', i)
    arbitraza([dff.iloc[0]['1'], dff.iloc[0]['X2']], '1|X2', i)
    arbitraza([dff.iloc[0]['W1'], dff.iloc[0]['W2']], 'W1|W2', i)
    arbitraza([dff.iloc[0]['I 1'], dff.iloc[0]['I X2']], 'I 1|I X2', i)
    arbitraza([dff.iloc[0]['I 1X'], dff.iloc[0]['I 2']], 'I 1X|I 2', i)
    arbitraza([dff.iloc[0]['I 12'], dff.iloc[0]['I X']], 'I 12|I X', i)
    arbitraza([dff.iloc[0]['II 1'], dff.iloc[0]['II X2']], 'II 1|II X2', i)
    arbitraza([dff.iloc[0]['II 1X'], dff.iloc[0]['II 2']], 'II 1X|II 2', i)
    arbitraza([dff.iloc[0]['II 12'], dff.iloc[0]['II X']], 'II 12|II X', i)
    arbitraza([dff.iloc[0]['I 0'], dff.iloc[0]['I 1+']], 'I 0|I 1+', i)
    arbitraza([dff.iloc[0]['I 0-1'], dff.iloc[0]['I 2+']], 'I 0-1|I 2+', i)
    arbitraza([dff.iloc[0]['I 0-2'], dff.iloc[0]['I 3+']], 'I 0-2|I 3+', i)
    arbitraza([dff.iloc[0]['II 0'], dff.iloc[0]['II 1+']], 'II 0|II 1+', i)
    arbitraza([dff.iloc[0]['II 0-1'], dff.iloc[0]['II 2+']], 'II 0-1|II 2+', i)
    arbitraza([dff.iloc[0]['II 0-2'], dff.iloc[0]['II 3+']], 'II 0-2|II 3+', i)
    arbitraza([dff.iloc[0]['1'], dff.iloc[0]['X'], dff.iloc[0]['2']], '1|X|2', i)
    arbitraza([dff.iloc[0]['1'], dff.iloc[0]['1-X2'],dff.iloc[0]['X2-X2']], '1|1-X2|X2-X2', i)
    arbitraza([dff.iloc[0]['2'], dff.iloc[0]['2-1X'],dff.iloc[0]['1X-1X']], '2|2-1X|1X-1X', i)
    arbitraza([dff.iloc[0]['X'], dff.iloc[0]['X-12'],dff.iloc[0]['12-12']], 'X|X-12|12-12', i)


#############################################################################################

#####################################################################################

with Manager() as manager:
    messages = manager.list()
    with ProcessPoolExecutor() as executor:
        rezultati = list(executor.map(func, rezultat))
    messages = list(messages)

asyncio.run(send(messages, False))
#asyncio.run(delete_messages([message_id]))
end = time.time()
print(f"\nUkupno vreme trajanja: {yellow}{end - start:.2f}{reset} sekundi\n")
